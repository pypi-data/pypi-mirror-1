import os
from setuptools import setup, find_packages

version = '0.1b6'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name='garbas.forum',
      version=version,
      description="Forum for Plone",
      long_description=('\n'.join((
              read('README.txt'), '',
              read('TODO.txt'), '',
              read('HISTORY.txt'), '',
          ))),

      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rok Garbas',
      author_email='rok.garbas@gmail.com',
      url='http://github.com/garbas/garbas.forum/tree/master',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['garbas'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.captcha',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
