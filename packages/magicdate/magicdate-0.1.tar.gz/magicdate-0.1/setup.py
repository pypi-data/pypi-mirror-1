RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.1'

setup(name='magicdate',
      version=version,
      description="Convert fuzzy date to a datetime object.",
      long_description="""\
Description will come soon, sorry.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='datetime time',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://dealmeida.net/projects/magicdate',
      download_url = "http://cheeseshop.python.org/packages/source/m/magicdate/magicdate-%s.tar.gz" % version,
      license='MIT',
      py_modules=['magicdate'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
