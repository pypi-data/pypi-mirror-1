#!/usr/bin/env python2.4
"""\
empywiz
-------

A template expansion system with interactive prompting

Usage
=====

One way to expand a target:

    expandtemplate.py [options] target

If ``target`` is a file, it is expanded and the expansion is sent to
clipboard (this is called Clipboard mode). If it is a directory, it is
expanded in the Directory expansion mode. To get the list of available
options, execute ``python expandtemplate.py -h``.

Clipboard mode
==============

This program takes a single EmPy template file (.em) as an argument
and checks whether it contains 'ignigicators' that hint the expansion
system which variables need to be prompted. After the expansion the
produced text is sent to the Windows clipboard, to be pasted into your
program/whatever.

Let's assume that the template file to be expanded has the following
significators:

    @%prompt 'classname', 'once'
    @%prompt 'methodname rettype'


Here, the user will be prompted for the value of ``classname``
variable exactly once. Then the user will be prompted for
``methodname`` and ``retval`` variables, after which the
``methodname`` and ``retval`` variables are asked again, ad
infinitum. This way the user doesn't need to change the classname
every time a new method needs to be created.

Here is a sample template::

    @%prompt 'classname','once'
    @%prompt 'methodname rettype'
    @%prompt 'somearray','ListPrompter()', 'once'

    @(rettype) @(classname)::@(methodname)()
        {
        }


Syntax of ``prompt``::

  ``@%prompt <varlist> [,<prompter> ] [, <qualifier...>]``

Where ``<varlist>`` is a string consisting of variable names seperated
by whitespace.

``<prompter>`` is optional. If a prompter is a string object, it is
evaluated in the namespace of ``wizprompters`` module (see
``wizprompters.py``). The evaluation should yield an object with the
method ``prompt(varname)``, which will be called with the current
variable name at the prompting time (before expansion). Typically
prompter is an instruction that instantiates a class,
e.g. ``'IntPrompter(min=0,max=100)'`` instantiates an IntPrompter,
which has the method ``prompt()``.

If a prompter isn't specified (i.e. the first arg after varlist is not
an object with the ``prompt()`` method) a normal string prompter is
used. Qualifiers can be anything I can think up, so far ``'once'``
makes the system ask for the variable only once.

Note how the value of variable is fetched by
``@(variablename)``. ``@variablename`` works also, if it is not
followed by any special characters. Arbitrary python code can be
executed also, check the EmPy homepage for details
(http://www.alcyone.com/pyos/empy/).



Directory expansion mode
========================

Sometimes several files need to be created at once. You can do this by
creating a directory that contains a number of files, in addition to
some template files with ``.em`` prefix. Give the directory as a startup
parameter for this program. All the .em files in the directory will be
expanded recursively, with variables prompted from the user similar to
the Clipboard mode (except that ``once`` has no meaning - all variables
are asked only once!)

Renaming files
--------------

After the directory expansion, the 'root' of the template directory
will be checked for the existence of a file names
'empy_rename_files'. It should contain entries like this::

    oldname.txt,newname.txt
    garbage.txt,<delete>

The catch is that ``empy_rename_files`` was created by expansion of
``empy_rename_files.em``, which can contain variable references
etc. Thus you can use the variable values to determine file names that
will be created.

``<delete>`` is a magical conjuration to, you guessed it, delete the
file.


Defaults
========

The module ``wizdefaults.py``, in the same directory as this program,
contains normal Python code to define default values to some
variables. If the variable can be found in wizdefaults, it is not
asked, but the default is used instead. Good candidates are ``author``,
etc.


Installation
============

This script should be linked via a shortcut from your 'Send To'
directory (``Documents and Settings/username/SendTo``), that way you can
navigate to the templates directory and 'send' the templates to this
script. Note that the shortcut should have the target such as
``c:\python24\scripts\expandtemplate.exe``

Requirements for this program to work:

Python >= 2.3
   http://www.python.org
win32all extensions (required for clipboard mode)
   http://starship.python.net/crew/mhammond/win32/Downloads.html
EmPy
   Included (em.py), available at http://www.alcyone.com/pyos/empy/
"""

__program__ =  'pywiz'
__version__ =  '0.14'
__revision__ = '$LastChangedRevision: 54 $'
__date__    =  '$LastChangedDate: 2003-11-10 20:07:45 +0200 (Mon, 10 Nov 2003) $'
__url__     =  'http://www.students.tut.fi/~vainio24/pywiz/'
__author__  =  'Ville Vainio <ville.nospamvainio@spammehardtut.fi>'
__copyright__= 'Copyright (C) 2003 Ville Vainio'
__license__ =  'BSD'

import re,sys,os,operator,shutil,tempfile,time
import em
import wizdefaults
import wizprompters
import empywizcfg as conf
from distutils import dir_util
from optparse import OptionParser



class ExpandError(Exception):
    pass

