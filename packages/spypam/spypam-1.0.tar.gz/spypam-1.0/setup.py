#!/usr/bin/env python
from distutils.core import setup, Extension

setup(name="spypam", version="1.0", author="Ludvig Ericson",
    author_email="ludvig.ericson@gmail.com",
    ext_modules=[Extension("_spypam", ["spypammodule.c"], libraries=["pam"])],
    py_modules=["spypam"])
