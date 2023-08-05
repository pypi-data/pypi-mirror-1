from setuptools import setup, find_packages
import sys, os

version = '3.0rc1'

setup(name='Products.statusmessages',
      version=version,
      description="statusmessages provides an easy way of handling "
                  "internationalized status messages managed via an "
                  "BrowserRequest adapter storing status messages in "
                  "client-side cookies. It requires Zope >= 2.10.",
      long_description="""\
      """,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone status messages i18n',
      author='Hanno Schlichting',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/collective/statusmessages/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      download_url='http://plone.org/products/statusmessages/releases',
      install_requires=[
        'setuptools',
      ],
)
