from setuptools import setup
from setuptools import find_packages
import sys
version = '1.0.4'

install_requires = [
    'setuptools',
    'Chameleon>=1.0.1',
    ]

if sys.version_info[:3] < (2,5,0):
    install_requires.append('elementtree')

setup(name='chameleon.core',
      version=version,
      description="Attribute language template compiler",
      long_description=open("README.txt").read() + open("CHANGES.txt").read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Malthe Borch and the Zope Community',
      author_email='zope-dev@zope.org',
      url='',
      license='BSD',
      namespace_packages=['chameleon'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      )
