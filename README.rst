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

2. Include the polls URLconf in your project urls.py like this::

    path("bwf_components/", include("bwf_components.urls")),

3. Run ``python manage.py migrate`` to create the models.

4. Start the development server and visit the admin to create a workflow.
