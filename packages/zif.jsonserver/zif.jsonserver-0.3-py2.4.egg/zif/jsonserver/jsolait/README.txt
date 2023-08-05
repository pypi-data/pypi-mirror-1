This is a place for the jsolait javascript library from 

 http://jsolait.net/
 
It will be accessible as a resource , '/@@/jsolait/...'
 
Manual installation is something like:

get the library
extract it here
fix the paths in jsolait.js so that all .js files are accessible from the 
/@@/jsolait resourceDirectory, i.e., this folder
fix the submodule GET so that things still work after page refresh on konqueror and safari 
    (just add a ?s="[timestamp]" so the file gets refetched instead of mouldering in cache)
fix content-types in jsonrpc.js from text/plain or text/xml to text/x-json

There is a script here that does the above for you. It's small, and
you probably want to read it so that it cannot suprise you.  After 
viewing it, use it from this directory:

python install_jsolait.py

The installer uses urllib and writes files in this directory, so expect
it to fail if you do not have write privileges or an accessible internet 
connection.
 
Jim Washington
21 Sep 2005
