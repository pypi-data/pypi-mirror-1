Installing boostmpi
===================

This tutorial will walk you through the process of building
:mod:`mpiboost`. To follow, you only need four basic things:

* A UNIX-like machine with web access.
* An `MPI <http://mpi-forum.org>`_ implementation. Issuing the
  :command:`mpicc --help` in your shell should not result in
  an error.
* A C++ compiler, preferably a Version 4.x gcc.
* A working `Python <http://www.python.org>`_ installation, 
  Version 2.4 or newer.

Step 1: Build Boost
-------------------

You may already have a working copy of the `Boost C++ libraries
<http://www.boost.org>`_. If so, make sure that it's version 1.37.0 or newer.
If not, no problem, there are simple `instructions
<http://mathema.tician.de/software/install-boost>`_ on how to build and install
boost available.

.. note::

    You need to compile boost with MPI support. Consult the Boost documentation
    on how to achieve that with your MPI implemenation.

Step 2: Create and Customize a Configuration File
-------------------------------------------------

Copy and paste the following text into a file called
:file:`.aksetup-defaults.py` (Make sure not to miss
the initial dot, it's important.) in your home directory::

    BOOST_INC_DIR = ['/home/andreas/pool/include/boost-1_37']
    BOOST_LIB_DIR = ['/home/andreas/pool/lib']
    BOOST_PYTHON_LIBNAME = ['boost_python-gcc43-mt']

You will need to adapt the path names in this file to your personal
situation, of course.

Additionally, make sure that the compiler tag in
`BOOST_PYTHON_LIBNAME` matches your boost libraries. (It's `gcc43` in
the example, which stands for gcc Version 4.3. Yours may be different.
Find out by looking at the directory listing of :file:`$HOME/pool/lib`, or
wherever you installed the Boost libraries.)

Step 3: Download and Unpack boostmpi
------------------------------------

Download the latest `release of boostmpi
<http://pypi.python.org/pypi/boostmpi>`_. Then do this::

    $ tar xfz boostmpi-VERSION.tar.gz


Step 4: Build and Install boostmpi
----------------------------------

Actually compiling and installing hedge should now be fairly simple::

    $ cd boostmpi-VERSION # if you're not there already
    $ sudo python setup.py install

Get some coffee while boostmpi is installed. If you don't get any errors,
congratulations! You have successfully installed boostmpi.

Step 5: Run Tests
-----------------

You can run boostmpi's automated unit tests by typing::

    $ cd boostmpi-VERSION # if you're not there already
    $ cd test
    $ mpirun -np 5 python run_all.py

