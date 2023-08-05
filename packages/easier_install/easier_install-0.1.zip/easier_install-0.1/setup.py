from setuptools import setup
setup(
    name = 'easier_install',
    version = "0.1",
    author = "Ville M. Vainio",
    author_email = 'vivainio@gmail.com',
    url = 'http://opensvn.csie.org/vvprj/trunk/easier_install/',
    license = 'MIT Open Source License',
    py_modules = [
 'easier_install',
],
    description = 'Create setup.py files for a number of modules and scripts quickly',
    long_description = """ Easily create setup.py files for easy_install / setuptools 

I'm too lazy to author setup.py files for installation of simple python modules 
and scripts, and setuptools/easy_install is very handy for installing scripts
"properly" on both win32 and unix. Hence this script for creating a functional
setup.py quickly. It's perfectly usable for creating source and binary distributions 
as well.

Quick guide:

- Go to a directory with lots of python modules (no packages!).
- If the directory name is /home/foo/bar, 'bar' will be used as the name of 
  the distribution.
- If a python module has 'def main' in it, it's considered executable
- Run easier_install
- Review the resulting ei_setup.py and run it, as instructed.

""",
    
    entry_points = {
        'console_scripts': [
 'easier_install = easier_install:main',                            
                
        ],
        }
    
)
