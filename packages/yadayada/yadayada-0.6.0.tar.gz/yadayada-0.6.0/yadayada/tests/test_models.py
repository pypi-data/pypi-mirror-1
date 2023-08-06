import unittest
from yadayada.models import StdModel, StdSharedModel
from yadayada.managers import StdManager
from django.db import models


class SubStdModel(StdModel):
    foo = models.CharField("foo", max_length=100)


class SubStdSharedModel(StdSharedModel):
    foo = models.CharField("foo", max_length=100)


class StdModelTest(unittest.TestCase):

    def setUp(self):
        self.stdmodel = SubStdModel(foo="baz")
        self.stdsharedmodel = SubStdSharedModel(foo="xuzzy")

    def testHasManager(self):
        self.assertTrue(isinstance(SubStdModel.manager, StdManager))
        self.assertTrue(isinstance(
            SubStdSharedModel.manager, StdManager))

    def testHasCustomField(self):
        self.assertEquals(self.stdmodel.foo, "baz")
        self.assertEquals(self.stdsharedmodel.foo, "xuzzy")

    def testIsInitiallyActive(self):
        self.assertTrue(self.stdmodel.is_active)
