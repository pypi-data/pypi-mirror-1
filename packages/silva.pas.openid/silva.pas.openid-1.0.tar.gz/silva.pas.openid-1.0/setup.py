# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: setup.py 28864 2008-05-27 10:08:20Z sylvain $

from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='silva.pas.openid',
      version=version,
      description="OpenID suport for Silva",
      long_description= open('README.txt').read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='pas openid silva',
      author='Sylvain Viollon',
      author_email='info@infrae.com',
      url='http://svn.infrae.com/silva.pas.openid/trunk',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva', 'silva.pas'],
      include_package_data=True,
      zip_safe=False,
      install_requires=["python-openid >= 2.1",
                        "silva.pas.base",
                        "silva.pas.membership",
                        "silva.captcha",
                        "plone.session",
                        "elementtree",
                        "setuptools"],
      )

