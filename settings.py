from os import environ
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SESSION_CONFIGS = [

    dict(
        name='tester_en',
        display_name="tester (English)",
        num_demo_participants=1,
        app_sequence=['tester'],
        language='en'
    ),
    dict(
        name='tester_ru',
        display_name="tester (Russian)",
        num_demo_participants=1,
        app_sequence=['tester'],
        language='ru'
    ),

    dict(
        name='endline',
        display_name="endline_test",
        num_demo_participants=1,
        app_sequence=['endline']
    ),
    dict(
        name='endline_ru',
        display_name="endline_test (Russian)",
        num_demo_participants=1,
        app_sequence=['endline'],
        language='ru'
    ),

    dict(
        name='full_ru',
        display_name="Full study (Russian)",
        num_demo_participants=1,
        app_sequence=['tester', 'endline', 'last'],
        language='ru'
    ),
    dict(
        name='full_en',
        display_name="Full study (English)",
        num_demo_participants=1,
        app_sequence=['tester', 'endline', 'last'],
        language='en',
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    toloka_participation_fee=1.50,
    doc="",
    use_browser_bots=False,
    toloka=True,
    toloka_sandbox=True
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = []

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """
TOLOKA_API = environ.get('TOLOKA_API')
SANDBOX_TOLOKA_API = environ.get('SANDBOX_TOLOKA_API')

SECRET_KEY = '&7hh8&8q=8ifh$)0&kzlh^)!tqas&4s4w6dofyup+!n4=i)7m)'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
EXTENSION_APPS = ['tolokaregister']
INSTALLED_APPS = [
    'otree',
    'webpack_loader',
    'django.contrib.admin',
    'django_user_agents',
]
# Cache backend is optional, but recommended to speed up user agent parsing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
MIDDLEWARE_CLASSES = (
    'django_user_agents.middleware.UserAgentMiddleware',
)
# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
USER_AGENTS_CACHE = 'default'

WEBPACK_LOADER = {
    'DEFAULT': {
        # 'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'vue/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'front', 'webpack-stats.json'),
        'POLL_INTERVAL': 0.3,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}
