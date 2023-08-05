"""perforce.tests.api - Test the Perforce API extension module."""

import os.path
import unittest
import perforce.api
from perforce.tests.server import PerforceServerMixin

class ErrorSeverityTests(unittest.TestCase):

    def testErrorSeverities(self):

        from perforce.api import ErrorSeverity

        self.failUnless(isinstance(ErrorSeverity.EMPTY, ErrorSeverity))
        self.failUnless(isinstance(ErrorSeverity.INFO, ErrorSeverity))
        self.failUnless(isinstance(ErrorSeverity.WARN, ErrorSeverity))
        self.failUnless(isinstance(ErrorSeverity.FAILED, ErrorSeverity))
        self.failUnless(isinstance(ErrorSeverity.FATAL, ErrorSeverity))

    def testStrConversion(self):

        from perforce.api import ErrorSeverity

        self.assertEqual(str(ErrorSeverity.EMPTY), "empty")
        self.assertEqual(str(ErrorSeverity.INFO), "info")
        self.assertEqual(str(ErrorSeverity.WARN), "warning")
        self.assertEqual(str(ErrorSeverity.FAILED), "error")
        self.assertEqual(str(ErrorSeverity.FATAL), "error")

class CharSetTests(unittest.TestCase):

    def testCharSets(self):
        from perforce.api import CharSet

        self.failUnless(isinstance(CharSet.NOCONV, CharSet))
        self.failUnless(isinstance(CharSet.UTF_8, CharSet))
        self.failUnless(isinstance(CharSet.UTF_16, CharSet))
        self.failUnless(isinstance(CharSet.ISO8859_1, CharSet))
        self.failUnless(isinstance(CharSet.ISO8859_15, CharSet))
        self.failUnless(isinstance(CharSet.SHIFTJIS, CharSet))
        self.failUnless(isinstance(CharSet.EUCJP, CharSet))
        self.failUnless(isinstance(CharSet.WIN_US_ANSI, CharSet))
        self.failUnless(isinstance(CharSet.WIN_US_OEM, CharSet))
        self.failUnless(isinstance(CharSet.MACOS_ROMAN, CharSet))
        if float(perforce.api.version) >= 2005.2:
            self.failUnless(isinstance(CharSet.ISO8859_5, CharSet))
            self.failUnless(isinstance(CharSet.KOI8_R, CharSet))
            self.failUnless(isinstance(CharSet.WIN_CP_1251, CharSet))
            self.failUnless(isinstance(CharSet.UTF_16_LE, CharSet))
            self.failUnless(isinstance(CharSet.UTF_16_BE, CharSet))
            self.failUnless(isinstance(CharSet.UTF_16_LE_BOM, CharSet))
            self.failUnless(isinstance(CharSet.UTF_16_BE_BOM, CharSet))
            self.failUnless(isinstance(CharSet.UTF_16_BOM, CharSet))
            self.failUnless(isinstance(CharSet.UTF_8_BOM, CharSet))

    def testStrConversion(self):
        from perforce.api import CharSet

        self.assertEqual(str(CharSet.NOCONV), "none")
        self.assertEqual(str(CharSet.UTF_8), "utf8")
        if float(perforce.api.version) < 2005.2:
            self.assertEqual(str(CharSet.UTF_16), "utf16")
        else:
            self.assertEqual(str(CharSet.UTF_16), "utf16-nobom")
        self.assertEqual(str(CharSet.ISO8859_1), "iso8859-1")
        self.assertEqual(str(CharSet.ISO8859_15), "iso8859-15")
        self.assertEqual(str(CharSet.SHIFTJIS), "shiftjis")
        self.assertEqual(str(CharSet.EUCJP), "eucjp")
        self.assertEqual(str(CharSet.WIN_US_ANSI), "winansi")
        self.assertEqual(str(CharSet.WIN_US_OEM), "winoem")
        self.assertEqual(str(CharSet.MACOS_ROMAN), "macosroman")
        if float(perforce.api.version) >= 2005.2:
            self.assertEqual(str(CharSet.ISO8859_5), "iso8859-5")
            self.assertEqual(str(CharSet.KOI8_R), "koi8-r")
            self.assertEqual(str(CharSet.WIN_CP_1251), "cp1251")
            self.assertEqual(str(CharSet.UTF_16_LE), "utf16le")
            self.assertEqual(str(CharSet.UTF_16_BE), "utf16be")
            self.assertEqual(str(CharSet.UTF_16_LE_BOM), "utf16le-bom")
            self.assertEqual(str(CharSet.UTF_16_BE_BOM), "utf16be-bom")
            self.assertEqual(str(CharSet.UTF_16_BOM), "utf16")
            self.assertEqual(str(CharSet.UTF_8_BOM), "utf8-bom")

    def testStrConstruction(self):
        from perforce.api import CharSet

        self.failUnless(CharSet(str(CharSet.NOCONV)) is CharSet.NOCONV)
        self.failUnless(CharSet(str(CharSet.UTF_8)) is CharSet.UTF_8)
        self.failUnless(CharSet(str(CharSet.ISO8859_1)) is CharSet.ISO8859_1)
        self.failUnless(CharSet(str(CharSet.ISO8859_15)) is CharSet.ISO8859_15)
        self.failUnless(CharSet(str(CharSet.SHIFTJIS)) is CharSet.SHIFTJIS)
        self.failUnless(CharSet(str(CharSet.EUCJP)) is CharSet.EUCJP)
        self.failUnless(CharSet(str(CharSet.WIN_US_ANSI)) is
                        CharSet.WIN_US_ANSI)
        self.failUnless(CharSet(str(CharSet.WIN_US_OEM)) is
                        CharSet.WIN_US_OEM)
        self.failUnless(CharSet(str(CharSet.MACOS_ROMAN)) is
                        CharSet.MACOS_ROMAN)
        self.failUnless(CharSet(str(CharSet.UTF_16)) is CharSet.UTF_16)
        if float(perforce.api.version) >= 2005.2:
            self.failUnless(CharSet(str(CharSet.ISO8859_5)) is
                            CharSet.ISO8859_5)
            self.failUnless(CharSet(str(CharSet.KOI8_R)) is
                            CharSet.KOI8_R)
            self.failUnless(CharSet(str(CharSet.WIN_CP_1251)) is
                            CharSet.WIN_CP_1251)
            self.failUnless(CharSet(str(CharSet.UTF_16_LE)) is
                            CharSet.UTF_16_LE)
            self.failUnless(CharSet(str(CharSet.UTF_16_BE)) is
                            CharSet.UTF_16_BE)
            self.failUnless(CharSet(str(CharSet.UTF_16_LE_BOM)) is
                            CharSet.UTF_16_LE_BOM)
            self.failUnless(CharSet(str(CharSet.UTF_16_BE_BOM)) is
                            CharSet.UTF_16_BE_BOM)
            self.failUnless(CharSet(str(CharSet.UTF_16_BOM)) is
                            CharSet.UTF_16_BOM)
            self.failUnless(CharSet(str(CharSet.UTF_8_BOM)) is
                            CharSet.UTF_8_BOM)

    def testCodecNames(self):

        from perforce.api import CharSet

        self.failUnless(CharSet.NOCONV.codec is None)
        self.assertEqual(CharSet.UTF_8.codec, "utf_8")
        self.assertEqual(CharSet.ISO8859_1.codec, "latin_1")
        self.assertEqual(CharSet.ISO8859_15.codec, "iso8859_15")
        self.assertEqual(CharSet.SHIFTJIS.codec, "shift_jis")
        self.assertEqual(CharSet.EUCJP.codec, "euc_jp")
        self.assertEqual(CharSet.WIN_US_ANSI.codec, "cp1252")
        self.assertEqual(CharSet.WIN_US_OEM.codec, "cp437")
        self.assertEqual(CharSet.MACOS_ROMAN.codec, "mac_roman")
        self.assertEqual(CharSet.UTF_16.codec, "utf_16")
        if float(perforce.api.version) >= 2005.2:
            self.assertEqual(CharSet.ISO8859_5.codec, "iso8859_5")
            self.assertEqual(CharSet.KOI8_R.codec, "koi8_r")
            self.assertEqual(CharSet.WIN_CP_1251.codec, "cp1251")
            self.assertEqual(CharSet.UTF_16_LE.codec, "utf_16_le")
            self.assertEqual(CharSet.UTF_16_BE.codec, "utf_16_be")
            self.assertEqual(CharSet.UTF_16_LE_BOM.codec, "utf_16_le")
            self.assertEqual(CharSet.UTF_16_BE_BOM.codec, "utf_16_be")
            self.assertEqual(CharSet.UTF_16_BOM.codec, "utf_16")

    def testCodecExistence(self):

        import codecs
        from perforce.api import CharSet

        # Make sure all codecs are actually supported by Python
        e, d, r, w = codecs.lookup(CharSet.UTF_8.codec)
        e, d, r, w = codecs.lookup(CharSet.ISO8859_1.codec)
        e, d, r, w = codecs.lookup(CharSet.ISO8859_15.codec)
        e, d, r, w = codecs.lookup(CharSet.SHIFTJIS.codec)
        e, d, r, w = codecs.lookup(CharSet.EUCJP.codec)
        e, d, r, w = codecs.lookup(CharSet.WIN_US_ANSI.codec)
        e, d, r, w = codecs.lookup(CharSet.WIN_US_OEM.codec)
        e, d, r, w = codecs.lookup(CharSet.MACOS_ROMAN.codec)
        e, d, r, w = codecs.lookup(CharSet.UTF_16.codec)
        if float(perforce.api.version) >= 2005.2:
            e, d, r, w = codecs.lookup(CharSet.ISO8859_5.codec)
            e, d, r, w = codecs.lookup(CharSet.KOI8_R.codec)
            e, d, r, w = codecs.lookup(CharSet.UTF_16_LE.codec)
            e, d, r, w = codecs.lookup(CharSet.UTF_16_BE.codec)
            e, d, r, w = codecs.lookup(CharSet.UTF_16_LE_BOM.codec)
            e, d, r, w = codecs.lookup(CharSet.UTF_16_BE_BOM.codec)
            e, d, r, w = codecs.lookup(CharSet.UTF_16_BOM.codec)

    def testEncodeDecode(self):

        from perforce.api import CharSet

        self.assertRaises(ValueError, CharSet.NOCONV.encode, u'test')
        self.assertRaises(ValueError, CharSet.NOCONV.decode, 'test')

        def checkDecodedEncodingIsSame(charset):
            original = u'test string'
            
            encoded = charset.encode(original)
            self.failUnless(isinstance(encoded, str))
                                       
            decoded = charset.decode(encoded)
            self.failUnless(isinstance(decoded, unicode))
            
            self.assertEqual(original, decoded)

        checkDecodedEncodingIsSame(CharSet.UTF_8)
        checkDecodedEncodingIsSame(CharSet.ISO8859_1)
        checkDecodedEncodingIsSame(CharSet.ISO8859_15)
        checkDecodedEncodingIsSame(CharSet.SHIFTJIS)
        checkDecodedEncodingIsSame(CharSet.EUCJP)
        checkDecodedEncodingIsSame(CharSet.WIN_US_ANSI)
        checkDecodedEncodingIsSame(CharSet.WIN_US_OEM)
        checkDecodedEncodingIsSame(CharSet.MACOS_ROMAN)
        checkDecodedEncodingIsSame(CharSet.UTF_16)
        if float(perforce.api.version) >= 2005.2:
            checkDecodedEncodingIsSame(CharSet.ISO8859_5)
            checkDecodedEncodingIsSame(CharSet.KOI8_R)
            checkDecodedEncodingIsSame(CharSet.UTF_16_LE)
            checkDecodedEncodingIsSame(CharSet.UTF_16_BE)
            checkDecodedEncodingIsSame(CharSet.UTF_16_LE_BOM)
            checkDecodedEncodingIsSame(CharSet.UTF_16_BE_BOM)
            checkDecodedEncodingIsSame(CharSet.UTF_16_BOM)

    def testEncodeFailure(self):

        from perforce.api import CharSet

        euro = u'\u20AC'

        # ISO8859-1 doesn't include the euro sign (U+20AC)
        self.assertRaises(ValueError, CharSet.ISO8859_1.encode, euro)

        # ISO8859-15 does include it, however
        encodedEuro = CharSet.ISO8859_15.encode(euro)
        self.assertEqual(encodedEuro, '\xA4')

