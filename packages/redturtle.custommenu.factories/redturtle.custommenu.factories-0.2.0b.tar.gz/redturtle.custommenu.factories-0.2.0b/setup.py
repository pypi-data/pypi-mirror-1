from setuptools import setup, find_packages
import os

version = '0.2.0b'

tests_require=['zope.testing']

setup(name='redturtle.custommenu.factories',
      version=version,
      description="Customize the Plone \"add portal content\" menu",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        ],
      keywords='plone menu factories customize',
      author='RedTurtle Technology',
      author_email='luca.fabbri@redturtle.net',
      url='http://svn.plone.org/svn/collective/redturtle.custommenu.factories',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle', 'redturtle.custommenu'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'redturtle.custommenu.factories.tests.test_doctest.test_suite',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
