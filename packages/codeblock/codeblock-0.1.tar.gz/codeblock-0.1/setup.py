"""Syntax-highlighted code blocks for docutils plugin for zc.rst2

This is a wrapping of the Python Recipe:

  Syntax-highlighted code blocks for docutils

for zc.rst2, http://www.python.org/pypi/zc.rst2

"""

from setuptools import setup

entry_points = """
[rst.directive]
code-block = codeblock:code_block
"""

name='codeblock'
setup(
    name=name,
    version = "0.1",
    author = "Kevin Schluff (packaged by Jim Fulton)",
    description = "Syntax-highlighted code blocks for docutils",
    long_description=__doc__,
    license = "Python Cookbook code is freely available for use and review.",
    url='http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252170',
    
    py_modules=['codeblock'],
    entry_points=entry_points,
    install_requires='SilverCity',
    zip_safe=False,
    )

    