class ErrorTests(unittest.TestCase):

    def testConstructionAndDestruction(self):

        e1 = perforce.api.Error()
        e2 = perforce.api.Error()

        self.failUnless(isinstance(e1, perforce.api.Error))
        self.failUnless(isinstance(e2, perforce.api.Error))

        self.failIf(e1.test())
        self.failIf(e1.isInfo())
        self.failIf(e1.isWarning())
        self.failIf(e1.isError())

        del e1
        del e2

    def testSetError(self):

        e = perforce.api.Error()
        e.set(perforce.api.ErrorSeverity.INFO, 'some message')
        self.failIf(e.test())
        self.failUnless(e.isInfo())
        self.failIf(e.isWarning())
        self.failIf(e.isError())
        self.assertEqual(str(e), 'some message')

        e.set(perforce.api.ErrorSeverity.FAILED, 'some error message')
        self.failUnless(e.test())
        self.failIf(e.isInfo())
        self.failIf(e.isWarning())
        self.failUnless(e.isError())
        self.assertEqual(str(e), 'some error message')

    def testFormat(self):

        e = perforce.api.Error()
        
        e.set(perforce.api.ErrorSeverity.INFO, u'some message')
        self.failUnless(isinstance(e.format(), unicode))
        self.assertEqual(e.format(), u'some message')

        e.set(perforce.api.ErrorSeverity.INFO, 'some message')
        self.failUnless(isinstance(e.format(), str))
        self.assertEqual(e.format(), 'some message')

    def testUnicodeErrors(self):

        e = perforce.api.Error()
        e.set(perforce.api.ErrorSeverity.INFO, u'some message \u2164')
        self.assertEqual(e.format(), u'some message \u2164')
        self.assertEqual(unicode(e), u'some message \u2164')

        # Will fail if the default codec is ASCII
        self.assertRaises(UnicodeEncodeError, str, e)

