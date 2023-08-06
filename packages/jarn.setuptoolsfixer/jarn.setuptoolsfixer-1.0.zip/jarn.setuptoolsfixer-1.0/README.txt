Introduction
============

This package is a zc.buildout extension which fixes a bug in setuptools which
makes it fail when the homepage or download url on a PyPI page is broken. If
the egg is stored on PyPI then this fix allows buildout to continue.