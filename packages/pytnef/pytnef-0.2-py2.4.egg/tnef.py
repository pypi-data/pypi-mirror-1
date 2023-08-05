#!/usr/local/bin/python2.4
import os
from subprocess import Popen, PIPE


__all__ = ("TNEFError", "hasBody", "hasFiles", "listFilesAndTypes", "extractAll", "hasContent")

DEFAULTBODY = "tnfbdyname"

class TNEFError(Exception):
   "raised whenever something goes wrong invoking the command-line"


def runTnef(sourcefile, args):
   "helper function"
   args = ("tnef",) + args
   TNEF = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
   out, err = TNEF.communicate(sourcefile.read())
   
   if TNEF.returncode:
      raise TNEFError("Problem running tnef command: %s" % err)

   return out
   

def hasBody(sourcefile):
   "true if the TNEF file contains a content body"
   files = listFilesAndTypes(sourcefile, bodyname=DEFAULTBODY).keys()
   if DEFAULTBODY in "".join(files):
      return True
   return False

   
def hasFiles(sourcefile):
   "true if the TNEF file contains embedded files; ignores body"
   filenames = listFilesAndTypes(sourcefile, bodyname=DEFAULTBODY).keys()
   if not filenames or DEFAULTBODY in filenames[0]:
      return False
   return True


def hasContent(sourcefile):
   "true of the file contains body OR files"
   if listFilesAndTypes(sourcefile):
      return True
   return False


def parseListing(listing):
   "return a dict of file names as keys & types as values"
   listing = listing.strip().split("\n")
   files = {}
   for l in listing:
      if l:
         fname, ftype = l.split('|')
         files[fname] = ftype
   return files

   
def listFilesAndTypes(sourcefile, bodyname=None):
   "list files, including body"
   args = ("--list-with-mime-types",)   

   if bodyname:
      args += ("--save-body=%s" % bodyname,)
   else:
      args += ("--save-body",)

   output = runTnef(sourcefile, args)
   return parseListing(output)


def extractAll(sourcefile, targetdir=None, bodyname=None):
   "return {fullpath: contenttype} list of extracted stuff"

   args = ("--overwrite",)

   if bodyname:
      args += ("--save-body=%s" % bodyname,)
   else:
      args += ("--save-body",)

   if targetdir:
      args += ("--directory=%s" % targetdir,)
   else:
      targetdir = os.curdir
   files = []
   runTnef(sourcefile, args) #gives no output
   return [targetdir + os.sep + fn for fn in os.listdir(targetdir)]