class EnviroTests(unittest.TestCase):
    """Tests for the perforce.api.Enviro class."""

    def testUpdate(self):

        e = perforce.api.Enviro()

        # Both raw strings
        e.update('P4PORT', 'perforce:1666')
        self.assertEqual(e.get('P4PORT'), 'perforce:1666')

        # Key as unicode string
        e.update(u'P4PORT', 'perforce:1667')
        self.assertEqual(e.get(u'P4PORT'), 'perforce:1667')

        # Value as unicode string
        e.update('P4PORT', u'perforce:1668')
        self.assertEqual(e.get('P4PORT'), u'perforce:1668')

        # Both unicode string
        e.update(u'P4PORT', u'perforce:1668')
        self.assertEqual(e.get(u'P4PORT'), u'perforce:1668')

    def testConstruction(self):

        # Construct the system registry
        e = perforce.api.Enviro(None)

        # Construct to a service registry
        e = perforce.api.Enviro('my-service')
        e = perforce.api.Enviro(u'my-service')

class SpecTests(unittest.TestCase):
    """Tests for the perforce.api.Spec class."""

    def testSingleFieldSpec(self):
        
        specdef = "Word;code:123;type:word;;"
        spec = perforce.api.Spec(specdef)

        self.assertEqual(len(spec), 1)
        self.failUnless('Word' in spec)

        elem = spec['Word']
        self.failUnless(isinstance(elem, perforce.api.SpecElem))
        self.assertEqual(elem.code, 123)
        self.assertEqual(elem.tag, 'Word')
        self.assertEqual(elem.preset, None)
        self.assertEqual(elem.numWords, 1)
        self.assertEqual(elem.values, None)
        self.assertEqual(elem.maxLength, 0)
        self.assertEqual(elem.isReadOnly(), False)
        self.assertEqual(elem.isRequired(), False)
        self.assertEqual(elem.isWords(), True)
        self.assertEqual(elem.isSingle(), True)
        self.assertEqual(elem.isText(), False)
        self.assertEqual(elem.isSelect(), False)
        self.assertEqual(elem.isList(), False)
        self.assertEqual(elem.isDate(), False)

    def testSpecIteration(self):

        specdef = "WordA;code:123;type:word;;WordB;code:234;type:word;;"
        spec = perforce.api.Spec(specdef)

        self.assertEqual(len(spec), 2)
        for name in spec:
            self.failUnless(name in ["WordA", "WordB"])

        self.assertEqual(spec['WordA'].code, 123)
        self.assertEqual(spec['WordB'].code, 234)

    def testParseForm(self):

        specdef = "Word;code:123;type:word;;"
        form = """# Some commentary
Word:\thello
"""
        spec = perforce.api.Spec(specdef)
        
        try:
            d = spec.parse(form)
            self.assertEqual(len(d), 1)
            self.assertEqual(d['Word'], 'hello')
        except perforce.api.ParseError, err:
            self.fail(err)

    def testFormatForm(self):

        specdef = "Word;code:123;type:word;;"
        spec = perforce.api.Spec(specdef)
        
        data = {'Word' : 'hello'}
        form = spec.format(data)
        
        self.assertEqual(form, "Word:\thello\n")

    def testFormatTextField(self):

        specdef = "Text;code:123;type:text;;"
        spec = perforce.api.Spec(specdef)

        data = {'Text' : "Some multi-line text\nfor testing.\n"}

        form = spec.format(data)

        self.assertEqual(form,
                         "Text:\n\tSome multi-line text\n\tfor testing.\n")

    def testFormatLineListField(self):

        specdef = "List;code:10;type:llist;;"
        spec = perforce.api.Spec(specdef)

        data = {'List' : ["Line 1",
                          "Line 2",
                          "Line 3"]}

        form = spec.format(data)

        self.assertEqual(form, "List:\n\tLine 1\n\tLine 2\n\tLine 3\n")

    def testFormatWordListField(self):

        specdef = "WList;code:10;type:wlist;words:3;;"
        spec = perforce.api.Spec(specdef)

        data = {'WList' : [('foo', 'bar', 'baz'),
                           ('flib', 'flob', 'flap')]}

        form = spec.format(data)

        self.assertEqual(form, "WList:\n\tfoo bar baz\n\tflib flob flap\n")

    def testUnicodeForm(self):

        specdef = u"WordA;code:123;type:word;;" + \
                  u"WordB;code:234;type:word;;" + \
                  u"LineC;code:345;type:line;;"
        spec = perforce.api.Spec(specdef)

        self.assertEqual(len(spec), 3)
        for name in spec:
            self.failUnless(isinstance(name, unicode))
            self.failUnless(name in [u"WordA", u"WordB", u"LineC"])

        self.assertEqual(spec[u'WordA'].code, 123)
        self.assertEqual(spec[u'WordB'].code, 234)
        self.assertEqual(spec[u'LineC'].code, 345)
        
        self.failUnless(isinstance(spec[u'WordA'].tag, unicode))
        self.failUnless(isinstance(spec[u'WordB'].tag, unicode))
        self.failUnless(isinstance(spec[u'LineC'].tag, unicode))

        data = {u'WordA' : u'ValueA',
                u'WordB' : u'ValueB',
                u'LineC' : u'This costs \u20AC0.02'
                }

        form = spec.format(data)

        self.failUnless(isinstance(form, unicode))

        data2 = spec.parse(form)

        for tag, value in data2.iteritems():
            self.failUnless(isinstance(tag, unicode))
            self.failUnless(isinstance(value, unicode))

        self.assertEqual(data2, data)

