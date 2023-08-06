#!/Users/gb/Work/PythonPlay/testing/bin/python
# -*- coding: utf8 -*-

from standalone.conf import settings
settings = settings(
    DATABASE_ENGINE='sqlite3',
    DATABASE_NAME=':memory:',
)

# build some test models we need for test cases
from standalone import models

class MyModel(models.StandaloneModel):

    col1 = models.CharField(max_length=1000)
    col2 = models.IntegerField()
    col3 = models.BooleanField()

    def __unicode__(self):
        return self.col1

# set up the test database
from django.core.management import call_command
call_command('syncdb')

# run the provided tests
call_command('test', 'standalone')

