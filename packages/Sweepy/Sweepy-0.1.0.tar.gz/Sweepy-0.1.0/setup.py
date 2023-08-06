try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='Sweepy',
    version='0.1.0',
    description='A very basic minesweeper clone written in Pylons',
    author='Francis O Reilly',
    author_email='fran@memorista.com',
    url='http://www.memorista.com',
    install_requires=[
        "Pylons>=0.9.7",
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'sweepy': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'sweepy': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = sweepy.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Framework :: Pylons",
        "Programming Language :: Python",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],
    keywords='pylons sweepy minesweeper puzzle game demo',
    license='GNU General Public License (GPL) 3.0 or any later version',
    long_description='''\
++++++
Sweepy
++++++

This is a very simple (and ugly) implementation of the well known 
mine sweeper type game, in the Pylons framework. No extra dependencies
are needed above Pylons itself, except for easy_install.

Installation
============

Assuming you have easy_install::

    easy_install Sweepy
    paster make-config Sweepy config.ini

Running Sweepy
==============

Assuming you have permissions to run a webserver on port 80 of your
local machine::

    paster serve config.ini

The game is now available at http://localhost .

If not, you need to edit config.ini and change the port under the 
[server:main] section to a port you have permissions to use. This will
usually be a port above 1024, e.g. 8000; and in that case the game
is available at http://localhost:8000

Files
=====

    ''',

)
