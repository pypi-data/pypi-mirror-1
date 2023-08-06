import os
from distutils.core import setup
from distutils.extension import Extension

try:
    dia_dir = os.environ["DIA"]
except KeyError:
    print "Set DIA environment variable to point to your DIA installation"
    raise SystemExit
if dia_dir[0]=='"':
    dia_dir = dia_dir[1:-1]

classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: Academic Free License (AFL)
Programming Language :: Python
Programming Language :: C++
Topic :: Software Development :: Debuggers
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Microsoft :: Windows
"""

setup(name="pydia",
      version="1.0",
      description="Microsoft DIA (Debug Interface Access) Wrapper Module",
      long_description=open("README.txt").read(),
      url="http://pypi.python.org/pypi/pydia",
      license='Academic Free License ("AFL") v. 3.0',
      author="Martin v. Loewis",
      author_email="martin@v.loewis.de",
      ext_modules=[Extension('dia', ['diamodule.cpp'],
                             include_dirs = [dia_dir+"\\Include"],
                             library_dirs = [dia_dir+"\\Lib"])],
      scripts=['diademo.py'],
      classifiers = filter(None, classifiers.split("\n"))
      )
      
