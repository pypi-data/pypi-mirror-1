from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension

import sys

if sys.platform == 'darwin':
    extensions = [
        Extension("gfx.gl", ["gfx/gl.pyx"], libraries = ["GL","GLU"], 
            extra_compile_args=['-framework','OpenGL','-I','/System/Library/Frameworks/OpenGL.framework/Headers'], 
            extra_link_args=['-dynamic','-framework','OpenGL', '-L/System/Library/Frameworks/OpenGL.framework/Libraries']), 
        ]
elif sys.platform == 'win32':
    extensions = [
        Extension("gfx.gl", ["gfx/gl.pyx"], libraries = ["opengl32","glu32"],
            extra_compile_args=[])
        ]
else:
    extensions = [
        Extension("gfx.array", ["gfx/array.pyx"], libraries = ["GL","GLU"],
            extra_compile_args=['-I','/usr/include/GL']),
        Extension("gfx.gl", ["gfx/gl.pyx"], libraries = ["GL","GLU"],
            extra_compile_args=['-I','/usr/include/GL'])
        ]

packages = find_packages(exclude=['tests'])

setup(
    name = "GFX",
    version = "4",
    url="http://code.google.com/p/corsair-redux/wiki/GFX",
    ext_modules=extensions,
    packages = packages,
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='MIT',
    platforms=['Any'],
    description="Basic Textured Quads and Lines using OpenGL.",
    long_description="GFX is used for drawing quads and lines, with textures, in an OpenGL viewport. It uses Pyrex, and does not require PyOpenGL.",

)

