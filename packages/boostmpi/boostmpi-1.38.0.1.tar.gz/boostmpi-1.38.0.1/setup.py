#!/usr/bin/env python
# -*- coding: latin-1 -*-

# boostmpi - Boost.MPI.Python redistributed
# Copyright (C) 2007 Doug Gregor
#
# Use, modification and distribution is subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE_1_0.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)





def get_config_schema():
    from aksetup_helper import ConfigSchema, Option, \
            IncludeDir, LibraryDir, Libraries, BoostLibraries, \
            Switch, StringListOption, make_boost_base_options

    return ConfigSchema(make_boost_base_options() + [
        BoostLibraries("python"),

        Option("MPICC", "mpicc",
            "Path to MPI C compiler"),
        Option("MPICXX", 
            help="Path to MPI C++ compiler (defaults to same as MPICC)"),
        BoostLibraries("mpi"),

        StringListOption("CXXFLAGS", [], 
            help="Any extra C++ compiler options to include"),
        StringListOption("LDFLAGS", [], 
            help="Any extra linker options to include"),
        ])




def main():
    import glob
    from aksetup_helper import hack_distutils, get_config, setup, Extension
    from setuptools import find_packages

    hack_distutils()
    conf = get_config(get_config_schema())

    LIBRARY_DIRS = conf["BOOST_LIB_DIR"]
    LIBRARIES = conf["BOOST_PYTHON_LIBNAME"]

    EXTRA_DEFINES = {}
    EXTRA_INCLUDE_DIRS = []
    EXTRA_LIBRARY_DIRS = []
    EXTRA_LIBRARIES = []

    EXTRA_DEFINES["OMPI_SKIP_MPICXX"] = 1
    LIBRARIES.extend(conf["BOOST_MPI_LIBNAME"])

    from distutils import sysconfig
    cvars = sysconfig.get_config_vars()
    cvars["CC"] = conf["MPICC"]
    cvars["CXX"] = conf["MPICXX"]

    INCLUDE_DIRS = [
            "src/cpp",
            ] \
            + conf["BOOST_INC_DIR"] \

    setup(name="boostmpi",
            # metadata
            version="1.38.0.1",
            description="Boost MPI Python wrappers",
            long_description="""
            boostmpi is a high-quality Python wrapper around the 
            `Message Passing Interface <http://mpi-forum.org>`_ (MPI).
            MPI is a standardized interface to libraries such as
            `OpenMPI <http://www.open-mpi.org>`_ and 
            `MPICH <http://www.mcs.anl.gov/research/projects/mpich2/>`_
            that provide high-performance inter-process communication
            for distributed-memory computing.

            boostmpi uses the 
            `Boost.MPI library <www.boost.org/doc/html/mpi.html>`_, which 
            gives MPI a very usable C++ interface.
            This C++ interface is then made accessible to Python
            via the 
            `Boost.Python library <www.boost.org/doc/libs/release/libs/python/doc/>`_.

            boostmpi was originally distributed as part of the 
            `Boost C++ library <http://boost.org>`_. This separate
            distribution aims to make the software more accessible.

            boostmpi (born as Boost.MPI.Python) was written by 
            `Doug Gregor <http://www.osl.iu.edu/~dgregor/>`_
            and is currently maintained by 
            `Andreas Kloeckner <http://mathema.tician.de>`_
            """,
            author=u"Andreas Kloeckner",
            author_email="inform@tiker.net",
            license = "Boost Software License V1",
            url="http://mathema.tician.de/software/boostmpi",
            classifiers=[
              'Environment :: Console',
              'Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'Intended Audience :: Other Audience',
              'Intended Audience :: Science/Research',
              'Natural Language :: English',
              'Programming Language :: C++',
              'Programming Language :: Python',
              'Topic :: Software Development :: Libraries',
              'Topic :: Scientific/Engineering',
              ],

            # build info
            zip_safe=False,

            packages=["boostmpi"],
            package_dir={"boostmpi": "src/python"},
            ext_package="boostmpi",
            ext_modules=[
                Extension("_internal", 
                    glob.glob("src/wrapper/*.cpp"),
                    include_dirs=INCLUDE_DIRS + EXTRA_INCLUDE_DIRS,
                    library_dirs=LIBRARY_DIRS + EXTRA_LIBRARY_DIRS,
                    libraries=LIBRARIES + EXTRA_LIBRARIES,
                    define_macros=list(EXTRA_DEFINES.iteritems()),
                    extra_compile_args=conf["CXXFLAGS"],
                    extra_link_args=conf["LDFLAGS"],
                    ),
                Extension("skeleton_content_test", 
                    glob.glob("src/test/skeleton_content_test.cpp"),
                    include_dirs=INCLUDE_DIRS + EXTRA_INCLUDE_DIRS,
                    library_dirs=LIBRARY_DIRS + EXTRA_LIBRARY_DIRS,
                    libraries=LIBRARIES + EXTRA_LIBRARIES,
                    define_macros=list(EXTRA_DEFINES.iteritems()),
                    extra_compile_args=conf["CXXFLAGS"],
                    extra_link_args=conf["LDFLAGS"],
                    ),
                ],
            data_files=[
                    ("include/boostmpi", glob.glob("src/cpp/boostmpi/*.hpp")),
                    ],
            )




if __name__ == '__main__':
    main()
