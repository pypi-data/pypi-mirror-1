Reference Documentation
=======================

.. automodule:: boostmpi

Communicators
-------------

.. autoclass:: Communicator
    :members:

Utility functions
-----------------

.. autofunction:: init
.. autofunction:: initialized
.. autofunction:: abort
.. autofunction:: finalize
.. autofunction:: finalized

Collectives
-----------

.. autofunction:: all_gather
.. autofunction:: all_reduce
.. autofunction:: all_to_all
.. autofunction:: broadcast
.. autofunction:: gather
.. autofunction:: reduce
.. autofunction:: scan
.. autofunction:: scatter

Non-blocking Communication
--------------------------

.. autoclass:: Request
    :members:

.. autoclass:: RequestList
    :members:

.. autoclass:: Status
    :members:

.. autofunction:: test_all
.. autofunction:: test_any
.. autofunction:: test_some
.. autofunction:: wait_all
.. autofunction:: wait_any
.. autofunction:: wait_some

Skeleton/Content API
--------------------

.. autoclass:: SkeletonProxy
    :members:
.. autoclass:: Content
    :members:

.. autofunction:: get_content
.. autofunction:: skeleton

Timers
------

.. autoclass:: Timer
    :members:

Error Handling
--------------

.. autoexception:: Error
.. autoexception:: ObjectWithoutSkeletonError
