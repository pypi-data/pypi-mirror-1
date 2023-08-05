from setuptools import setup, find_packages
pkg = find_packages()
print pkg
setup(
    name = "empywiz",
    version = "0.6",
    author = "Ville M. Vainio",
    author_email = 'vivainio@gmail.com',
    url = 'http://opensvn.csie.org/vvprj/trunk/empywiz/',
    packages = ['empywiz'],
    include_package_data = 1,
    description = 'Wizard for EmPy templates',
    long_description = """\
empywiz - Universal project wizard with empy templating system

This project is a simple system to automatically render and rename directory 
hierarchies of files, usually containing templates authored in "empy" template format.

Also rendering to clipboard is supported for simpler templating tasks.
""",
    
    entry_points = {
        'console_scripts': [
            'expandtemplate = empywiz.expandtemplate:main',
            'prjwiz = empywiz.prjwiz:guimain',
        ],
        }
    
)