class FileSysTypeTests(unittest.TestCase):
    """Tests for the perforce.api.FileSysType class."""

    def testPredefinedValues(self):
        from perforce.api import FileSysType
        self.failUnless(isinstance(FileSysType.TEXT, FileSysType))
        self.failUnless(isinstance(FileSysType.BINARY, FileSysType))
        self.failUnless(isinstance(FileSysType.GZIP, FileSysType))
        self.failUnless(isinstance(FileSysType.DIRECTORY, FileSysType))
        self.failUnless(isinstance(FileSysType.SYMLINK, FileSysType))
        self.failUnless(isinstance(FileSysType.RESOURCE, FileSysType))
        self.failUnless(isinstance(FileSysType.SPECIAL, FileSysType))
        self.failUnless(isinstance(FileSysType.MISSING, FileSysType))
        self.failUnless(isinstance(FileSysType.CANTTELL, FileSysType))
        self.failUnless(isinstance(FileSysType.EMPTY, FileSysType))
        self.failUnless(isinstance(FileSysType.UNICODE, FileSysType))
        self.failUnless(isinstance(FileSysType.GUNZIP, FileSysType))
        self.failUnless(isinstance(FileSysType.MASK, FileSysType))
        self.failUnless(isinstance(FileSysType.M_APPEND, FileSysType))
        self.failUnless(isinstance(FileSysType.M_EXCL, FileSysType))
        self.failUnless(isinstance(FileSysType.M_SYNC, FileSysType))
        self.failUnless(isinstance(FileSysType.M_EXEC, FileSysType))
        self.failUnless(isinstance(FileSysType.M_APPLE, FileSysType))
        self.failUnless(isinstance(FileSysType.M_COMP, FileSysType))
        self.failUnless(isinstance(FileSysType.M_MASK, FileSysType))
        self.failUnless(isinstance(FileSysType.L_LOCAL, FileSysType))
        self.failUnless(isinstance(FileSysType.L_LF, FileSysType))
        self.failUnless(isinstance(FileSysType.L_CR, FileSysType))
        self.failUnless(isinstance(FileSysType.L_CRLF, FileSysType))
        self.failUnless(isinstance(FileSysType.L_LFCRLF, FileSysType))
        self.failUnless(isinstance(FileSysType.L_MASK, FileSysType))
        self.failUnless(isinstance(FileSysType.ATEXT, FileSysType))
        self.failUnless(isinstance(FileSysType.XTEXT, FileSysType))
        self.failUnless(isinstance(FileSysType.RTEXT, FileSysType))
        self.failUnless(isinstance(FileSysType.RXTEXT, FileSysType))
        self.failUnless(isinstance(FileSysType.CBINARY, FileSysType))
        self.failUnless(isinstance(FileSysType.XBINARY, FileSysType))
        self.failUnless(isinstance(FileSysType.APPLETEXT, FileSysType))
        self.failUnless(isinstance(FileSysType.APPLEFILE, FileSysType))
        self.failUnless(isinstance(FileSysType.XAPPLEFILE, FileSysType))
        self.failUnless(isinstance(FileSysType.XUNICODE, FileSysType))
        self.failUnless(isinstance(FileSysType.RCS, FileSysType))

    def testOperators(self):
        from perforce.api import FileSysType
        fst1 = FileSysType.UNICODE | FileSysType.M_EXEC | FileSysType.L_LF
        self.assertEqual(fst1 & FileSysType.MASK, FileSysType.UNICODE)
        self.assertEqual(fst1 & FileSysType.M_MASK, FileSysType.M_EXEC)
        self.assertEqual(fst1 & FileSysType.L_MASK, FileSysType.L_LF)
        self.failIf(fst1 & FileSysType.M_COMP)
        self.assertEqual(fst1 ^ FileSysType.M_EXEC,
                         FileSysType.UNICODE | FileSysType.L_LF)

