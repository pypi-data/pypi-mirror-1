mediantracker.py 1.0
2009 Sep 01

Python 2 module to track the overall median of a stream of values "on-line" 
in reasonably efficient fashion.

This is a self-contained pure Python 2 module to dynamically compute the on-line
median of a series of values.  This means that as new values arrive, you can
add them to a MedianTracker and request the overall median of all values seen
so far in an efficient fashion.

For installation instructions, see the file INSTALL.

For information on using this module, see the docstrings:

    $ python
    >>> import mediantracker
    >>> help(mediantracker)
    
More information can be found at the project homepage:
http://sourceforge.net/projects/mediantracker/


This Software is Copyright (c) 2009 John Kleint

This is free software, licensed under the MIT/X11 License,
available in the accompanying LICENSE file or via the Internet at 
http://www.opensource.net/licenses/mit-license.html

