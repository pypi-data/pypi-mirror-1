import unittest
import doctest
import tempfile
import transaction

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)

class DoctestCase(unittest.TestCase):
    def __new__(self, test):
        return getattr(self, test)()

    @classmethod
    def test_readme(cls):
        database_path = tempfile.NamedTemporaryFile().name

        globs = dict(
            database_path=database_path,
            transaction=transaction,
            )

        return doctest.DocFileSuite(
            'README.txt',
            optionflags=OPTIONFLAGS,
            globs=globs,
            setUp=cls.setUp,
            tearDown=cls.tearDown,
            package="dobbin")

    @staticmethod
    def setUp(test):
        transaction.abort()

    @staticmethod
    def tearDown(test):
        tx = transaction.get()
        transaction.manager.free(tx)
