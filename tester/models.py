from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
from django.conf import settings
from django.db import models as djmodels
import itertools
import logging
import yaml
from otree.models import Participant
import random
from django.db.models import Q, Max, FloatField, Sum, F, ExpressionWrapper
from django.utils.translation import gettext_lazy as _
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
author = 'Chapkovski, De Filippis, Henig-Schmidt'

doc = """
App testing for the most controversial questions for the conformity project
"""


class Constants(BaseConstants):
    name_in_url = 'tester'
    players_per_group = None
    distributions = [[0, 33, 66, 100], [0, 50, 50, 100]]
    LIKERT = range(0, 11)
    bonus_amount_average = 50  # amount in cents to be bonus participants for guessing second-order beliefs correctly
    bonus_amount_distribution = 50  # amount in cents to bonus participants for guessing distributions correctly
    MAX_ATTENTION_FAILURES = 2
    with open(r'./data/qleads.yaml') as file:
        leads = yaml.load(file, Loader=yaml.FullLoader)
    fields = list(leads.keys())  # again, not the best one, but will work for now. TODO?
    sortable_fields = fields + ['first',
                                'relative_importance']  # we use this for creating custom sorting for each field
    num_rounds = len(fields) + 1  # we ask one extra question (about relative importance).
    with open(r'./data/q.yaml') as file:
        qs = yaml.load(file, Loader=yaml.FullLoader)

    bodies = [q.get('statement') for q in qs]
    distribution_explication = _("""Using the sliders please estimate the share of  participants in this study who have
            answered from 0 to 3, from 4 to 6, from 7 to 10 about the
            statement above. <b>Please Note: You must move BOTH the sliders in order 
            to progress to the next page</b>""")

    distribution_obj = dict(
        categories=[_("from 0 to 3"), _("from 4 to 6"), _("From 7 to 10")],
        yLab=(_('Share (in %)')),
        plotTitle=_("Distribution of answers", ),
        popup=_('of participants answered between'),
        next=_('Next'),
        attention_checker_text=_('Attention: set middle slider (the blue one) to 100%'),

    )
    rank_obj = dict(
        title=_('Sort items based on the relative importance for you'),
        originalListTitle=_('Move from here'),
        rankedListTitle=_('...to here'),
        next=_('Next')
    )
    attention_error = dict(title=_('Attention'),
                           body=_(
                               'You commit some errors. Please pay more attention. Next time you fail to pass the attention test, we may finish the study'),
                           button=_('Ok'))


