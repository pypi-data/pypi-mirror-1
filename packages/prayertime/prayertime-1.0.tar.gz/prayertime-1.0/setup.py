#!/usr/bin/env python

from distutils.core import setup, Extension


prayertime_module = Extension('prayertime/_prayertime',
                           sources=['prayertime_wrap.cxx', 'prayertime.cpp'],
                           swig_opts=['-c++'],
                           )

setup (name = 'prayertime',
       version = '1.0',
       author = "Ahmed Youssef",
       author_email="xmonader@gmail.com",
       description='prayertime for Python',
       url="http://programming-fr34ks.net",
       license="GPL v2",
       ext_modules = [prayertime_module],
       packages=['prayertime'],
       classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: C++',
          ],
       )
