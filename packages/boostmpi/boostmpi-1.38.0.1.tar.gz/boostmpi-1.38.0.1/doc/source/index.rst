.. boostmpi documentation master file, created by sphinx-quickstart on Tue Feb  3 00:48:53 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to boostmpi's documentation!
====================================

:mod:`boostmpi` is a high-quality Python wrapper around the 
`Message Passing Interface <http://mpi-forum.org>`_ (MPI).
MPI is a standardized interface to libraries such as
`OpenMPI <http://www.open-mpi.org>`_ and 
`MPICH <http://www.mcs.anl.gov/research/projects/mpich2/>`_
that provide high-performance inter-process communication
for distributed-memory computing.
:mod:`boostmpi` uses the 
`Boost.MPI library <www.boost.org/doc/html/mpi.html>`_, 
which gives MPI a very usable C++ interface.
This C++ interface is then made accessible to Python via the 
`Boost.Python library <www.boost.org/doc/libs/release/libs/python/doc/>`_.

:mod:`boostmpi` was originally distributed as part of the 
`Boost C++ library <http://boost.org>`_. This separate
distribution aims to make the software more accessible.

Here's a small sample to give you an idea what programming with
:mod:`boostmpi` is like::

    import boostmpi as mpi

    if mpi.rank == 0:
        for i in range(1, mpi.size):
            mpi.world.send(dest=i, value="Hey %d, what's up?" % i)
    else:
        print mpi.world.recv()


Web Page and Support
--------------------

:mod:`boostmpi` has a `home page <http://mathema.tician.de/software/boostmpi>`_
that contains news, download links and support options for boostmpi.

Table of Contents
-----------------

.. toctree::
    :maxdepth: 2

    installing
    reference
    faq

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

