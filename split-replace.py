# -*- coding: utf-8 -*-
import os, sys,shutil, re

mydir= 'C:\python-snippts'

# find and replace in a dir by multiple pairs of regex

findreplace = [
(re.compile(ur'''if ([^{]+) {([^}]+)}''',re.U|re.M), ur'''if \1 then \2end'''), 
(re.compile(ur'''!=''',re.U|re.M), ur'''~='''),
(re.compile(ur'''next;''',re.U|re.M), ur'''back()'''),
(re.compile(ur'''//''',re.U|re.M), ur'''--'''),
(re.compile(ur'''/\*''',re.U|re.M), ur'''--[['''),
(re.compile(ur'''\*/''',re.U|re.M), ur'''--]]'''),
(re.compile(ur'''stats \|= ([^;]+)''',re.U|re.M), ur'''stats = ((stat) or (\1))''')
# more regex pairs here
]

def splitIntoFiles(filePath):
    "split the result into different files"
    input = open(filePath,'rb')
    s=unicode(input.read(),'utf-8')
    input.close()
    numRep = re.findall(r'''void ([^\(]+) \(\) {([^}]+)}''',s)
    for couple in numRep:
        print ' filename', couple[0]
        print ' text',couple[1]
        outtext = str(couple[1])
        input = open(mydir+'/'+couple[0]+'.lua','w')
        input.write(outtext)
        input.truncate()
        input.close()

def replaceStringInFile(filePath):
    """replaces all string by a regex substitution"""

    backupName=filePath+'~re~'

    print 'reading:', filePath
    input = open(filePath,'rb')
    s=unicode(input.read(),'utf-8')
    input.close()

    numRep=None
    for couple in findreplace:
      if numRep is not None:
         numRep = re.search(couple[0],s)
      outtext = re.sub(couple[0],couple[1], s)
      s=outtext

    if numRep:
      print ' writing:', filePath
      shutil.copy2(filePath,backupName)
      outF = open(filePath,'r+b')
      outF.read() # we do this way to preserve file creation date
      outF.seek(0)
      outF.write(s.encode('utf-8'))
      outF.truncate()
      outF.close()

def myfun(dummy, curdir, filess):
    for child in filess:
        if re.search(r'.+\.c$', child, re.U) and os.path.isfile(curdir + '/' + child):
            replaceStringInFile(curdir+'/'+child)
            splitIntoFiles(curdir+'/'+child)

os.path.walk(mydir, myfun, 3)