def setClipText(aString): 
    import win32clipboard as w  # only works with win32all, not impl yet for Linux
    import win32con

    w.OpenClipboard()
    w.EmptyClipboard()
    aString = aString.replace("\n","\r\n")
    w.SetClipboardData(win32con.CF_TEXT,aString) 
    w.CloseClipboard()

def list_significators(templ):
    signif = []
    for l in open(templ):
        sig = re.search(em.SIGNIFICATOR_RE_STRING,l)
        if sig:
            signif.append(sig.groups())
    return signif
    
def promptvars(vars):
    questionsasked = 0
    allvars = vars.keys()
    allvars.sort()
    vals = {}
    for v in allvars:
        try:
            val = getattr(wizdefaults,v)
            print "'%s' acquired from wizdefaults" % v
            vals[v] = val
            continue
        except AttributeError:
            pass

        questionsasked+=1

        if isinstance(vars[v][0], basestring):
            try:
                prompter = eval(vars[v][0],wizprompters.__dict__)
            except:
                print "Cannot eval '%s' as a prompter (exception) -> using normal string prompter." % vars[v][0]
                prompter = wizprompters.DefaultPrompter()
        else:
            prompter = wizprompters.DefaultPrompter()

        if hasattr(prompter,'prompt') and callable(prompter.prompt):
            val = prompter.prompt(v) # call the prompter
        else:
            val = raw_input("%s: " % v)

        vals[v] = val

    return vals,questionsasked

def expand_with_vars(tmpl, vars):
    exp= em.expand(open(tmpl).read(),vars)
    #setClipText(exp)
    return exp


def find_vars(templates):
    vars = {}
    for templ in templates:
        sigs = list_significators(templ)
        for sig in sigs:
            if sig[0] != "prompt":
                continue
            data = eval(sig[1])

            if isinstance(data, basestring): # lonely string is a normal var list
                prompttype = (None,)
                varlist = data.split()
            elif operator.isSequenceType(data):
                prompttype = data[1:]
                varlist = data[0].split()

            for v in varlist:
                if vars.has_key(v) and vars[v] != prompttype:
                    print " *** Warning! %s: possibly conflicting definition (%s versus %s) for '%s' !! Choosing the first one..." % (templ,prompttype,vars[v],v)
                vars[v] = prompttype
    return vars

    

def file_to_clipboard(template):
    print " ---- Clipboard mode * Template preview -------"
    print "".join(open(template).readlines()[:20])
    vars = find_vars([template])
    print vars
    permvars = dict([ (k,vars[k]) for k in vars.keys() if 'once' in vars[k]])
    print "-- Enter values for permanent variables --"

    variables = {}
    permvals,dummy = promptvars(permvars)

    variables.update(permvals)
    while 1:
        print " -- Enter values for variables --"
        questions = 0
        normalvars = dict([ (k,vars[k]) for k in vars.keys() if 'once' not
                             in vars[k]])
                             
        vals,questions = promptvars(normalvars)
        variables.update(vals)
        exp = expand_with_vars(template,variables)
        setClipText(exp)
        print "** Expansion (%d bytes) sent to clipboard **" % len(exp)
        if questions == 0:
            sys.exit()


def ask_question(prompt, legal):
    while 1:
        response = raw_input(prompt)
        if response in legal:
            return response
        print "Illegal input, enter one of",legal
        
def expand_tree(path):
    path = os.path.abspath(path)
    print "Directory expansion mode on",path
    os.chdir(path)
    templates = []
    for dpath, dnames, fnames in os.walk(path):
        templates += [os.path.join(dpath,f)
          for f in fnames if f.lower().endswith(".em")]
    print "Found templates:",templates
    if not templates:
        print "Nothing to do, bailing out!"
        return 
    vars = find_vars(templates)

    # ask in alphabetical order - set order is random
    print "Variables:",vars
    print " -- Enter values for variables --"
    vals,dummy = promptvars(vars)
    newnames = []
    force = force_overwrite
    for t in templates:
        newname = t[:-3]
        print "Expanding",t,"to",newname
        if os.path.isfile(newname) and not force:
            print "File exists already: f = force overwrite, a=overwrite all,q=quit"
            forcecmd = ask_question("Action: ",['f','q','a'])
            
            if forcecmd == "q":
                return
            elif forcecmd == "a":
                force = 1
            elif forcecmd == "f":
                pass
            else:
                assert 0

        exp = expand_with_vars(t, vals)
        open(newname,"w").write(exp)
        newnames.append(newname)

    print "produced following files:",newnames

    renames = []
    renamefile = os.path.join(path, "empy_rename_files")
    if os.path.isfile(renamefile):
        renames = [l.strip().split(",") for l in open(renamefile) if
          l.find(',') != -1]
        print "'empy_remane_files' found, need to perform the following renames:"
        print "\n".join( [" -> ".join([old,new]) for old,new in renames] )
        

    print "Enter 'y' to commit (remove .em files), 'n' to revert (remove new files), 'q' to quit"
    if conf.preview_changes:
        os.startfile(path)
    if preserve_emfiles:
        cmd="q"
    elif delete_emfiles:
        cmd = "y"
    else:
        cmd = ask_question("Commit changes? ",['y','n','q'])

    if cmd == "y":
        print "Deleting .em files..."
        [os.remove(f) for f in templates]
        print "Renaming..."
        for old,new in renames:
            print old,"->",new
            if new.find("<delete>")!=-1:
                print "(Deleting %s)" % old
                os.remove(old)
            else:
                os.rename(old,new)
        
    elif cmd == "n":
        print "Deleting all the produced files!"
        [os.remove(f) for f in newnames]
    elif cmd == "q":
        print "All files left intact"
        return
    else:
        assert 0

