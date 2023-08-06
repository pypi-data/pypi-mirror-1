import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "pod",
    version = "0.40",
    author = "Andrew Carter, et al",
    author_email = "andrewjcarter@gmail.com",
    description = "A Python Object Database Implemented Using cPickle and SQLite - An easy way to store and fetch Python objects",
    license = "BSD",
    keywords = "python object database pickle persistent persistence object relational mapper ODBMS ORM",
    url = "http://code.google.com/p/pickled-object-database/",   # project home page, if any
    packages     = find_packages(),
    long_description = "The 0.40 release introduces major changes to the basic working and philosophy of pod and is not backward compatible.", 
    )