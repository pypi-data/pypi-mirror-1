from base import IMSTransportTestCase
from collective.imstransport.utilities.webct.webctreader import WebCTReader
from unittest import TestSuite, makeSuite
from xml.dom import minidom



manifests = """"<manifest>
  </manifest>
  <manifest>
  </manifest>
  <manifest>
  </manifest>
"""

toplevel = """<general>
      <title>
        <langstring xml:lang="en-US">WebCT Test Course</langstring>
      </title>
      <language>
        en
      </language>
      <description>
        <langstring xml:lang="en-US">
          This is a WebCT Test Course
        </langstring>
      </description>
      <keyword>
        <langstring xml:lang="en-US">
          test
        </langstring>
        <langstring xml:lang="en-US">
          module
        </langstring>
        <langstring xml:lang="en-US">
          course
        </langstring>
      </keyword>
    </general>
    <educational>
      <learningresourcetype>
        <source>
          <langstring xml:lang="x-none">WebCT</langstring>
        </source>
        <value>
          <langstring xml:lang="x-none">Course</langstring>
        </value>
      </learningresourcetype>
    </educational>
"""

organizations = """<organizations default="1000">
  <organization identifier="1000">
    <item identifier="1002" identifierref="2000">
      <title>Test Title 1</title>
    </item>
    <item identifier="1003" identifierref="2001">
      <title>Test Title</title>
    </item>
  </organization>
</organizations>
"""

resources = """<resources>
  <resource identifier="2000" href="test.html" type="webcontent" />
</resources>
"""

general = """<general>
      <identifier>
        asdf
      </identifier>
      <title>
        <langstring xml:lang="en">
          asdf
        </langstring>
      </title>
      <language>
        en
      </language>
      <description>
        <langstring xml:lang="en">
          this is a test
        </langstring>
      </description>
      <keyword>
        <langstring xml:lang="en">
          Hello
        </langstring>
        <langstring xml:lang="en">
          There
        </langstring>
      </keyword>
    </general>
"""

lifecycle = """<lifecycle>
  <contribute>
    <role>
      <source>
        <langstring xml:lang="x-none">
          LOMv1.0
        </langstring>
      </source>
      <value>
        <langstring xml:lang="x-none">
          author
        </langstring>
      </value>
    </role>
    <centity>
      <vcard>
        BEGIN:VCARD
        FN: Sandra Suzannah Serendipity
        END:VCARD
      </vcard>
    </centity>
    <centity>
      <vcard>
        BEGIN:VCARD 
        FN:HUGO 
        END:VCARD
      </vcard>
    </centity>
    <centity>
      <vcard> 
        BEGIN:VCARD
        FN: Quincy Adams
        END:VCARD
      </vcard>
    </centity>
    <date>
      <datetime>
        2009-05-09 15:07:16
      </datetime>
    </date>
  </contribute>
  <contribute>
    <role>
      <source>
        <langstring xml:lang="x-none">
          LOMv1.0
        </langstring>
      </source>
      <value>
        <langstring xml:lang="x-none">
          unknown
        </langstring>
      </value>
    </role>
    <centity>
      <vcard>
        BEGIN:VCARD
        FN:Garth
        END:VCARD
      </vcard>
    </centity>
    <date>
      <datetime>
        2009-05-11 15:07:16
      </datetime>
    </date>
  </contribute>
</lifecycle>
"""

technical = """<technical>
  <format>
    image/png
  </format>
</technical>
"""

rights = """<rights>
  <copyrightandotherrestrictions>
    <source>
      <langstring xml:lang="x-none">
        LOMv1.0
      </langstring>
    </source>
      <value>
        <langstring xml:lang="x-none">
          yes
        </langstring>
      </value>
   </copyrightandotherrestrictions>
   <description>
     <langstring xml:lang="x-none">
       This material is copyrighted.
     </langstring>
   </description>
</rights>
"""

entity="""<centity>
  <vcard>
    BEGIN:VCARD
    FN:  Harrison Cheever
    EMAIL;INTERNET: harrc@plone.org
    END:VCARD
  </vcard>
</centity>
"""

LOM_WEBCT_namespace = 'http://www.imsproject.org/metadata'
LOM_IMSCP_namespace = 'http://www.imsglobal.org/xsd/imsmd_v1p2'
LOM_version = 'LOMv1.0'

class TestWebCTReader(IMSTransportTestCase):
    """
    """

    def testParseManifest(self):
        """ Test parsing of manifest node """
        webctreader = WebCTReader()
        doc = webctreader.parseManifest('<test>Hello</test>')
        assert(doc.getElementsByTagName('test'))
        
    def testReadManifestsMetadata(self):
        """ Test the reading of top level manifests """
        webctreader = WebCTReader()
        doc = minidom.parseString(manifests)
        mans = webctreader.readManifests(doc)
        self.assertEqual(len(mans), 3)

    def testReadPackageMetadata(self):
        """ Test the reading of package level metadata """
        webctreader = WebCTReader()
        manifest = '<metadata><lom xmlns="%s">' %LOM_WEBCT_namespace + toplevel + '</lom></metadata>'
        doc = webctreader.parseManifest(manifest)
        pmd = webctreader.readPackageMetadata(doc)
        assert(pmd.has_key('title'))
        self.assertEqual(pmd['title'], 'WebCT Test Course')
        assert(pmd.has_key('language'))
        self.assertEqual(pmd['language'], 'en-US')
        assert(pmd.has_key('description'))
        self.assertEqual(pmd['description'], 'This is a WebCT Test Course')
        assert(pmd.has_key('subject'))
        self.assertEqual(pmd['subject'], ['test', 'module', 'course'])        
        assert(pmd.has_key('webcttype'))
        self.assertEqual(pmd['webcttype'], 'Course')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestWebCTReader))
    return suite
