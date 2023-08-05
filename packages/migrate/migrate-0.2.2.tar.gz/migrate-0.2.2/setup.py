#!/usr/bin/python
from setuptools import setup,find_packages

# Pudge
try:
    import buildutils
except ImportError:
    pass

setup(
    name = "migrate",
    version = "0.2.2",
    packages = find_packages(exclude=['test*']),
    scripts = ['shell/migrate'],
    include_package_data = True,
    description = "Database schema migration for SQLAlchemy",
    long_description = """
Inspired by Ruby on Rails' migrations, Migrate provides a way to deal with database schema changes in `SQLAlchemy <http://sqlalchemy.org>`_ projects.
""",

    install_requires = ['sqlalchemy >= 0.3.0dev'],
    setup_requires = ['py >= 0.8.0-alpha2'],

    author = "Evan Rosson",
    author_email = "evan.rosson@gmail.com",
    url = "http://erosson.com/migrate",
    license = "MIT",

    test_suite = "py.test.cmdline.main",
)