class FileSysTests(unittest.TestCase):
    """Tests for the perforce.api.FileSys class."""

    def setUp(self):
        import tempfile
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        try:
            for root, dirs, files in os.walk(self.tempdir, topdown=False):
                for name in files:
                    p = os.path.join(root, name)
                    os.chmod(p, 0777)
                    os.remove(p)
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.tempdir)
        finally:
            del self.tempdir

    def testOpenFile(self):

        from perforce.api import FileSys, FileSysType, FileOpenMode, Error

        path = os.path.join(self.tempdir, 'foo.txt')

        f = FileSys(FileSysType.TEXT | FileSysType.L_LF)
        f.set(path)
        self.assertEqual(f.path(), path)

        e = Error()
        f.open(FileOpenMode.WRITE, e)
        self.failIf(e.test())

        e = Error()
        f.close(e)

    def testOpenFileUnicode(self):

        from perforce.api import FileSys, FileSysType, FileOpenMode, Error

        path = os.path.join(self.tempdir, u'foo.txt')

        f = FileSys(FileSysType.TEXT | FileSysType.L_LF)
        f.set(path)
        self.assertEqual(f.path(), path)
        self.failUnless(isinstance(f.path(), unicode))

        e = Error()
        f.open(FileOpenMode.WRITE, e)
        self.failIf(e.test())

        e = Error()
        f.close(e)

