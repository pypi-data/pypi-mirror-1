# Django settings for KForge project.
import os

from django.dispatch import dispatcher
from django.core import signals

from kforge.soleInstance import application
from dm.django.settings.main import *

ROOT_URLCONF = 'kforge.django.settings.urls.main'

class UmaskWrapper:
    def __init__(self, umask):
        self._requestUmask = umask
        self._oldUmask = None

    def beginRequest(self):
        self._oldUmask = os.umask(self._requestUmask)

    def endRequest(self):
        os.umask(self._oldUmask)
        self._oldUmask = None

wrapper = UmaskWrapper(2)
dispatcher.connect(wrapper.beginRequest, signal=signals.request_started)
dispatcher.connect(wrapper.endRequest, signal=signals.request_finished)

