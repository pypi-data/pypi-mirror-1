from dm.ioc import RequiredFeature
from dm import dictionarywords

dictionary = RequiredFeature('SystemDictionary')

#
## Settings commonly defined in the system dictionary.
DEBUG = dictionary[dictionarywords.SYSTEM_MODE] != 'production',
TEMPLATE_DIRS = (dictionary[dictionarywords.DJANGO_TEMPLATES_DIR],)
TIME_ZONE = dictionary[dictionarywords.TIMEZONE]
SECRET_KEY = dictionary[dictionarywords.DJANGO_SECRET_KEY]

#
## Settings needing to be defined by a settings.main module.

ROOT_URLCONF = ''


#
## Settings that are apparently extra to requirements!

LANGUAGE_CODE = 'en-us'
SITE_ID = 1
ADMINS = ()
MANAGERS = ADMINS
MEDIA_ROOT = ''
MEDIA_URL = ''

