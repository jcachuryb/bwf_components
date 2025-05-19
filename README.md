# BWF_CORE

A Django app to build flexible, reusable workflows from a highlevel, that can be integrated with any other Django App.
 

## Quick start
There are a couple of configurations to be set in the host app:  

0. Add module to ``requiremens.txt`` 
```
git+https://github.com/dbca-wa/bwf_components.git#egg=bwf_components
```
1. Add "bwf_core" to your ``INSTALLED_APPS`` settings. It should be before the ``bwf_components`` app import.

```
INSTALLED_APPS = [
	...,
	"bwf_components",
	"bwf_core"
]
```

2. Add the templates directory to the TEMPLATE config

```
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "<host_app>/templates",
            BASE_DIR / "bwf_core/templates",
        ],
        ...
    },
]
```

  

3. Include the bwf_core URLconf in your project urls.py like this::
At the top of the host app ``urls.py`` config, import the ``bwf_core`` settings file
``from  bwf_core  import  settings_bwf``
Down below, import the list of urls 
``path("bwf/", include("bwf_core.urls")),``

  

4. Run the django migration commands to create and/or update all the models from bwf_core and the plugins.

5. Start the development server and visit the admin to create a workflow.

---

### Routes

**Home:** Displays workflows and versions

> /bwf/dashboard

  

**Workflow Detail:**

>/bwf/workflow/<int:workflow_id>/  

**Workflow Edition:**

>/bwf/workflow/<int:workflow_id>/edit/<int:version_id>

---

### Core Plugins and more

``bwf_core`` will include inside its folder ``core_plugins`` the definition and execution of base plugins such as branches, loops, etc. However, the rest of plugins are expected to exist inside a sibling project, [bwf_components](https://github.com/dbca-wa/bwf_components)