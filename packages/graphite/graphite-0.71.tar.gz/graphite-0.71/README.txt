Graphite  (v0.69)
================
This directory contains an release of Graphite, an open-source,
Python graphing/plotting package.
It contains a library and two command-line applications that will
let you make line plots and scatter plots.

It's still in 
development, which means three things: 
1. Many planned features are not yet implemented.
2. Many implemented features are not yet as easy to use as we'd like.
3. Some implemented features have bugs.
4. Documentation is mostly missing.

However, it also means:

5. It runs and can make cool graphs, and you can have fun playing with it now.

The point of releasing it at this stage is that, as an open source
project, we'd like to get as many people hacking on it as possible.  We
feel it's far enough along to give you a credible promise of greatness, a
promise we can easily achieve with your in put and assistance. 

But, documentation is sparse, and test cases are too few.
Using it as a library (as opposed to the supplied script) will require a bit of
rummaging around.  We are happy to help.

Features
--------

For an overview of all the features which are planned:

	http://Graphite.sourceforge.net/featureoverview.html. (old)

For a detailed list of features which are included in this release:

	http://Graphite.sourceforge.net/features.html. (old)

For release notes see:
	
	http://Graphite.sourceforge.net/releasenotes.html. (old)


INSTALLATION
------------

Graphite does its cross-platform, cross-media output through the magic of
PIDDLE.  If you don't have PIDDLE, you can't run Graphite.  Stop now, and
go get piddle from http://piddle.sourceforge.net .

Then, you need either the Numeric (Numpy) or numarray modules
for python.   Numeric is heavily tested; numarray less so.

If you can find the TableIO package for python, it will speed-up
operation on large data files, though graphite defaults to using
a pure-python read routine and will operate identically without it.

Once you have these installed and working, then you're ready for Graphite. 
We don't support graphite for python before 2.2, and it's only tested
on Python 2.4.

You should be able to execute

python setup.py install

from this directory, and have everything put in its proper place.

If you need superuser access to install, it may make more sense to do

python setup.py build
sudo /usr/bin/python setup.py install

so that you don't have problems with compiler path names, if your
environment isn't complete for root.

Next, try it out.

This installs a program (g_multiplot) in your path, and you
can use it to plot multi-column datafiles.   Run it without
arguments to get a page of help and usage information.

You can also use graphite as a library.
Move to the tests subdirectory, and execute "testa.py". 
An Adobe Acrobat (PDF) file should appear.  View this with Acrobat Reader
(or ghostview or whatever), and admire the pretty graph. 

You can try the other test programs too.  And if you edit testa.py, you'll
find that it actually contains a number of different test functions, each
producing a different sort of graph.  Go to the bottom of this file to
select which test is actually run.  You can also change which PIDDLE
backend is used to render the graph at the top of the file.  Experiment. 
Let us know how it goes.


Getting Started
---------------
To get started check out the tutorials on the web page.  

	http://Graphite.sourceforge.net

Also, read the Graphite white paper.


CONTACT INFO
------------

Graphite was initially conceived by Joe and Michelle Strout, with
extensive helpful input from David Ascher and other members of the Python
plotting community.  We expect Graphite to continue developing rapidly, so
you'll want to stay on top of things by frequenting the Graphite web site: 

       http://Graphite.sourceforge.net/
       
and by subscribing to the mailing list:

       http://lists.sourceforge.net/mailman/listinfo/graphite-list

Good luck, have fun, and stay in touch!
