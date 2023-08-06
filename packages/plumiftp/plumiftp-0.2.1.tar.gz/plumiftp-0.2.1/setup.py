from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(name='plumiftp',
      version=version,
      description="resumable large video FTP uploads, wrapped around Zope FTP server",
      long_description="""\
Large video files uploads , designed for use in Plumi video Plone CMS""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='video zope plone ftp',
      author='Andy Nicholson',
      author_email='andy@engagemedia.org',
      url='http://plumi.org/',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
	'pyftpdlib',
      ],
      entry_points={
	 'console_scripts': [
		    'plumiftp = plumiftp.zope_ftpd:plumiftp_wrapper',
	],
	}
      )
