""" Easily create setup.py files for easy_install / setuptools 

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

"""
import glob,os,sys,string

template = string.Template('''
from setuptools import setup
setup(
    name = '$name',
    version = "0.1",
    author = "Ville M. Vainio",
    author_email = 'vivainio@gmail.com',
    url = 'http://opensvn.csie.org/vvprj/trunk/easier_install',
    py_modules = [
$modules
],
    description = 'Has modules: $allmods',
    long_description = """\
An easier_install distribution with following python modules:

$allmods 

And the following scripts (exacutables):

$allscripts


""",
    
    entry_points = {
        'console_scripts': [
$consolescripts                            
                
        ],
        }
    
)
''')

def main():
    scripts = []
    mods = []
    for pyfile in glob.glob('*.py'):
        print "scanning",pyfile
        if 'setup' in pyfile:
            print "skipping, file name has 'setup' in it"
            continue
        
        cont = open(pyfile).read()
        mname = os.path.splitext(pyfile)[0]
        mods.append(mname)
        if 'def main()' in cont:
            print "def main() found, it's probably a script!"
            scripts.append(mname)
    
    cslines = '\n'.join([" '%s = %s:main'," % (m, m) for m in scripts])
    mlines = '\n'.join( " '%s'," % m for m in mods)
    mname = os.path.split(os.getcwd())[1]
    
    out = template.substitute( 
        name = mname, consolescripts = cslines, modules = mlines, 
        allmods = ', '.join(mods),
        allscripts = ', '.join(scripts))
                               
    
    print out
    assert not os.path.exists('ei_setup.py')
    open ('ei_setup.py','w').write(out)
    print "Emitted ei_setup.py. Now run the following command to install:"
    print "python ei_setup.py install"
    

if __name__ == '__main__':
    main()