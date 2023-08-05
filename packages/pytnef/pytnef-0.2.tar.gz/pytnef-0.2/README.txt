This package contains:

- a wrapper to the unix tnef command-line tool (using Python 2.4 subprocess module); see http://tnef.sourceforge.net

- conversion of a Ruby tnef library (in turn based on a C version) to Python; see the lib directory of the package

Since interfacing with the unix command does all I need, the pure-Python library has not received any effort. Nor will I have time to work on it. Feel free to pick up the code. Another nice option would be adding some code to interface with for example the ytnef library.