#!/usr/bin/env python

from setuptools import setup

setup(
    name='mulib',
    version='0.2',
    description='REST web service framework',
    author='Linden Lab',
    author_email='eventletdev@lists.secondlife.com',
    url='http://wiki.secondlife.com/wiki/Mulib',
    packages=['mulib'],
    install_requires=['eventlet', 'simplejson'],
    long_description="""
    Mulib is a REST web service framework built on top of
    eventlet.httpd. Httpd parses incoming HTTP request and generates
    the response; mulib takes care of locating the object which will
    handle the request (url traversal) and calling the appropriate
    callback method based on the method of the request. Code written
    using mulib looks like a series of subclasses of mu.Resource which
    override methods such as handle_get or handle_post, making it easy
    to implement web services.

    The stacked traversal code also knows how to traverse python
    objects like dicts and lists. Using that style, it is possible to
    easily interact with compositional data structures through the
    Web.""",
    classifiers=[
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Intended Audience :: Developers",
    "Development Status :: 4 - Beta"]
    )

