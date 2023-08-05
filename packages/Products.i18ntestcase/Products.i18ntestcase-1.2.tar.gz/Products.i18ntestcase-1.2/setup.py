from setuptools import setup, find_packages
import sys, os

version = '1.2'

setup(name='Products.i18ntestcase',
      version=version,
      description="Products.i18ntestcase is build on top of the ZopeTestCase "
                  "package. It has been developed to simplify testing of "
                  "gettext i18n files for Zope products.",
      long_description="""\
      """,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
      ],
      keywords='Plone i18n gettext testcase',
      author='Hanno Schlichting',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/collective/Products.i18ntestcase/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
)
