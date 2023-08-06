#!/usr/bin/python
# ^^^^^^^^^^^^^^^ This line will be changed by distutils

"""Spyke: A telepathy connection manager for skype. 

DO NOT USE THIS PROGRAM WITH SETUPTOOLS/easy_install!

This program must be installed using python setup.py install --prefix=$HOME
in order things are installed into the xdg base directory structure correctly.

This can be used with empathy in the usual way, with the restrictions that:
* The account name in empathy must match that of skype.

These restrictions will be relaxed in future releases.
"""

if __name__ == "__main__":
    import spyke
    spyke.main()