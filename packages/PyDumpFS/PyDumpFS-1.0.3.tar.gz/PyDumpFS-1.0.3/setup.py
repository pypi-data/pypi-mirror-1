from distutils.core import setup
f=open("README")
desc=unicode(f.read(),"utf8")
f.close()
setup(name='PyDumpFS',
      version='1.0.3',
      author='MASA.H',
      author_email='hasegawa@mapse.eng.osaka-u.ac.jp',
      url='http://www.masahase.mydns.jp/hg/PydumpFS/',
      scripts=['src/pdumpfs.py'],
      description="Python base pseudo dump file system",
      license="New-style BSD Lecense",
      platforms=["Posix"],
      #long_description=desc,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: Japanese',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: System :: Archiving :: Backup',
          ],
      )
