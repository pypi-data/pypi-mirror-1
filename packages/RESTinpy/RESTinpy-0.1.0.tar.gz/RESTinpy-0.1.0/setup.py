# -*- coding: utf-8 -*-
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
      name='RESTinpy',
      version='0.1.0',
      description='Python library to publicate REST-style web services in Django applications',
      long_description = 'A Python library to ease the publication of REST-style web services in Django applications, specially (but not exclusively) those using the Django Model framework.',
      license = 'GNU Library or Lesser General Public License (LGPL) v3', #Should be removed by PEP  314
      #author='Diego Berrueta, Jana Álvarez, Sergio Fernández, Carlos Tejo Alonso', # Error in python 2.5. Fixed in rev.66181 of python http://svn.python.org/view?view=rev&revision=66181
      author='Diego Berrueta, Jana Alvarez, Sergio Fernandez, Carlos Tejo Alonso',
      author_email='diego.berrueta at fundacionctic org, jana.alvarez at fundacionctic org, sergio.fernandez at fundacionctic org, carlos.tejo at fundacionctic org',
      #maintainer=u'Diego Berrueta', #Not in PEP  314, 241.
      #maintainer_email='diego.berrueta at fundacionctic org', #Not in PEP  314, 241
      url = 'http://rest-in-py.sourceforge.net/',
      download_url = 'https://sourceforge.net/project/downloading.php?group_id=255808&filename=RESTinpy-0.1.0.tar.gz&a=94759195',
      platforms = ['any'], #Should be removed by PEP  314
      packages=['RESTinpy'],
      requires=['simplejson', 'mimeparse', 'django'], # Used by distutils to create metadata PKG-INFO
      install_requires=['simplejson == 2.0.9', 'mimeparse == 0.1.2', 'django == 1.0.2-final'], #Used by setuptools to install the dependencies
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
      ],
      keywords = 'python REST',
      requires_python= '>=2.5', # Future in PEP 345
      scripts = ['ez_setup.py'],
)
