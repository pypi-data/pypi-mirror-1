==========================
jsolait javascript library
==========================

zif.jsonserver is now bundled with jsolait javascript library.

Documentation for the library is avaialable at:

  http://jsolait.net/wiki/documentation
  
jsolait will be accessible as a resource::

  '/@@/jsolait/...'
 

Historical manual installation notes
------------------------------------

The following manual installation notes are have been left for reference. You
NO LONGER need to manually install jsolait for the zif.jsonserver package::

  * obtain the library
  * extract it
  * fix the paths in jsolait.js so that all .js files are accessible from 
    the /@@/jsolait resourceDirectory, i.e., this folder
  * fix the submodule GET so that things still work after page refresh on
    konqueror and safari (just add a ?s="[timestamp]" so the file gets 
    refetched instead of mouldering in cache)
  * fix content-types in jsonrpc.js from text/plain or text/xml to text/x-json

Executing the following script in the jsolait folder with do this for you.

python install_jsolait.py

Note, the script uses urllib and writes files in this directory, so expect
it to fail if you do not have write privileges or an accessible internet 
connection.

