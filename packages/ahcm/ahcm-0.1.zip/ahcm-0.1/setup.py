
from setuptools import setup
setup(
    name = 'ahcm',
    version = "0.1",
    author = "Ville M. Vainio",
    author_email = 'vivainio@gmail.com',
    url = 'http://vvtools.googlecode.com/svn/trunk/ahcm#egg=ahcm-dev',
    py_modules = [
 'ahcm',
 'mglob',
 'path',
],
    description = 'ahcm - ad hoc configuration management tool',
    long_description = """\
ahcm apply mypatch /prj/foo
ahcm apply blah.txt foo.txt /prj/foo

- Copy all files under directory mypatch over corresponding files in 
/prj/foo. Do the same for blah.txt and foo.txt 
If file doesn't exist under target dir, it's NOT created.

Also other simple but handy "dirty" CM operations are supported for those unmanaged situations. ;-)
""",
    
    entry_points = {
        'console_scripts': [
 'ahcm = ahcm:main',
 'mglob = mglob:main',                            
                
        ],
        }
    
)
