##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
# jsolait installer
#
#
# jsolait is available on the net, licensed LGPL. When you run this
# script, you will download, unzip, and make appropriate changes to
# the jsolait library to make it usable with jsonserver.
# jwashin 2005-05-16
# 2005-09-21 Updated for 20050914 beta of jsolait

import os, md5, urllib

#get the current, working version of jsolait
#this one (a beta of 1.1) works as of now (3 Jun 05)
loc = 'http://jsolait.net/download/'

filename = 'jsolait.2005-11-15.small.zip'
#md5sum = '69014dddf37fb7cb7b88b5eac84d1569'
#md5sum = '475b7a505d6ab911b25818831244bd43'
md5sum = 'c21c32a7a8756a35a0e48a30b710b3e1'
fileurl = loc + filename

#Assure the folders are there.
for directory in ['src','doc','lib','libws']:
    if not os.path.exists(directory):
        os.mkdir(directory)

zippedfile = os.path.join('src',filename)

#get file unless it is already there
if not os.path.exists(zippedfile):
    print "retrieving %s" % fileurl
    urllib.urlretrieve(fileurl,zippedfile)
else:
    print "%s exists; reprocessing. " % zippedfile
    print "to retrieve again, delete or rename %s." % zippedfile

#check file signature
print "checking md5"
filedata = file(zippedfile,'r').read()
check = md5.new(filedata).hexdigest()
if not check == md5sum:
    raise ValueError('md5 sums do not match')

#got the file; now, unzip it.

import zipfile

print "unzipping %s" % zippedfile

zip = zipfile.ZipFile(zippedfile,'r')

filesList = zip.namelist()

        
#put the files in the folders
for k in filesList:
    if not k.endswith('/'):
        f = os.path.split(k)
        #print f
        if 'doc' in f[0]:
            file(os.path.join('doc',f[1]),'wb').write(zip.read(k))
        elif 'libws' in f[0]:
            file(os.path.join('libws',f[1]),'wb').write(zip.read(k))
        elif 'lib' in f[0]:
            file(os.path.join('lib',f[1]),'wb').write(zip.read(k))
        else:
            file(f[-1],'wb').write(zip.read(k))

# patch to modify paths in init.js
# init.js is no more, replaced by jsolait.js, so fix those paths

linesep = os.linesep
mfile = 'jsolait.js'
print "patching %s" % mfile
t = file(mfile,'U')
lines = t.readlines()
t.close()
t = file(mfile,'w')
moda = False
modb = False
lineadded = False
for k in lines:
    d = k.rstrip()
    #set the installPath to the resource directory name
    if d.find('mod.baseURI="./jsolait"') >= 0:
        s = 'mod.baseURI = "/++resource++jsolait";'
    #this one works around some javascript clients not using js if it's already in cache
    #OK, we load the js each time it's used, but it still works if you refresh the page
    #in konqueror or safari.
    #elif d.find('xmlhttp.open("GET", url, false);') >= 0:
    #    s = 'var d = new Date();\nxmlhttp.open("GET", url +"?m="+d.getTime(), false);'
    #elif d.find('xmlhttp.open("GET", uri, false);') >= 0:
    #    s = 'var d = new Date();\nxmlhttp.open("GET", uri +"?m="+d.getTime(), false);'
    #elif d.find('xmlhttp.open("GET",uri,false);') >= 0:
    #    s = 'var d=new Date();%sxmlhttp.open("GET",uri +"?m="+d.getTime(),false);' % linesep
    elif d.find('baseURI)s') > 0:
        s = d.replace('/','',1)
        if lineadded == False:
            #add a line for pythonkw
            s = s + linesep + 'pythonkw:"%(baseURI)slib/pythonkw.js",'
            lineadded = True
    elif d.find('if(xmlhttp.status==200') == 0:
        s = 'if(xmlhttp.status==200||xmlhttp.status==0||xmlhttp.status==null){'
    else:
        s = d
    t.write('%s%s' % (s,linesep))
t.write('importModule=imprt'+linesep)
t.close()

#for compat with prev version, copy jsolait.js to init.js
t = file(mfile,'r')
z = t.readlines()
t.close()
f = file('init.js','w')
for k in z:
    f.write(k)
f.close()

#patch text/plain and text/xml to text/x-json
mfile = 'jsonrpc.js'
os.chdir('lib')
print "patching %s" % mfile
t = file(mfile,'U')
lines = t.readlines()
t.close()
t = file(mfile,'w')
for k in lines:
    d = k.rstrip()
    if d.find('text/plain') >= 0:
        s = d.replace('text/plain','application/json-rpc')
    elif d.find('text/xml') >= 0:
        s = d.replace('text/xml','application/json-rpc')
    elif d.find('ImportFailed(') > 0 and not d.endswith(';'):
        s = d + ';'
    else:
        s = d
    t.write('%s%s' % (s,linesep))
t.close()
os.chdir('..')
print "done."
print "original zip file is %s" % zippedfile
