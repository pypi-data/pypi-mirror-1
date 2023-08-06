from setuptools import setup, find_packages
import os

version = '0.0.2'

desc = (
    open(os.path.join('prdg', 'ploneio', 'README.txt')).read()
    + '\n' + open('HISTORY.txt').read()
)    

setup(name='prdg.ploneio',
      version=version,
      description='Provide a set of views allowing to import and export content into and from a Plone Site.',
      long_description=desc,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rafael Oliveira',
      author_email='rafaelbco@gmail.com',
      url='http://code.google.com/p/prdg-python/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['prdg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'prdg.plone.util>=0.0.5,<=0.0.99'
      ],
      entry_points='',
)
