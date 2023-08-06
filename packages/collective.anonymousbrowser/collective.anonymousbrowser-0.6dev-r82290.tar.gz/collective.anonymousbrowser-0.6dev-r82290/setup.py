import os
from setuptools import setup, find_packages

setup(
    name='collective.anonymousbrowser',
    version="0.6",
    description='A zope.testbrowser extension with useragent faking and proxy abilities',
    license='GPL',
    url="https://svn.plone.org/svn/collective/collective.anonymousbrowser/trunk",
    long_description='\n'.join(
        open(os.path.join(*path)).read() for path in [
            ("README.txt",),
            ("src", "collective", "anonymousbrowser", "tests", "browser.txt",),
            ("docs", "HISTORY.txt")]),
    author='Mathieu Pasquet',
    author_email='kiorky@cryptelium.net',
    #url='',
    namespace_packages=['collective'],
    include_package_data=True,
    extras_require={'test': ['IPython', 'zope.testing', 'mocker']},
    install_requires=[
        'lxml',
        'mechanize',
        'setuptools',
        'mozrunner',
        'zc.testbrowser',
    ],
    packages=find_packages('src'),
    package_dir = {'': 'src'}, 
)
