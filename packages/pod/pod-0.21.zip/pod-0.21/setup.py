import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "pod",
    version = "0.21",
    author = "Andrew Carter, et al",
    author_email = "andrewjcarter@gmail.com",
    description = "An Object Database Management System (ODBMS) for Python built on cPickle and sqlite -- An easy way to store and fetch Python objects",
    license = "BSD",
    keywords = "python object database pickle persistent persistence object relational mapper ODBMS ORM",
    url = "http://code.google.com/p/pickled-object-database/",   # project home page, if any
    packages     = find_packages(),
    long_description = "The 0.21 release fixes a bug in the 0.2 release that affected Python 2.5"
)
