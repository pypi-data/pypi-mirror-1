from setuptools import setup, find_packages
import sys

version = '0.3'

install_requires = [
    'setuptools',
    'zope.interface',
    'zope.component',
    'zope.i18n >= 3.5',
    'chameleon.core',
    'cssutils',
    'lxml >= 2.1.1',
    ]

setup(name='chameleon.html',
      version=version,
      description="Dynamic HTML template compiler with XSS language support.",
      long_description=open("README.txt").read(),
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
