from setuptools import setup, find_packages

version = '4.0b1'

setup(name='Products.statusmessages',
      version=version,
      description="statusmessages provides an easy way of handling "
                  "internationalized status messages managed via an "
                  "BrowserRequest adapter storing status messages in "
                  "client-side cookies.",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone status messages i18n',
      author='Hanno Schlichting',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/Products.statusmessages',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.component',
            'Zope2',
        ]
      ),
      install_requires=[
        'setuptools',
        'zope.annotation',
        'zope.i18n',
        'zope.interface',
      ],
)
