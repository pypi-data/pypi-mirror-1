# First install the package (python setup.py install),
# then run these tests from within the test directory

import unittest, os
from cStringIO import StringIO
import tnef

tmpdir = "tmptestdir"

class TestTnefFunctions(unittest.TestCase):
    
   def setUp(self):
      os.mkdir(tmpdir)
      
   def tearDown(self):
      os.rmdir(tmpdir)

   def testHasBody(self):
      self.failUnless(tnef.hasBody(open("body.tnef")))
      self.failIf(tnef.hasBody(open("multi-name-property.tnef")))

   def testHasFiles(self):
      self.failUnless(tnef.hasFiles(open("two-files.tnef")))
      self.failIf(tnef.hasFiles(open("multi-name-property.tnef")))
      self.failIf(tnef.hasFiles(open("body.tnef")))

   def testHasContent(self):
      self.failUnless(tnef.hasContent(open("two-files.tnef")))
      self.failIf(tnef.hasContent(open("multi-name-property.tnef")))
      self.failUnless(tnef.hasContent(open("body.tnef")))

   def testlistFilesAndTypes_Body_NoMimeTypes(self):
      correct = {
         "AUTOEXEC.BAT": "",
         "CONFIG.SYS": "",
         "boot.ini": "",
         "%s.rtf" % tnef.DEFAULTBODY: "",
      }
      tested = tnef.listFilesAndTypes(open("data-before-name.tnef"), bodyname=tnef.DEFAULTBODY)
      self.assertEqual(correct, tested)
      
   def testlistFilesAndTypes_NoBody_MimeTypes(self):
      correct = {
         "AUTHORS": "application/octet-stream",
         "README": "application/octet-stream",
      }
      tested = tnef.listFilesAndTypes(open("two-files.tnef"))
      self.assertEqual(correct, tested)
      
   def testExtractAll_Body_NoMimeTypes(self):
      "use StringIO to make sure filelike objects are ok"
      pth = tmpdir + os.sep
      correct = [
         "%sAUTOEXEC.BAT" % pth,
         "%sCONFIG.SYS" % pth,
         "%sboot.ini" % pth,
         "%s%s.rtf" % (pth, tnef.DEFAULTBODY)
      ]
      tfile = open("data-before-name.tnef")
      files = tnef.listFilesAndTypes(tfile, bodyname=tnef.DEFAULTBODY).keys()
      tfile = StringIO(open("data-before-name.tnef").read())
      listing = tnef.extractAll(tfile, targetdir=tmpdir, bodyname=tnef.DEFAULTBODY)
      for fn in files:
         pth = tmpdir + os.sep + fn
         self.failUnless(os.path.isfile(pth))
         os.remove(pth)
      self.assertEqual(correct, listing)


if __name__=="__main__":   
   unittest.main()
   
