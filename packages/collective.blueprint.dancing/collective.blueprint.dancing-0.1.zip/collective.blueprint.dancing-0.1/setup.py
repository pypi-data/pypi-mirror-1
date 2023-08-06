import os, sys

from setuptools import setup, find_packages

version = '0.1'

def read(*rnames):
    return open(
        os.path.join('.', *rnames)
    ).read()

long_description = ('\n'.join((
    read('collective', 'blueprint', 'dancing', 'README.txt'), ''
    'Detailed Documentation',
    '**********************', '',
    read('collective', 'blueprint', 'dancing', 'importsubscriber.txt'), '',
    read('docs', 'HISTORY.txt'), '',
    'Download',
    '********', ''
)))

open('doc.txt', 'w').write(long_description)

classifiers = [
    "Framework :: Plone",
    "Framework :: Zope2",
    "Programming Language :: Python",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Topic :: Software Development :: Libraries :: Python Modules",]

setup(
    name='collective.blueprint.dancing',
    namespace_packages=['collective', 'collective.blueprint',],
    version=version,
    description='collective.dancing blueprints for collective.transmogrifier pipelines',
    long_description=long_description,
    classifiers=classifiers,
    keywords='plone dancing blueprints transmogrifier',
    author='Sylvain Boureliou',
    author_email='sylvain.boureliou@makina-corpus.com',
    url='http://www.makina-corpus.com',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'collective.transmogrifier',
    ],
    # define there your console scripts
    entry_points="""
    # -*- Entry points: -*-
    """,

)