class ClientMergeEnumTests(unittest.TestCase):
    """Tests for the perforce.api.ClientMerge enumerations."""

    def testMergeType(self):

        from perforce.api import MergeType

        self.failUnless(isinstance(MergeType.BINARY, MergeType))
        self.failUnless(isinstance(MergeType.TEXT_2WAY, MergeType))
        self.failUnless(isinstance(MergeType.TEXT_3WAY, MergeType))

    def testMergeStatus(self):

        from perforce.api import MergeStatus

        self.failUnless(isinstance(MergeStatus.QUIT, MergeStatus))
        self.failUnless(isinstance(MergeStatus.SKIP, MergeStatus))
        self.failUnless(isinstance(MergeStatus.MERGED, MergeStatus))
        self.failUnless(isinstance(MergeStatus.EDIT, MergeStatus))
        self.failUnless(isinstance(MergeStatus.THEIRS, MergeStatus))
        self.failUnless(isinstance(MergeStatus.YOURS, MergeStatus))

    def testMergeForce(self):

        from perforce.api import MergeForce

        self.failUnless(isinstance(MergeForce.AUTO, MergeForce))
        self.failUnless(isinstance(MergeForce.SAFE, MergeForce))
        self.failUnless(isinstance(MergeForce.FORCE, MergeForce))

class ClientApiTests(unittest.TestCase):
    """Tests for the perforce.api.ClientApi class."""

    def testConstructionAndDestruction(self):
        c1 = perforce.api.ClientApi()
        c2 = perforce.api.ClientApi()

        self.failUnless(isinstance(c1, perforce.api.ClientApi))
        self.failUnless(isinstance(c2, perforce.api.ClientApi))
        
        del c1
        del c2

    def testGetMethods(self):
        c = perforce.api.ClientApi()

        val = c.getCharset()
        val = c.getClient()
        val = c.getCwd()
        val = c.getHost()
        val = c.getLanguage()
        val = c.getOs()
        val = c.getPassword()
        val = c.getPort()
        val = c.getUser()

        del c

    def testSetMethods(self):
        c = perforce.api.ClientApi()

        c.setCharset('utf8')
        self.assertEqual(c.getCharset(), 'utf8')

        c.setClient('some-client')
        self.assertEqual(c.getClient(), 'some-client')

        from os import getcwd
        from os.path import join
        path = join(getcwd(), 'dummy')
        c.setCwd(path)
        self.assertEqual(c.getCwd(), path)
        
        c.setHost('localhost')
        self.assertEqual(c.getHost(), 'localhost')

        c.setLanguage('en')
        self.assertEqual(c.getLanguage(), 'en')

        c.setPassword('secret')
        self.assertEqual(c.getPassword(), 'secret')

        c.setPort('p4server:1666')
        self.assertEqual(c.getPort(), 'p4server:1666')

        c.setUser('p4user')
        self.assertEqual(c.getUser(), 'p4user')

        del c

    def testSetProtocol(self):

        c = perforce.api.ClientApi()

        # Just check that we can call the setProtocol method for now.
        c.setProtocol('tag', '')
        c.setProtocol('specstring', '')
        c.setProtocol('api', '57')

        del c

    def testSetTrans(self):

        c = perforce.api.ClientApi()

        c.setTrans(perforce.api.CharSet.NOCONV,
                   dialog=perforce.api.CharSet.UTF_8,
                   fnames=perforce.api.CharSet.UTF_8,
                   content=perforce.api.CharSet.UTF_8)

        del c

    def testSetTransUtf16(self):

        from perforce.api import CharSet, ClientApi

        c = ClientApi()

        self.assertRaises(ValueError, c.setTrans,
                          CharSet.UTF_16)

        if float(perforce.api.version) >= 2005.2:
            self.assertRaises(ValueError, c.setTrans,
                              CharSet.UTF_16_LE)
            self.assertRaises(ValueError, c.setTrans,
                              CharSet.UTF_16_BE)
            self.assertRaises(ValueError, c.setTrans,
                              CharSet.UTF_16_LE_BOM)
            self.assertRaises(ValueError, c.setTrans,
                              CharSet.UTF_16_BE_BOM)
            self.assertRaises(ValueError, c.setTrans,
                              CharSet.UTF_16_BOM)

        self.assertRaises(ValueError, c.setTrans,
                          CharSet.UTF_16, CharSet.UTF_8,
                          CharSet.UTF_8, CharSet.UTF_8)
        
        self.assertRaises(ValueError, c.setTrans,
                          CharSet.UTF_8, CharSet.UTF_8,
                          CharSet.UTF_16, CharSet.UTF_8)

        self.assertRaises(ValueError, c.setTrans,
                          CharSet.UTF_8, CharSet.UTF_8,
                          CharSet.UTF_8, CharSet.UTF_16)

        c.setTrans(CharSet.UTF_8, CharSet.UTF_16,
                   CharSet.UTF_8, CharSet.UTF_8)

        del c

    def testUnicodeGetSetMethods(self):

        from perforce.api import CharSet, ClientApi

        ###
        # Test P4USER get/set in presence of setTrans()
        
        c = ClientApi()

        # Set/get untranslated value
        c.setUser('fred')
        self.assertEqual(c.getUser(), 'fred')
        self.failUnless(isinstance(c.getUser(), str))

        # Now set a character set
        c.setTrans(CharSet.UTF_8)

        self.assertEqual(c.getUser(), u'fred')
        self.failUnless(isinstance(c.getUser(), unicode))

        ###
        # Test P4CLIENT get/set in presence of setTrans()

        c = ClientApi()

        # Set/get untranslated value
        c.setClient('my-client')
        self.assertEqual(c.getClient(), 'my-client')
        self.failUnless(isinstance(c.getClient(), str))

        # Should use default codec (ie ASCII)
        c.setClient(u'another-client')
        self.assertEqual(c.getClient(), 'another-client')
        self.failUnless(isinstance(c.getClient(), str))

        # Now set a character set
        c.setTrans(CharSet.UTF_8)

        self.assertEqual(c.getClient(), u'another-client')
        self.failUnless(isinstance(c.getClient(), unicode))

        # Should use the specified character set
        c.setClient(u'my-client')
        self.assertEqual(c.getClient(), u'my-client')
        self.failUnless(isinstance(c.getClient(), unicode))

        # Should use the default codec to obtain a Unicode string which is
        # then encoded using the specified character set
        c.setClient('some-client')
        self.assertEqual(c.getClient(), u'some-client')
        self.failUnless(isinstance(c.getClient(), unicode))

        ###
        # Test P4PORT get/set in presence of setTrans()
        # (Should always be an ASCII string)

        c = ClientApi()

        # Set/get untranslated value
        c.setPort('perforce:1666')
        self.assertEqual(c.getPort(), 'perforce:1666')
        self.failUnless(isinstance(c.getPort(), str))

        c.setPort(u'server:1667')
        self.assertEqual(c.getPort(), 'server:1667')
        self.failUnless(isinstance(c.getPort(), str))

        # Now set a character set
        c.setTrans(CharSet.UTF_8)

        self.assertEqual(c.getPort(), 'server:1667')
        self.failUnless(isinstance(c.getPort(), str))

        ###
        # Test P4HOST get/set in presence of setTrans()
        # (Should always be an ASCII string)

        c = ClientApi()

        # Set/get untranslated value
        c.setHost('machine')
        self.assertEqual(c.getHost(), 'machine')
        self.failUnless(isinstance(c.getHost(), str))

        c.setHost(u'machine2')
        self.assertEqual(c.getHost(), 'machine2')
        self.failUnless(isinstance(c.getHost(), str))

        # Now set a character set
        c.setTrans(CharSet.UTF_8)

        self.assertEqual(c.getHost(), 'machine2')
        self.failUnless(isinstance(c.getHost(), str))

        ###
        # Test P4PASSWD get/set in presence of setTrans()

        c = ClientApi()

        # Set/get untranslated value
        c.setPassword('secret')
        self.assertEqual(c.getPassword(), 'secret')
        self.failUnless(isinstance(c.getPassword(), str))

        c.setPassword(u's3cr3t')
        self.assertEqual(c.getPassword(), 's3cr3t')
        self.failUnless(isinstance(c.getPassword(), str))

        # Now set a character set
        c.setTrans(CharSet.UTF_8)

        self.assertEqual(c.getPassword(), u's3cr3t')
        self.failUnless(isinstance(c.getPassword(), unicode))

        c.setPassword(u'foobar')
        self.assertEqual(c.getPassword(), u'foobar')
        self.failUnless(isinstance(c.getPassword(), unicode))

    def testSetTicketFile(self):

        # setTicketFile is only available for perforce.api 2005.1 or later
        if float(perforce.api.version) < 2005.1:
            return
        
        c = perforce.api.ClientApi()
        
        ticketPath = os.path.join(os.getcwd(), 'ticketFile')
        c.setTicketFile(ticketPath)

        # TODO: Test that 'login' commands actually use this file.
        # For now we just test that we can call this method.

