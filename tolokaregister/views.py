from django.views.generic import ListView, RedirectView, View
from otree.models import Participant, Session
from .models import TolokaParticipant, UpdParticipant, UpdSession
from django.urls import reverse
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from datetime import datetime
from django.template import loader
import logging

logger = logging.getLogger(__name__)
class TolokaSessionList(ListView):
    model = UpdSession
    url_pattern = 'tolokadata/sessions'
    url_name = 'toloka_sessions'
    display_name = 'Sessions run in Toloka'
    template_name = 'tolokaregister/toloka_sessions_list.html'
    context_object_name = 'tolokasessions'

    def get_queryset(self):
        ss = self.model.objects.filter(is_demo=False)
        s = [o for o in ss if o.config.get('toloka')]
        return s


class TolokaTask(View):
    """
    For returning tsv file for Toloka pool
    """
    url_name = 'toloka_task'
    url_pattern = 'tolokadata/tsv/<str:session_code>'
    content_type = 'text/csv'

    def get(self, request, *args, **kwargs):
        session_code = self.kwargs.get('session_code')
        if session_code:
            try:
                s = Session.objects.get(code=session_code)
                anonymous_url = self.request.build_absolute_uri(
                    reverse('JoinSessionAnonymously', args=[s._anonymous_code])
                )
            except Session.DoesNotExist:
                logger.warning(f'Session {session_code} not found')
                return HttpResponseRedirect(reverse_lazy('ExportIndex'))
            response = HttpResponse(content_type=self.content_type)
            formatted_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            t = loader.get_template('tolokaregister/tasks.tsv')
            c = {'session_url': anonymous_url}
            filename = f'{session_code}_{formatted_date}.tsv'
            response['Content-Disposition'] = f'attachment; filename={filename}'
            response.write(t.render(c))
            return response
        else:
            logger.warning(f'No session code provided')
            return HttpResponseRedirect(reverse_lazy('ExportIndex'))


class TolokaSessionDetail(ListView):
    url_pattern = 'tolokasession/<code>'
    url_name = 'tolokasession'
    template_name = 'tolokaregister/toloka_session.html'
    context_object_name = 'participants'
    model = UpdParticipant

    def get_queryset(self):
        code = self.kwargs.get('code')
        session = Session.objects.get(code=code)
        participants = self.model.objects.filter(label__isnull=False, session=session)
        return participants

    def get_context_data(self, *args, **kwargs):
        r = super().get_context_data(*args, **kwargs)
        code = self.kwargs.get('code')
        session = Session.objects.get(code=code)
        r['session'] = session
        return r


class TolokaGeneralRedirect(RedirectView):
    url_pattern = None
    url_name = None

    def to_do(self):
        pass

    def get_redirect_url(self, *args, **kwargs):
        tp_id = kwargs.pop('toloka_participant', None)
        self.tp = TolokaParticipant.objects.get(id=tp_id)
        self.to_do()
        session = self.tp.owner.session
        ret_url = reverse('tolokasession', kwargs={'code': session.code})
        return ret_url


class GetInfo(RedirectView):
    url_pattern = 'tolokadata/assignment/<participant_pk>'
    url_name = 'get_toloka_info'

    def get_redirect_url(self, *args, **kwargs):
        # what we do here:
        # we get assignment
        # we check if the tolokaparticipant with this assignment exists
        # if it does we send a request to toloka asking for info update and update this tolokaparticipant
        # if tolokaparticipant does not exist we create it, and send the reuqest to toloka, and update the toloka participant

        participant_pk = kwargs.pop('participant_pk', None)
        p = Participant.objects.get(id=participant_pk)
        session = p.session
        """the following makes all default sessions to run in sandbox toloka. Not the realistic assumption taken
        into account how fucked up toloka sandbox is, but it is more safe."""
        sandbox = session.config.get('toloka_sandbox', True)
        self.tp, _ = TolokaParticipant.objects.get_or_create(owner=p,
                                                             defaults=dict(assignment=p.label, sandbox=sandbox))
        self.tp.get_info()
        session = self.tp.owner.session
        ret_url = reverse('tolokasession', kwargs={'code': session.code})
        return ret_url


class AcceptAnswer(TolokaGeneralRedirect):
    url_pattern = 'tolokadata/accept/<int:toloka_participant>'
    url_name = 'accept_toloka_answer'

    def to_do(self):
        self.tp.accept_assignment()


class PayBonus(TolokaGeneralRedirect):
    url_pattern = 'tolokadata/pay_bonus/<int:toloka_participant>'
    url_name = 'pay_toloka_bonus'

    def to_do(self):
        self.tp.pay_bonus(host=self.request.get_host())
