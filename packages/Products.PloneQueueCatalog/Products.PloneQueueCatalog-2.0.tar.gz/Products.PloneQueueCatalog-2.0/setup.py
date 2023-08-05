from setuptools import setup, find_packages
import sys, os

version = '2.0'

setup(name='Products.PloneQueueCatalog',
      version=version,
      description="Products.PloneQueueCatalog makes it easier to use "
                  "QueueCatalog in your Plone site.",
      long_description="""\
      """,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
      ],
      keywords='Plone QueueCatalog',
      author='Helge Tesdal',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/collective/PloneQueueCatalog/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
)