class OnlineClientApiTests(PerforceServerMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
      unittest.TestCase.__init__(self, *args, **kwargs)
      PerforceServerMixin.__init__(self)

    def testConnectingToServer(self):

        c = perforce.api.ClientApi()
        c.setPort(self.port)

        try:
            c.init()
            c.final()
        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())

        del c

    def testConnectionFailure(self):

        c = perforce.api.ClientApi()

        c.setPort('bogus-server:12345')

        try:
            c.init()
            self.fail('should have thrown ConnectionFailed')
        except perforce.api.ConnectionFailed, err:
            pass

        del c

    def testRunCommand(self):

        c = perforce.api.ClientApi()
        c.setPort(self.port)

        try:
            c.init()

            ui = perforce.api.ClientUser()
            try:
                try:
                    c.run('info', ui)
                except perforce.api.ConnectionDropped:
                    self.fail("connection dropped running command")
            finally:
                c.final()
        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())

        del c

    def testRunInvalidCommand(self):

        c = perforce.api.ClientApi()
        c.setPort(self.port)

        try:
            c.init()

            ui = perforce.api.ClientUser()
            try:
                try:
                    c.run('bogus', ui)
                except perforce.api.ConnectionDropped:
                    self.fail("connection dropped running command")
            finally:
                c.final()
        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())

        del c

    def testRunCommandWithClientUserSubclass(self):

        class TestClientUser(perforce.api.ClientUser):

            def __init__(self):
                self.events = []

            def outputInfo(self, level, msg):
                self.events.append(msg)

        c = perforce.api.ClientApi()
        c.setPort(self.port)

        try:
            c.init()

            try:
                try:
                    ui = TestClientUser()
                    c.run('info', ui)

                    self.failUnless(ui.events)
                    self.failUnless(len(ui.events) > 5)
                    
                except perforce.api.ConnectionDropped:
                    self.fail("connection dropped running command")
            finally:
                c.final()

        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())

    def testRunInvalidCommandWithClientUserSubclass(self):

        class TestClientUser(perforce.api.ClientUser):

            def __init__(self):
                self.messages = []
                self.errors = []

            def outputInfo(self, level, message):
                self.messages.append(message)

            def outputError(self, message):
                self.errors.append(message)

        c = perforce.api.ClientApi()
        c.setPort(self.port)

        try:
            c.init()

            try:
                try:
                    ui = TestClientUser()
                    c.run('bogus', ui)
                    self.failUnless(ui.errors)
                except perforce.api.ConnectionDropped:
                    self.fail("connection dropped running command")
            finally:
                c.final()
        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())

        del c

    def testSetProg(self):

        c = perforce.api.ClientApi()
        c.setPort(self.port)

        try:
            c.init()
            c.setProg('test-program')
            c.final()
        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())

        del c

    def testRunCommandWithArgs(self):

        c = perforce.api.ClientApi()
        c.setPort(self.port)

        try:
            c.init()

            try:
                try:
                    ui = perforce.api.ClientUser()
                    args = ('-o', c.getUser())
                    c.setArgs(args)
                    c.run('user', ui)
                except perforce.api.ConnectionDropped:
                    self.fail("connection dropped running command")
            finally:
                c.final()
        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())

        del c
        
