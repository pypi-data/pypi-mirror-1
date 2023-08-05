This is a setuptools plugin for enabling Bazaar support just like standard
Subversion and CVS support.

Use this by adding the following to the 'setup_requires' variable of your
setup() function:

    'setuptools_bzr'

See this package's own setup.py file for an example.  You must either have
bzrlib installed in your Python or access to the bzr(1) command line program.

Barry Warsaw <barry@python.org>

See also:
http://www.bazaar-vcs.org

http://peak.telecommunity.com/DevCenter/setuptools#adding-support-for-other-revision-control-systems
