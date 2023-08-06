import texttree

from distutils.core import setup
setup(name='texttree',
    version='1.0.4',
    description="Parse textual representations of strings using indentation for nesting",
    long_description="""
texttree is a basic python module for parsing textual representations of trees
of strings which use indentation to indicate nesting - like the following:

        Root
             non-leaf
                 leaf1
                  leaf2
             leaf3
""",
    author='Tom Wright',
    author_email="tat.wright@googlemail.com",
    url="http://tat.wright.name/texttree/",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Utilities"],
    py_modules=['texttree'])
