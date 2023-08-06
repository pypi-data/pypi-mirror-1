import os
from setuptools import setup, find_packages

setup(
    name='collective.anonymousbrowser',
    version="0.2",
    description='A zope.testbrowser extension with useragent faking and proxy abilities',
    license='GPL',
    url="https://svn.plone.org/svn/collective/collective.anonymousbrowser/trunk",
    long_description='\n'.join(
        open(os.path.join(*path)).read() for path in [
            ("README.txt",),
            ("collective", "anonymousbrowser", "tests", "browser.txt",),
            ("docs", "HISTORY.txt")]),
    author='Mathieu Pasquet',
    author_email='kiorky@cryptelium.net',
    #url='',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    extras_require={'test': ['IPython', 'zope.testing', 'mocker']},
    install_requires=[
        'lxml',
        'mechanize',
        'setuptools',
        'zope.testbrowser',
    ],
)
