import os
from setuptools import setup, find_packages

version = '0.1.1'

long_description = os.path.join('iw', 'subscriber', 'docs', 'README.txt')

setup(name='iw.subscriber',
      version=version,
      description="This package allow Plone users to subscribe to contents. "
      "Then they will be notified on all creation/modification on this "
      "contents.",
      long_description=open(long_description).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='https://ingeniweb.svn.sourceforge.net/svnroot/ingeniweb/iw.subscriber',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.datetimewidgets',
          'iw.email>0.2',
      ],
      dependency_links=[
          'http://products.ingeniweb.com/catalog/simple',
      ],
      )

