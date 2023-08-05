import unittest

from elementtree.ElementTree import XML

class FieldHandlerTests(unittest.TestCase):

    def test_TextHandler(self):
        from zope.schema import Text
        from userschema.etree import TextHandler
        node = XML('''<Text name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>Default</default>
                      </Text>''')
        field = TextHandler(node)
        self.failUnless(isinstance(field, Text))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 'Default')

    def test_TextLineHandler(self):
        from zope.schema import TextLine
        from userschema.etree import TextLineHandler
        node = XML('''<TextLine name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>Default</default>
                        <min_length>5</min_length>
                        <max_length>10</max_length>
                      </TextLine>''')
        field = TextLineHandler(node)
        self.failUnless(isinstance(field, TextLine))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 'Default')
        self.assertEqual(field.min_length, 5)
        self.assertEqual(field.max_length, 10)

    def test_PasswordHandler(self):
        from zope.schema import Password
        from userschema.etree import PasswordHandler
        node = XML('''<Password name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>Default</default>
                        <min_length>5</min_length>
                        <max_length>10</max_length>
                      </Password>''')
        field = PasswordHandler(node)
        self.failUnless(isinstance(field, Password))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 'Default')
        self.assertEqual(field.min_length, 5)
        self.assertEqual(field.max_length, 10)

    def test_IntHandler(self):
        from zope.schema import Int
        from userschema.etree import IntHandler
        node = XML('''<Int name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>6</default>
                        <min>5</min>
                        <max>10</max>
                      </Int>''')
        field = IntHandler(node)
        self.failUnless(isinstance(field, Int))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 6)
        self.assertEqual(field.min, 5)
        self.assertEqual(field.max, 10)

    def test_BoolHandler(self):
        from zope.schema import Bool
        from userschema.etree import BoolHandler
        node = XML('''<Bool name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>True</default>
                      </Bool>''')
        field = BoolHandler(node)
        self.failUnless(isinstance(field, Bool))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, True)

    def test_SourceTextHandler(self):
        from zope.schema import SourceText
        from userschema.etree import SourceTextHandler
        node = XML('''<SourceText name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>Source text</default>
                      </SourceText>''')
        field = SourceTextHandler(node)
        self.failUnless(isinstance(field, SourceText))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 'Source text')

    def test_BytesHandler(self):
        from zope.schema import Bytes
        from userschema.etree import BytesHandler
        node = XML('''<Bytes name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>Default</default>
                      </Bytes>''')
        field = BytesHandler(node)
        self.failUnless(isinstance(field, Bytes))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 'Default')

    def test_ASCIIHandler(self):
        from zope.schema import ASCII
        from userschema.etree import ASCIIHandler
        node = XML('''<ASCII name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>Default</default>
                      </ASCII>''')
        field = ASCIIHandler(node)
        self.failUnless(isinstance(field, ASCII))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 'Default')

    def test_BytesLineHandler(self):
        from zope.schema import BytesLine
        from userschema.etree import BytesLineHandler
        node = XML('''<BytesLine name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>Default</default>
                        <min_length>5</min_length>
                        <max_length>10</max_length>
                      </BytesLine>''')
        field = BytesLineHandler(node)
        self.failUnless(isinstance(field, BytesLine))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 'Default')
        self.assertEqual(field.min_length, 5)
        self.assertEqual(field.max_length, 10)

    def test_ASCIILineHandler(self):
        from zope.schema import ASCIILine
        from userschema.etree import ASCIILineHandler
        node = XML('''<ASCIILine name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>Default</default>
                        <min_length>5</min_length>
                        <max_length>10</max_length>
                      </ASCIILine>''')
        field = ASCIILineHandler(node)
        self.failUnless(isinstance(field, ASCIILine))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 'Default')
        self.assertEqual(field.min_length, 5)
        self.assertEqual(field.max_length, 10)

    def test_FloatHandler(self):
        from zope.schema import Float
        from userschema.etree import FloatHandler
        node = XML('''<Float name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>3.141926</default>
                        <min>1.414</min>
                        <max>7.1828</max>
                      </Float>''')
        field = FloatHandler(node)
        self.failUnless(isinstance(field, Float))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, 3.141926)
        self.assertEqual(field.min, 1.414)
        self.assertEqual(field.max, 7.1828)

    def test_DatetimeHandler(self):
        from zope.app.datetimeutils import parseDatetimetz
        from zope.schema import Datetime
        from userschema.etree import DatetimeHandler
        DEFAULT = '2007-01-29T09:34:27Z'
        MIN = '2007-01-01T00:00:00Z'
        MAX = '2007-12-31T23:59:59Z'
        node = XML('''<Datetime name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>%s</default>
                        <min>%s</min>
                        <max>%s</max>
                      </Datetime>''' % (DEFAULT, MIN, MAX))
        field = DatetimeHandler(node)
        self.failUnless(isinstance(field, Datetime))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, parseDatetimetz(DEFAULT))
        self.assertEqual(field.min, parseDatetimetz(MIN))
        self.assertEqual(field.max, parseDatetimetz(MAX))

    def test_DateHandler(self):
        from datetime import date
        from zope.app.datetimeutils import parseDatetimetz
        from zope.schema import Date
        from userschema.etree import DateHandler
        DEFAULT = '2007-01-29'
        MIN = '2007-01-01'
        MAX = '2007-12-31'
        node = XML('''<Date name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>%s</default>
                        <min>%s</min>
                        <max>%s</max>
                      </Date>''' % (DEFAULT, MIN, MAX))
        field = DateHandler(node)
        self.failUnless(isinstance(field, Date))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, parseDatetimetz(DEFAULT).date())
        self.assertEqual(field.min, parseDatetimetz(MIN).date())
        self.assertEqual(field.max, parseDatetimetz(MAX).date())

    def test_TimedeltaHandler(self):
        from datetime import timedelta
        from zope.schema import Timedelta
        from userschema.etree import TimedeltaHandler
        DEFAULT = timedelta(2, 3, 4)
        MIN = timedelta(1, 2, 3)
        MAX = timedelta(7, 8, 9)
        node = XML('''<Timedelta name="test">
                        <title>Title</title>
                        <description>Description</description>
                        <required>True</required>
                        <readonly>False</readonly>
                        <default>2:3:4</default>
                        <min>1:2:3</min>
                        <max>7:8:9</max>
                      </Timedelta>''')
        field = TimedeltaHandler(node)
        self.failUnless(isinstance(field, Timedelta))
        self.assertEqual(field.__name__, 'test')
        self.assertEqual(field.title, 'Title')
        self.assertEqual(field.description, 'Description')
        self.assertEqual(field.required, True)
        self.assertEqual(field.readonly, False)
        self.assertEqual(field.default, DEFAULT)
        self.assertEqual(field.min, MIN)
        self.assertEqual(field.max, MAX)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FieldHandlerTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
