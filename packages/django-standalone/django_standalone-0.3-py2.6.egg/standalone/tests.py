# -*- coding: utf8 -*-

from django.test import TestCase

"""
Testcases for django-standalone. Run with the provided test.py script.
"""

class DjangoStandaloneTests(TestCase):

    def test_environment(self):
        """
        Just make sure that all is set up correctly.
        """
        self.assert_(True)

    def test_create_objects(self):
        """
        Create a few objects in the database and check
        that they are actually where they belong.
        """
        from models import MyModel
        o1 = MyModel(col1='foo', col2=1, col3=True)
        o1.save()
        o2 = MyModel(col1='bar', col2=2, col3=False)
        o2.save()
        self.assertEquals(MyModel.objects.get(col2=1).col1, 'foo')
        self.assertEquals(MyModel.objects.get(col2=2).col1, 'bar')

