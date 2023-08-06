from distutils.core import setup
#from setuptools import setup

from types import ModuleType
script = ModuleType("rst2odp")
exec open("bin/rst2odp") in script.__dict__

setup(name="rst2odp",
      version=script.__version__,
      author=script.__author__,
      author_email=script.__email__,
      description="Converter for rst to OpenOffice Impress",
      long_description='''Packacking of rst2odp and opdlib from docutils sandbox.  odplib is a standalone library for creating odp output from python.  rst2odp wraps it for rst users''',
      license='Apache',
      scripts=["bin/rst2odp"],
      package_dir={"odplib":"odplib"},
      package_data={'odplib':['data/*.xml']},
      packages=['odplib'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Office/Business'
        ]
)
           
