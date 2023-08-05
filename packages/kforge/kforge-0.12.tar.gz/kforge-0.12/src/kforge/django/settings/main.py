# Django settings for KForge project.

import kforge.soleInstance

application = kforge.soleInstance.application

DEBUG = True

ADMINS = (
    # ('Admin', 'user@domain.name'),
)

MANAGERS = ADMINS

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'f*(d3d45zetsb3)$&2h5@%lua()yc+kfn4w^dmrf_j1i(6jjkq'

ROOT_URLCONF = 'kforge.django.settings.urls.main'

TEMPLATE_DIRS = (
    application.dictionary['django.templates_dir'],
)

INSTALLED_APPS = (
#    'kforge.django.apps.kui',
)