class Subsession(BaseSubsession):
    def get_current_language(self):

        return self.session.config.get('language', settings.LANGUAGE_CODE)

    def creating_session(self):
        for p in self.get_players():
            p.initial_distribution = p.id_in_group % 2
        if self.round_number == 1:
            l = self.get_current_language()
            ps = self.session.get_participants()
            sqs = [SensitiveQ(owner=p,
                              body=t[l].get('statement'),
                              label=t[l].get('for_ranking'),
                              order_r=random.random(),
                              attention_checker=t[l].get('for_ranking') == 'attention'
                              )
                   for p, t in itertools.product(ps, Constants.qs)]
            SensitiveQ.objects.bulk_create(sqs)
            sorters = []

            for s in SensitiveQ.objects.filter(owner__session=self.session):
                for f in Constants.sortable_fields:
                    sorters.append(Sorter(s=s, f=f, r=random.random()))
            Sorter.objects.bulk_create((sorters))


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    useragent_is_mobile = models.BooleanField()
    useragent_is_bot = models.BooleanField()
    useragent_browser_family = models.StringField()
    useragent_os_family = models.StringField()
    useragent_device_family = models.StringField()
    initial_distribution = models.IntegerField()
    attention_failure_counter = models.IntegerField(default=0)

    @property
    def total_attempts_failed(self):
        return self.participant.tester_player.aggregate(s=Sum('attention_failure_counter')).get('s', 0)

    def get_progress(self):
        totpages = self.participant._max_page_index
        curpage = self.participant._index_in_pages
        totsorters = Sorter.objects.filter(s__owner=self.participant).exclude(
            f='relative_importance')
        submitted_qs = totsorters.filter(submitted=True).count()

        return f"{(curpage + submitted_qs) / (totpages + totsorters.count()) * 100:.2f}"

    def get_ranking_titles(self):
        sqs = self.participant.sqs.annotate(
            s=Max('sorters__r', filter=Q(sorters__f='relative_importance'), output_field=FloatField()),
        ).order_by('s').values_list('label', flat=True)

        return [{'label': q} for q in sqs if q != 'attention']

    def get_distribution(self):
        return Constants.distributions[self.initial_distribution]

    def _next_q_for_dist(self):
        unanswered = self.participant.sqs.filter(first__isnull=True).annotate(
            s=Max('sorters__r', filter=Q(sorters__f='first'), output_field=FloatField()),
        ).order_by('s')

        if unanswered.exists():
            q = unanswered.first()
            q.mark_sorters_received('first')
            return dict(body=q.body, id=q.id, progress_value=self.get_progress(), label=q.label)
        else:
            return dict(no_q_left=True)

    def get_next_q_for_distribution(self, data):
        logger.info('message received from distribution')
        logger.info(data)
        qid = data.get('qid')
        distribution = data.get('distribution')
        if data.get('slider_movement_counter') and qid:
            q = SensitiveQ.objects.get(id=qid)
            q.slider_movement_counter += 1
            q.save()
            return
        if data.get('info_request'):
            r = {self.id_in_group: self._next_q_for_dist()}
            return r

        if qid and distribution:
            attention_failed = False
            q = SensitiveQ.objects.get(id=qid)
            for k, v in distribution.items():
                setattr(q, k, v)
            q.save()
            q.mark_sorters_done('first')
            if q.attention_checker and q.second != 100:
                attention_failed = True
                self.attention_failure_counter += 1
                self.save()
                if self.total_attempts_failed >= Constants.MAX_ATTENTION_FAILURES:
                    return {self.id_in_group: dict(too_many_failures=True)}
            return {self.id_in_group: {**self._next_q_for_dist(),
                                       'attention_failed': attention_failed}}  # we update the req

    def get_next_q(self, data):
        logger.info(data)
        qid = data.get('qid')
        field = data.get('field')
        body = data.get('body')
        value = data.get('value')
        next_q = self.next_q()
        r = {self.id_in_group: next_q}
        if data.get('info_request'):
            return r
        attention_failed = False
        if data.get('answer') and qid and field and value is not None:
            q = SensitiveQ.objects.get(id=qid)
            setattr(q, field, value)
            if q.attention_checker and body:
                _range = Constants.leads[field][self.subsession.get_current_language()]['range']
                _range = [str(i).lower() for i in _range]
                p = re.compile(r'\"(.*?[^,])\"')
                result = p.search(body)
                try:
                    checking_val = result.group(1).lower()
                    checking_index = _range.index(checking_val)
                    if checking_index != value:
                        raise IndexError
                except IndexError:
                    self.attention_failure_counter += 1
                    self.save()
                    if self.total_attempts_failed >= Constants.MAX_ATTENTION_FAILURES:
                        return {self.id_in_group: dict(too_many_failures=True)}
                    attention_failed = True
            q.save()
            q.mark_sorters_done(field)
        r = {self.id_in_group: {**self.next_q(), 'attention_failed': attention_failed}}  # we update the req
        return r

    def next_q(self):
        """
        We figure out the next unanswered question and return it
        we do it the following way:
        we first check if there are unanswered individual questions, if there are any we return the first one
        check if there are unanswered average questions
        then we return if there are unsanswered questions about distribution
        and then we return the questions about friendship

        """
        field = Constants.fields[self.round_number - 1]

        d = {f'{field}__isnull': True}
        unanswered = self.participant.sqs.filter(**d)
        if field in Constants.sortable_fields:
            unanswered = unanswered.annotate(s=Max('sorters__r', filter=Q(sorters__f=field), output_field=FloatField()),
                                             ).order_by('s')

        if unanswered.exists():
            q = unanswered.first()
            q.mark_sorters_received(field)
            body = q.body
            r = dict(body=body, field=field, id=q.id, progress_value=self.get_progress(), label=q.label, )
            if q.label == 'attention':
                _range = Constants.leads[field][self.subsession.get_current_language()]['range']
                r['body'] = q.body.format(num=str(random.choice(_range)).capitalize())
            return r
        else:
            return dict(no_q_left=True)


