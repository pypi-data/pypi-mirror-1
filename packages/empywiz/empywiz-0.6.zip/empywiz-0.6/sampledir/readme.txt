Running expandtemplates.py on this directory will create sample1.txt,
sample2.txt and empy_rename_files. 

sample1.txt will be renamed according to empy_rename_files, for
example if you specified the variable 'var1' as 'spam', sample1.txt
will be renamed to containsspamonly.txt. 

This readme.txt will be left untouched, because it has no '.em'
prefix. 'empy_rename_files' itself will be deleted, not automatically
but because the 'empy_rename_files' should be "renamed" to
<delete>. It's a good idea to always include that line in the
empy_rename_files.em, if you need it.

Note that this sample directory is also a good example template for
prjwiz.py. Copy this directory to your 'templates directory' (see
pywizconfig) and run prjwiz.py.
