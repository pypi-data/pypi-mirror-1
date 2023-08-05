#!/usr/bin/env python

from setuptools import setup

setup(
    name="TurboEntity",
    version="0.1.0",
    url="http://turboentity.ematia.de",
    
    py_modules=["turboentity"],
    
    zip_safe=True,
    install_requires=["SQLAlchemy >= 0.2.8"],
    
    author="Daniel Haus",
    author_email="daniel.haus@ematia.de",
    
    description="Declarative layer on top of SQLAlchemy",
    license="MIT",
    download_url="http://turboentity.ematia.de/",
    keywords="sqlalchemy declarative database",
    long_description="""
TurboEntity is a declarative layer on top of SQLAlchemy,
inspired by, but somewhat "thicker" than ActiveMapper.

Features:
- automatic polymorphic inheritance
- easy specification of relationships
- automatic creation of primary keys
- automatic creation of foreign keys
- automatic creation of secondary tables
- relations can be specified across modules

Documentation and examples are located at
http://turboentity.ematia.de/
    """,

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: TurboGears",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)