class SensitiveQ(djmodels.Model):
    def mark_sorters_received(self, field_name):
        now = datetime.now(tz=timezone.utc)
        self.sorters.filter(f=field_name, get_time__isnull=True).update(get_time=now)

    def mark_sorters_done(self, field_name):
        now = datetime.now(tz=timezone.utc)

        self.sorters.filter(f=field_name).update(submitted=True, post_time=now)
        self.sorters.filter(f=field_name).update(duration=F('post_time') - F('get_time'))

    attention_checker = models.BooleanField(default=False)
    owner = djmodels.ForeignKey(to=Participant, on_delete=djmodels.CASCADE, related_name="sqs")
    body = models.StringField()
    label = models.StringField()
    attitude = models.IntegerField(choices=Constants.LIKERT, widget=widgets.RadioSelectHorizontal)
    average_attitude = models.IntegerField(choices=Constants.LIKERT, widget=widgets.RadioSelectHorizontal)
    slider_movement_counter = models.IntegerField(default=0)
    order_r = models.FloatField()
    """
    The block of the following questions is to elicit info about distribution shape.
    We may think about something more complex later on. 
    """
    first = models.IntegerField(min=0, max=100)
    second = models.IntegerField(min=0, max=100)
    third = models.IntegerField(min=0, max=100)
    """Friendship answer. Do we want them to be likert as well?"""
    friend = models.IntegerField(choices=Constants.LIKERT)
    # Block of importance questions
    absolute_importance = models.IntegerField(choices=Constants.LIKERT)
    relative_importance = models.IntegerField()

    def __str__(self):
        return f'Q: "{self.body}" for participant {self.owner.code}'


class Sorter(djmodels.Model):
    get_time = djmodels.DateTimeField(null=True)
    post_time = djmodels.DateTimeField(null=True)
    duration = djmodels.DurationField(null=True)
    s = djmodels.ForeignKey(to=SensitiveQ, on_delete=djmodels.CASCADE, related_name='sorters')
    r = models.FloatField()
    f = models.StringField()
    submitted = models.BooleanField(default=False)

    def __str__(self):
        return f'sorter for {self.s.body}: field {self.f}, r: {self.r}'


def custom_export(players):
    yield ['code', 'body', 'label', 'attitude', 'average_attitude', 'first', 'second', 'third', 'friendship',
           'absolute_importance', 'relative_importance', 'slider_movement_counter',
           "sorter_attitude",
           "sorter_average_attitude",
           "sorter_first",
           "sorter_friendship",
           "sorter_absolute_importance",
           "sorter_relative_importance",
           "time_attitude",
           "time_average_attitude",
           "time_first",
           "time_friendship",
           "time_absolute_importance",
           "useragent_is_mobile",
           "useragent_is_bot",
           "useragent_browser_family",
           "useragent_os_family",
           "useragent_device_family",
           ]
    annotation = {}
    for f in Constants.sortable_fields:
        annotation[f'sorter_{f}'] = Max('sorters__r', filter=Q(sorters__f=f), output_field=FloatField())
        annotation[f'time_{f}'] = ExpressionWrapper(Max('sorters__duration', filter=Q(sorters__f=f), ),
                                                    output_field=djmodels.DurationField())
    sortableq = SensitiveQ.objects.order_by('id').annotate(**annotation)
    for q in sortableq:
        participant = q.owner
        player = participant.tester_player.first()
        yield [participant.code, q.body, q.label, q.attitude, q.average_attitude, q.first, q.second, q.third, q.friend,
               q.absolute_importance, q.relative_importance, q.slider_movement_counter,
               q.sorter_attitude,
               q.sorter_average_attitude,
               q.sorter_first,
               q.sorter_friend,
               q.sorter_absolute_importance,
               q.sorter_relative_importance,
               q.time_attitude,
               q.time_average_attitude,
               q.time_first,
               q.time_friend,
               q.time_absolute_importance,
               player.useragent_is_mobile,
               player.useragent_is_bot,
               player.useragent_browser_family,
               player.useragent_os_family,
               player.useragent_device_family,

               ]
