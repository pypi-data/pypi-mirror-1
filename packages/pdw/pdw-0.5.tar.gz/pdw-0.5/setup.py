try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys
sys.path.insert(0, '.')
from pdw import __version__, __doc__ as __long_description__

setup(
    name='pdw',
    version=__version__,

    # general metadata
    description='Public Domain Works Database Code and Web Application.',
    long_description=__long_description__,
    license='GPL',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://www.publicdomainworks.net/',
    download_url='http://knowledgeforge.net/pdw/hg',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'pdw': ['i18n/*/LC_MESSAGES/*.mo']},
    scripts=['bin/pdw-admin'],
    install_requires=[
        'Pylons>=0.9.6,<0.9.6.99',
        'SQLAlchemy>=0.4.8,<0.4.99',
        'Genshi>=0.4,<0.5.99',
        'python-dateutil',
        'pymarc',
        'swiss',
        ],
    extras_require = {
        # BL SA
        'scraper' : ['mechanize>=0.1'],
        # NB: (2007-03-25) please use the code in subversion as we need the
        # very latest changes made n r8781 (post release 0.4.1) which
        # introduced support for count and offset on query results, and support
        # for query and limit argument on filters) 
        'musicbrainz' : ['python-musicbrainz2>0.4.1'],
        },
    paster_plugins=[
        'pdw',
        'Pylons',
        'WebHelpers',
        'PasteScript',
        ],

    #message_extractors = {'pdw': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = pdw.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [paste.paster_command]
    db = pdw.cli:Db
    load = pdw.cli:Load
    stats = pdw.cli:Stats
    consolidate = pdw.cli:Consolidate
    """,
)
