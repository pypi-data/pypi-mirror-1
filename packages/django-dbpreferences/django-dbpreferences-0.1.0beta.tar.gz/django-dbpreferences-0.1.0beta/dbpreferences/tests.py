# coding: utf-8
"""
    Unittest for DBpreferences
    
    INFO: dbpreferences should be exist in python path!
"""

if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.INSTALLED_APPS += (
        'django.contrib.sites',
        'dbpreferences',
    )
    global_settings.DATABASE_ENGINE = "sqlite3"
    global_settings.DATABASE_NAME = ":memory:"
    global_settings.SITE_ID = 1

from django import forms
from django.test import TestCase

from dbpreferences.models import Preference
from dbpreferences.forms import DBPreferencesBaseForm


class FormWithoutMeta(DBPreferencesBaseForm):
    pass

class FormMetaWithoutAppLabel(DBPreferencesBaseForm):
    class Meta:
        pass

class UnittestForm(DBPreferencesBaseForm):
    """ preferences test form for the unittest """
    subject = forms.CharField(initial="foobar", help_text="Some foo text")   
    foo_bool = forms.BooleanField(initial=True, required=False, help_text="Yes or No?")
    count = forms.IntegerField(initial=10, min_value=1, help_text="A max number")
    font_size = forms.FloatField(initial=0.7, min_value=0.1, help_text="font size")

    class Meta:
        app_label = 'dbpreferences'



class TestDBPref(TestCase):   
    def test_form_without_meta(self):
        self.failUnlessRaises(AttributeError, FormWithoutMeta)
        
    def test_form_meta_without_app_label(self):
        self.failUnlessRaises(AttributeError, FormMetaWithoutAppLabel)
        
    def test(self):
        form = UnittestForm()
        # Frist time, the data would be inserted into the database
        self.failUnless(Preference.objects.count() == 0)
        pref_data = form.get_preferences()
        self.failUnless(Preference.objects.count() == 1)
        self.failUnless(isinstance(pref_data, dict),
            "It's not dict, it's: %s - %r" % (type(pref_data), pref_data))
        self.failUnlessEqual(pref_data,
            {'count': 10, 'foo_bool': True, 'font_size': 0.7, 'subject': 'foobar'})
        
        form = UnittestForm()
        self.failUnless(Preference.objects.count() == 1)
        pref_data = form.get_preferences()
        self.failUnless(Preference.objects.count() == 1)
        self.failUnless(isinstance(pref_data, dict),
            "It's not dict, it's: %s - %r" % (type(pref_data), pref_data))
        self.failUnlessEqual(pref_data,
            {'count': 10, 'foo_bool': True, 'font_size': 0.7, 'subject': 'foobar'})

if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', 'dbpreferences')