class OnlineUnicodeClientApiTests(PerforceServerMixin, unittest.TestCase):

    def __init__(self, *args, **kwargs):
      unittest.TestCase.__init__(self, *args, **kwargs)
      PerforceServerMixin.__init__(self, unicodeMode=True)

    def testRunCommand(self):

        from perforce.api import ClientApi, ClientUser, CharSet

        c = ClientApi()
        c.setPort(self.port)
        c.setTrans(CharSet.UTF_8)

        try:
            c.init()

            ui = ClientUser()
            try:
                try:
                    c.run('info', ui)
                except perforce.api.ConnectionDropped:
                    self.fail("connection dropped running command")
            finally:
                c.final()
        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())


    def testRunCommandWithClientUserSubclass(self):

        class TestClientUser(perforce.api.ClientUser):

            def __init__(self):
                self.events = []

            def outputInfo(self, level, msg):
                self.events.append(msg)

        c = perforce.api.ClientApi()
        c.setPort(self.port)
        c.setTrans(perforce.api.CharSet.UTF_8)

        try:
            c.init()

            try:
                try:
                    ui = TestClientUser()
                    c.run('info', ui)

                    self.failUnless(ui.events)
                    self.failUnless(len(ui.events) > 5)
                    for i in xrange(5):
                        self.failUnless(isinstance(ui.events[i], unicode))
                    
                except perforce.api.ConnectionDropped:
                    self.fail("connection dropped running command")
            finally:
                c.final()

        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())
        

    def testRunCommandWithTaggedOutput(self):

        class TestClientUser(perforce.api.ClientUser):

            def __init__(self):
                self.record = None

            def outputStat(self, data):
                self.record = data

        c = perforce.api.ClientApi()
        c.setPort(self.port)
        c.setTrans(perforce.api.CharSet.UTF_8)
        c.setProtocol('tag', '')

        try:
            c.init()

            try:
                try:
                    ui = TestClientUser()
                    c.run('info', ui)

                    # 'p4 info' only tagged for 2003.2 or later servers
                    if int(c.getProtocol('server2')) >= 17:
                        self.failUnless(ui.record)
                        self.failUnless(len(ui.record) > 5)
                        for key, value in ui.record.iteritems():
                            self.failUnless(isinstance(key, unicode))
                            self.failUnless(isinstance(value, unicode))
                    
                except perforce.api.ConnectionDropped:
                    self.fail("connection dropped running command")
            finally:
                c.final()

        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())

    def testRunCommandWithArgs(self):

        c = perforce.api.ClientApi()
        c.setPort(self.port)
        c.setTrans(perforce.api.CharSet.UTF_8)

        try:
            c.init()

            try:
                try:
                    
                    # Mixed str/unicode strings
                    ui = perforce.api.ClientUser()
                    args = ('-o', c.getUser())
                    c.setArgs(args)
                    c.run('user', ui)

                    # All unicode strings
                    args = (u'-o', u'my-client')
                    c.setArgs(args)
                    c.run(u'user', ui)
                    
                except perforce.api.ConnectionDropped:
                    self.fail("connection dropped running command")
            finally:
                c.final()
        except perforce.api.ConnectionFailed, err:
            self.fail("could not connect to server '%s'" % c.getPort())

        del c
