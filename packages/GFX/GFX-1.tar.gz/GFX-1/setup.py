from ez_setup import use_setuptools
use_setuptools()

import sys
from setuptools import setup, find_packages
import setuptools

if sys.platform == 'darwin':
    extensions = [
        setuptools.Extension("gfx.gl", ["gfx/gl.pyx"], libraries = ["GL","GLU"], 
            extra_compile_args=['-framework','OpenGL','-I','/System/Library/Frameworks/OpenGL.framework/Headers'], 
            extra_link_args=['-dynamic','-framework','OpenGL', '-L/System/Library/Frameworks/OpenGL.framework/Libraries']), 
        ]
else:
    extensions = [
        setuptools.Extension("gfx.gl", ["gfx/gl.pyx"], libraries = ["GL","GLU"],
            extra_compile_args=['-I','/usr/include/GL'])
        ]

packages = find_packages()

setup(
    name = "GFX",
    version = "1",
    url="http://code.google.com/p/corsair-redux/wiki/GFX",
    ext_modules=extensions,
    packages = packages,
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='MIT',
    platforms=['Any'],
    description="Basic Textured Quads and Lines using OpenGL.",
    long_description="GFX is used for drawing quads and lines, with textures, in an OpenGL viewport. It uses Pyrex, and does not require PyOpenGL."
)

