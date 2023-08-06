from setuptools import setup, find_packages
import os
import sys

version = '0.3'

site_lisp = os.path.join('site-lisp')
mailsync_gnus_el = os.path.join('site-lisp', 'rpatterson-gmail.el')
if 'install' in sys.argv:
    sys_site_lisp = os.path.join(
        '/usr', 'local', 'share', 'emacs', site_lisp)
    if os.path.isdir(sys_site_lisp):
        site_lisp = sys_site_lisp
data_files = [(site_lisp, [mailsync_gnus_el])]

setup(name='bbdb.gmailfilter',
      version=version,
      description="Export BBDB contacts to gmail filter import XML",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/bbdb.gmailfilter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bbdb'],
      include_package_data=True,
      data_files=data_files,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zope.pagetemplate',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      bbdb2gfilter = bbdb.gmailfilter.export:main
      """,
      )
