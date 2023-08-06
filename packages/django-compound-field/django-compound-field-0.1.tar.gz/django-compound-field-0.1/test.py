#
# (c) 2010 Andreas Kostyrka
#
"""
Unittests for django-compound-field
"""

class DjangoCaseAgainstSQLiteMemory:
    def setUp(self):
        """basic setup of django so that we can run models against an inmemory sqlite database."""
        import os, sys, new
        self.module_state = sys.modules
        os.environ["DJANGO_SETTINGS_MODULE"] = "dummy_settings_for_cfield"
        settings = new.module("dummy_settings_for_cfield")
        settings.__file__ = "./test.py"
        sys.modules["dummy_settings_for_cfield"] = settings
        settings.DATABASE_ENGINE = 'sqlite3'
        settings.DATABASE_NAME = ":memory:"
        settings.INSTALLED_APPS=["compoundfield",
                                 ]
        import django.db

    def tearDown(self):
        import sys
        from django.db import connection, transaction

        sys.modules = self.module_state # sqlite might need cleanup too :(
        cursor = connection.cursor()
        for statement in self._destroy:
            cursor.execute(statement)
        transaction.commit_unless_managed()

    def finishModels(self, models):
        """creates the given models in the given order. no fancy support for references"""
        from django.core.management.color import no_style
        from django.db import connection, transaction

        tables = connection.introspection.table_names()
        seen_models = connection.introspection.installed_models(tables)

        cursor = connection.cursor()
        self._destroy = []
        for model in models:
            sql, references = connection.creation.sql_create_model(model, no_style(), seen_models)
            seen_models.add(model)
            for statement in sql:
                cursor.execute(statement)
            self._destroy.extend(connection.creation.sql_destroy_model(model, [], no_style()))
        transaction.commit_unless_managed()

class TestCompoundField(DjangoCaseAgainstSQLiteMemory):
    def setUp(self):
        DjangoCaseAgainstSQLiteMemory.setUp(self)
        from django.db import models
        from compoundfield.field import CompoundField
        class MyCompound(CompoundField):
            test1 = models.CharField(max_length=100)
            test2 = models.CharField(max_length=100)
        class MyModel(models.Model):
            test = models.CharField(max_length=100)
            c = MyCompound()
            class Meta:
                app_label = "compoundfield"
        self.MyModel = MyModel
        self.MyCompound = MyCompound
        self.finishModels([MyModel])

    def test_roundtrip(self):
        "test that values stored in a Compound field end up in the database"
        x = self.MyModel.objects.create(test="abc")
        x.c.test1 = "abc"
        x.c.test2 = "def"
        x.save()
        
        assert self.MyModel.objects.get(id=1).c.test1 == "abc"
        assert self.MyModel.objects.get(id=1).c.test2 == "def"

    def test_creating_with_compounds(self):
        "initialising compound values via keyword arguments"
        x = self.MyModel.objects.create(test="abc", c_test1="abc", c_test2="def")
        assert x.c.test1 == "abc"
        assert x.c.test2 == "def"
     
    # creating fields that have no database representation is ugly at best, ...
    #def test_creating_with_helper(self):
    #    x = self.MyModel.objects.create(test="abc", c=self.MyCompound.cls(test1="abc", test2="def"))

