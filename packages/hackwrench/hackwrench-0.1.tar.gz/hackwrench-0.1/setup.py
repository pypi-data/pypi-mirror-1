#!/usr/bin/env python
# coding: utf-8
# vim: ai ts=4 sts=4 et sw=4

from setuptools import setup, find_packages
from glob import glob
#try:
#    from DistUtilsExtra.command import *
#    import bdist_debian
#    deb_args = dict(
#        bdist_debian = bdist_debian.bdist_debian
#        section = 'X11',
#        depends = 'python-gtk2, python-glade2, python-gtkhtml2, python-magic, pygtkimageview',
#        maintainer = 'pawnhearts',
#        maintainer_email = 'pawn13@gmail.com',
#        icon = 'fap.png',
#        #platforms='All',
#    )
#except ImportError:
#    deb_args = {}

setup(name = 'hackwrench',
    version = '0.1',
    description = 'web browser based on python-webkitgtk',
    long_description="""web browser based on python-webkitgtk
    Features:

    - reorderable tabs on top of window(like chrome)
    - python console
    - search from address bar
    - external download manager
    - gtkbuilder interface(defined in xml)
    - autocomplete addresses from history
    - sort-of speed dial
    - storing configuration in gconf
    - favicons; cached
    - userscripts
    """,
    author = 'Mikhail Sakhno',
    author_email = 'pawn13@gmail.com',
    url = 'http://tabed.org/software/hackwrench/',
    classifiers=[
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python',
    ],
    packages = ['hackwrench'],
    package_data = {'hackwrench': sum(map(glob, ['hackwrench/*png','hackwrench/*jpg','hackwrench/*html','hackwrench/*ui','hackwrench/*js']),[])},
    scripts = ['bin/hw'],
    include_package_data = True,
    data_files = [
        #('/usr/share/applications', ['hackwrench.desktop']),
        #('/usr/share/pixmaps', ['hackwrench/hackwrench.png']),
    ],
)
      



