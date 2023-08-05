from setuptools import setup, find_packages
pkg = find_packages()
print pkg
setup(
    name = "empywiz",
    version = "0.5",
    author = "Ville M. Vainio",
    author_email = 'vivainio@gmail.com',
    url = 'http://opensvn.csie.org/vvprj/trunk/empywiz/',
    packages = ['empywiz'],
    include_package_data = 1,
    description = 'Wizard for EmPy templates',
    entry_points = {
        'console_scripts': [
            'expandtemplate = empywiz.expandtemplate:main',
            'prjwiz = empywiz.prjwiz:guimain',
        ],
        }
    
)
