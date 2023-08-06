#!/usr/bin/python
# -*- coding: utf8 -*-
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

execfile('src/py_dumpfs/__init__.py')

setup(name='PyDumpFS',
      version=__version__,
      author='MASA.H',
      author_email='hasegawa@mapse.eng.osaka-u.ac.jp',
      url='http://www.masahase.mydns.jp/hg/PydumpFS/',
      package_dir={"": "src"},
      packages=find_packages("src"),
      scripts=['src/pdumpfs.py'],
      description="Python base pseudo plan9's dump file system",
      license="New-style BSD License",
      platforms=["Posix"],
      long_description="Python base pseudo plan9's dump file system",
      classifiers=[
#          'Development Status :: 4 - Beta',
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: Japanese',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: System :: Archiving :: Backup',
          ],
      package_data={'py_dumpfs':['locale/*/LC_MESSAGES/PyDumpFS.mo']},
      zip_safe=True,
      )
