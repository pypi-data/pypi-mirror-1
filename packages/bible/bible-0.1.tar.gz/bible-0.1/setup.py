from distutils.core import setup
setup(
    name = "bible",
    packages = ["bible"],
    version = "0.1",
    description = "Bible reference classes",
    author = "Jason Ford",
    author_email = "jason@jason-ford.com",
    url = "http://github.com/jasford/python-bible",
    keywords = ["encoding", "i18n", "xml"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Religion",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description = """\
Classes for Bible references: Verse and Passage
-----------------------------------------------

This module lets you interact with Bible verses and passages as Python
objects. It is useful for manipulating, comparing, formatting, and saving
Bible references.

"""
)