def choose_from_list(l):
    print "\n".join(["%2d.  %s" % t for t in enumerate(l)])
    while 1:
        inp = raw_input("Choice: ")
        try:
            return l[int(inp)]
        except:
            pass
    
def discover_template(template):
    if not os.path.isdir(template):
        projects = [ d for d in os.listdir(conf.project_templates_dir) 
                     if os.path.isdir(os.path.join(conf.project_templates_dir,d))]
        print projects
        prjs = [p for p in projects if not template or template.lower() in p.lower()]
        if not prjs:
            prjs = projects
        if len(prjs) == 1:
            prj = prjs[0]
        else:
            prj = choose_from_list(prjs)
        tmplpath = os.path.join(conf.project_templates_dir,prj)
    else:
        tmplpath = template
    return tmplpath
    
def expand_to_dir(template, td):
    tmplpath = discover_template(template)
    dir_util.copy_tree(tmplpath, tempdir)
    expand_tree(tempdir)
    dir_util.copy_tree(tempdir, td)
    
def process_existing_files(roots, templates):

    touchfiles = []
    for root in roots:
        for dpath, dnames, fnames in os.walk(root):
            for fn in fnames:
                fname = os.path.join(dpath,fn)
                for l in open(fname):
                    if "templatepoint" in l:
                        touchfiles.append(fname)
                        print fname," <="
                        print l
                        break
                
    
    print "Will touch:",touchfiles
    print "Using templates:",templates
    
    
    vars = find_vars(templates)
    print "vars", vars
    itp = em.Interpreter()
    vals, _ = promptvars(vars)
    print vals
    globs = itp.getGlobals()
    globs.update(vals)
    
    for ins in templates:
        itp.include(ins)

        
    def expanded_lines(lines):
        for l in lines:            
            tp = re.search(r"templatepoint:\s*(\w+)", l)
            if not tp:
                yield l
                continue
            expname = tp.group(1)
            expf = globs[expname]
            yield expf()
            yield l
            
        return
    
    for f in touchfiles:
        lines = open(f).readlines()

        open(f,"w").writelines(expanded_lines(lines))
        
        
def main():
    global tempdir
    tempdir = "/tmp/pywiztmpl" 
    if os.path.isdir(tempdir):
        try:
            print "Erasing temp dir"
            shutil.rmtree(tempdir)
        except OSError,e:
            print "Failed to remove temp dir;", e
            return

    parser = OptionParser()
    parser.add_option('-p','--preserve-templates',action="store_true",
    help="Preserve source .em files after directory expansion",
    dest="preserve_emfiles",
    default=False)

    parser.add_option(
    '-d','--delete-templates',action="store_true",
    help="Delete source .em files after directory expansion",
    dest="delete_emfiles",
    default=False)

    parser.add_option(
    '-f','--force',action="store_true",
    help="Force overwrite of target files if any exist",
    dest="force_overwrite",
    default=False)

    parser.add_option(
    '-e','--expandhere',action="store",
    help="Expand a template here",
    dest="expandhere", default = None)
    
    parser.add_option(
    '-m','--manipulate',action="append",
    help="Manipulate files",
    dest="manipulationguide", default = None)

    global options
    (options, args) = parser.parse_args()

    global preserve_emfiles,delete_emfiles,force_overwrite
    
    preserve_emfiles = options.preserve_emfiles
    delete_emfiles = options.delete_emfiles
    force_overwrite = options.force_overwrite
    
    if options.expandhere is not None:
        expand_to_dir(options.expandhere, os.path.abspath('.'))
        return
        
    if options.manipulationguide is not None:
        if args:
            p = args
        else:
            p = [os.getcwd()]
            
        process_existing_files(p, options.manipulationguide)
        return
        
        
    elif not args:
        print __doc__
        return
    if os.path.isfile(args[0]):
        file_to_clipboard(args[0])
    elif os.path.isdir(args[0]):
        expand_tree(args[0])

def init():
    global preserve_emfiles,delete_emfiles,force_overwrite
    preserve_emfiles,delete_emfiles,force_overwrite = 0,0,0

init()  # called also when used as module
    
    
if __name__ == '__main__':
    #process_existing_files(["/t/loc"], ['/prj/pywiz/localexpansions.em'])
    main()
