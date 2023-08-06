from distutils.core import setup
from subprocess import Popen, PIPE

setup(name="pywhich",
      version="1.0.1",
      description="Find path to python modules from the command line.",
      long_description=Popen("./pywhich", stdout=PIPE).communicate()[0],
      author='Tom Wright',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python',
          'License :: OSI Approved :: BSD License',
          'Topic :: Utilities'],
      author_email='tat.wright@googlemail.com',
      url='http://pypi.python.org/pypi/pywhich',
      scripts=["pywhich"])
