.. _quickstart:

==========
Quickstart
==========

<Description>

.. code-block:: python

    def foo(a, b):
        return {"a": a, "b": b}

.. code-block:: python

    import hydra_slayer

    registry = hydra_slayer.Registry()
    registry.add(foo)

    # ...

    res = registry.get_from_params(**{"_target_": "foo", "a": 1, "b": 2})()
    # {"a": 1, "b": 2}