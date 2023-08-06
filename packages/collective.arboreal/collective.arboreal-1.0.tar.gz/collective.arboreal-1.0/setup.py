import os
from setuptools import setup, find_packages

version = '1.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    
long_description = '\n'.join((
    read('README.txt'),
    read('CHANGES.txt')
))

setup(name='collective.arboreal',
      version=version,
      description="Arboreal is a tool which lets you manage multiple trees.",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='archetypes trees field widget index',
      author='Pareto',
      author_email='info@pareto.nl',
      url='http://pypi.python.org/pypi/collective.arboreal',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.i18n'
      ],
      )
