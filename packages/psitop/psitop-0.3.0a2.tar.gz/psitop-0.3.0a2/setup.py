try:
    from setuptools import setup, find_packages
    use_setuptools = True
except ImportError:
    from distutils.core import setup
    use_setuptools = False
import sys, os

version = '0.3.0a2'

if use_setuptools:
    setup_kwargs = dict(
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        install_requires=[
            'psi',
            'urwid',
        ],
        include_package_data=True,
        zip_safe=False,
        entry_points="""
        # -*- Entry points: -*-
        """,
    )
else:
    setup_kwargs = {}

setup(
    name='psitop',
    version=version,
    description="Utility for viewing process activity.",
    long_description="""\
A Python version of the popular top utility to view process activity
such as CPU use, memory use, etc.  Requires the Python System
Information (PSI) package to be installed and supports all operating
systems that PSI supports.  Also requires Urwid for curses support.

If you have setuptools installed then install using easy_install and
it will take care of the dependencies::

  $ easy_install psitop

Alternatively, install `psi`_ and `urwid`_ then download the psitop
tarball, unpack it and install with::

  $ python setup.py install

(you may need special privileges, such as root, depending on your
system).

.. _psi: http://pypi.python.org/pypi/PSI
.. _urwid: http://excess.org/urwid/

This should install a new command-line program "psitop", which can
be executed directly::

  $ psitop

Some systems will require root privileges to be able to see all details
about all processes.  You may need to use::

  $ sudo psitop

or, on Solaris 10 & OpenSolaris::

  $ pfexec psitop

An example of psitop output looks like::

  Load Averages: 0.45, 0.51, 0.50                       Host: cmmbp

    PID  #TH    USER   GROUP     RSS      VSZ  %CPU COMMAND
    230   36   chris   chris  538176  1503240 16.9% Safari
  16296    1    root   wheel    6028    80760  3.0% Python
    487    1    root   chris    2272    86816  3.0% pmTool
     97    5    root   wheel  146816   593420  2.9% WindowServer
   3562   14   chris   chris   24676   505344  2.4% iTerm
    486    5   chris   chris   13364   472000  1.6% Activity Monitor
  11050   14   chris   chris  120388   640684  1.3% Mail 
   4624   20   chris   chris   71160   569444  1.2% iTunes
  11390    1   chris   chris   21612   461792  1.0% VPNClient
    499    9   chris   chris   52444   507388  0.8% NetNewsWire
    164    4   chris   chris   26844   463360  0.3% Dock   
   1673    6   chris   chris   18468   436948  0.1% DashboardClient
   1226    1   chris   chris    3956   418976  0.1% Memory Monitor 

""",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console :: Curses',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Chris Miles',
    author_email='miles.chris@gmail.com',
    url='http://bitbucket.org/chrismiles/psitop/',
    download_url='http://pypi.python.org/pypi/psitop',
    license='MIT',
    scripts = ["bin/psitop"],
    **setup_kwargs
)
