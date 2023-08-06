martINI
=======
        
martINI is an extended facility for utilizing
`ini files <http://en.wikipedia.org/wiki/INI_file>`_ in python.
martINI includes API, command-line, and web interfaces.
martINI is built on the
`ConfigParser <http://docs.python.org/library/configparser.html>`_ module,
which is part of python's standard library.


Command Line Tools
------------------

martINI comes with several command line tools for manipulating .ini
files:

 * ini-get: get key or section values from a .ini files
 * ini-set: set .ini file values 
 * ini-delete: delete .ini key-value pairs from a .ini files
 * ini-munge: combine several .ini files 

Running the commands will display usage information.


TODO
----

Consider refactoring to use 
`INITools <http://pythonpaste.org/initools/>`_ instead of ``ConfigParser``.

--

http://k0s.org/portfolio/software.html#martini
