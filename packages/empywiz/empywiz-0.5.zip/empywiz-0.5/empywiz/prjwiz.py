#!/usr/bin/env python2.3
"""\
Universal project wizard
------------------------

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

"""

__revision__ = '$LastChangedRevision: 44 $'
__date__    =  '$LastChangedDate: 2003-11-07 22:17:46 +0200 (Fri, 07 Nov 2003) $'
__url__     =  'http://www.students.tut.fi/~vainio24'
__author__  =  'Ville Vainio <ville.nospamvainio@spammehardtut.fi>'
__copyright__= 'Copyright (C) 2003 Ville Vainio'
__license__ =  'BSD'


import sys,os
import shutil
from Tkinter import *
from tkMessageBox import *
import tkFileDialog
import expandtemplate
import empywizcfg as conf


def choicelist(choices):
    for i,choice in enumerate(choices):
        print "%2d. %s" % (i, choice)
    while 1:
        ch = raw_input("Your choice: ")
        try:
            n = int(ch)
            return choices[n]
        except:pass
        
def expandtemplatenow(template):
    while 1:
        targetdir = tkFileDialog.askdirectory(initialdir = "c:/",
                                              title="Where should the project '%s' be created?" % template)
        
        if not targetdir:
            return
        if os.path.exists(targetdir) or not targetdir:
            showerror("Path exists","The directory must not exist! Enter a new name for the directory!")
        else:
            break

        
    tmplpath = os.path.join(conf.project_templates_dir,template)
    shutil.copytree(tmplpath, targetdir)
    expandtemplate.expand_tree(targetdir)
    showinfo("Done","Expansion complete.")
    
    
class ScrolledList(Frame):
    """ stole this from Programming Python, 2nd ed, Mark Lutz, ISBN: 0-596-00085-5 """

    def __init__(self, options, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)                  # make me expandable
        self.makeWidgets(options)
    def handleList(self, event):
        index = self.listbox.curselection()               # on list double-click
        label = self.listbox.get(index)                   # fetch selection text
        self.runCommand(label)                            # and call action here

    def makeWidgets(self, options):                       # or get(ACTIVE)
        sbar = Scrollbar(self)
        list = Listbox(self, relief=SUNKEN)
        sbar.config(command=list.yview)                   # xlink sbar and list
        list.config(yscrollcommand=sbar.set)              # move one moves other
        sbar.pack(side=RIGHT, fill=Y)                     # pack first=clip last
        list.pack(side=LEFT, expand=YES, fill=BOTH)       # list clipped first
        pos = 0
        for label in options:                             # add to list-box
            list.insert(pos, label)                       # or insert(END,label)
            pos = pos + 1

        list.bind('<Double-1>', self.handleList)          # set event handler
        self.listbox = list

    def runCommand(self, selection):                      # redefine me lower
        expandtemplatenow(selection)

def guimain():
    os.chdir(conf.project_templates_dir)
    projects = [ d for d in os.listdir(conf.project_templates_dir) if os.path.isdir(d)]
    sl = ScrolledList(projects)
    sl.mainloop()

    

if __name__ == '__main__':
    guimain()
    
    
