#! /usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
    name = "gasket",
    entry_points = {'console_scripts': ['gasket = gasket:main']},
    version = "0.1",
    url = "http://joey101.net/gasket/",
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,

    author = "Joey Marshall",
    author_email = "web@joey101.net",
    description = "Simple note taking aplication for gnome",
    license = "GPL",
    keywords = "gnome notes note simple",
    platforms = 'x11',
    long_description = """Gasket is a simple note taking program I made for gnome. I liked the simplicity of kjots for KDE and the icons in basket (also for KDE). I combined the two into one light GTK program written in 208 lines of clean python code. It still doesn't have all the features I want such as handling hyper links, but it will!

    Requires python bindings for gtk and glade to run."""
)
