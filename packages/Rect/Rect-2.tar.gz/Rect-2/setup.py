from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension

packages = find_packages()

setup(
    name = "Rect",
    version = "2",
    url="http://code.google.com/p/corsair-redux/wiki/Rect",
    packages = packages,
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='MIT',
    platforms=['Any'],
    description="A class for handling rectangle regions.",
    long_description="""The Rect class is similar to the pygame.Rect class, except it works with
float precision in a left handed coordinate system.

The rect package also provides a spatial index and a rect packing function.

Changes:
20070717: Added QuadTree spatial index. (rect.quadtree)
20070718: Added rect packing algorithm. (rect.packer)
"""
)

