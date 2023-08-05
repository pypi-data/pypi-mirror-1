empywiz
-------

(Note that this project was formerly known as pywiz).

This project is a simple system to automatically render directory hierarchies of 
files, possibly containing templates authored in "empy" template format.
(http://www.alcyone.com/pyos/empy/). 
empy is included in this project.

You might want to edit empywizcfg.py before doing anything.

Running expandtemplate.py on this directory will create sample1.txt,
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

Docstrings:

prjwiz - Universal project wizard
---------------------------------

Usage:

Put all your templates in one directory. Modify the
project_templates_dir in pywizconfig.py to match the
directory.

Note that 'template' here means a directory, with arbitrary number of
files and subdirectories. The directory is expanded as described in
the documentation of expandtemplate.py

This is basically just a GUI frontend to the directory expansion mode
of expandtemplate.py. The template you choose (by 2-clicking on the
name) will be copied to the directory you choose and expanded. The
prompting will me made on the text console, just like with
expandtemplate.py.

See expandtemplate.py for license, version info etc.

Below you can see some screenshots about prjwiz in action

User has selected a template, and is being prompted for target directory:

.. image:: screenshot1.jpg

Target directory has been selected, variables have been prompted and
the user is asked whether he wants to commit the template expansion:

.. image:: screenshot2.jpg


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
