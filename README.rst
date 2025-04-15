============
bwf_components
============

bwf_components is a Django app to build flexible, reusable workflows from a highlevel,
that can be integrated with any other Django App.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "bwf_components" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "bwf_components",
    ]


Adding a new Plugin
-------------------
1. Create a folder inside the ``plugins`` folder.
2. Create a ``__init__.py`` file inside the folder.
3. Create a ``definition.json`` file inside the folder.
4. Create a ``component.py`` file inside the folder.
