import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'scanbooker.django.settings.main'

from scanbooker.application import Application

application = Application()

