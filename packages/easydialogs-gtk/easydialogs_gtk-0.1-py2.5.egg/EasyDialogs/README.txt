EasyDialogs for Linux version 0.1

To Install
----------
	1) cd ti this directory
	2) run python setup.py install
		or
	   run sudo python setup.py install
 

Documentation for the Macintosh version can be found at:

http://www.python.org/doc/current/mac/module-EasyDialogs.html


Prerequisites
EasyDialogs for Linux requires a Python 2.5, and
gtk2.0,pygtk2.0 or newer.

Example usage:
import EasyDialogs

EasyDialogs .Message("Testing EasyDialogs.") # displays a message box

filename = EasyDialogs.AskFileForOpen() # presents a standard file-open dialog

# display a progress bar
bar = EasyDialogs.ProgressBar(maxval=100)
for i in range(100):
    bar.inc()
del bar
