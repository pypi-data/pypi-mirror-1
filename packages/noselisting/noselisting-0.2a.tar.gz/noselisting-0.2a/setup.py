#!/usr/bin/env python

from setuptools import setup

setup(
    name="noselisting",
    version="0.2a",
    download_url = "http://pypi.python.org/pypi/noselisting/",
    description = "Plugin for the nose testing framework to list tests "
                  "without running them",
    author = "John J. Lee",
    author_email = "jjl@pobox.com",
    license = "BSD",
    platforms = ["any"],
    install_requires = ["nose>=0.10.0, ==dev"],
    url = "http://pypi.python.org/pypi/noselisting/",
    long_description = """\
Plugin for the nose testing framework to list tests without running them.

Use ``nosetests --list-test-names`` to get a listing.

``nosetests --list-long-test-names`` gives a listing with long names that can
be used as arguments to ``nosetests``.
""",
    py_modules = ["noselisting"],
    entry_points = {
        "nose.plugins.0.10": ["noselisting = noselisting:TestListingPlugin"]},
    zip_safe = True,
)
