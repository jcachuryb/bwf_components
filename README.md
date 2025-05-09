# bwf_components
bwf_components is a python module that will serve as the library of plugins available to the main componetisation module: bwf_core.

### A plugin
A plugin, or component, is the basic working unit of the BWF_CORE app. It is a self contained unit that needs a blueprint file called **definition.json** and an implementation file called  **component .py**, where an execution function is declared. 
Some plugins can be more complex and may include their own ``models.py, views.py and serializers``
Note: If you add a views .py file, make sure you register them accordingly in the main ``urls.py`` file.


## Adding a plugin

1. Create a folder inside the ``plugins`` folder.

2. Create a ``__init__.py`` file inside the folder.

3. Create a ``definition.json`` file inside the folder.

4. Create a ``component.py`` file inside the folder.
---
#### The definition.json file
This json file defines the structure of the plugin. You will define here the plugin id (a string), its version, input parameters and output fields. An example: 
```{
  "id": "http_request",
  "name": "HTTP Request",
  "description": "Make an HTTP request",
  "version": "1.0.0",
  "author": "BWF Components",
  "editable": false,
  "icon_class": "bi bi-globe",
  "icon_image_src": "icon.png",
  "node_type":"node",
  "base_input": [
    {
      "key": "url",
      "label": "URL",
      "type": "string",
      "value": "",
      "required": true
    },
    {
      "key": "method",
      "label": "Method",
      "type": "string",
      "options": [
        {
          "label": "GET",
          "value": "GET"
        },
        {
          "label": "POST",
          "value": "POST"
        },
        {
          "label": "PUT",
          "value": "PUT"
        },
        {
          "label": "DELETE",
          "value": "DELETE"
        }
      ],
      "value": "GET",
      "required": true
    },
    {
      "key": "headers",
      "label": "Headers",
      "type": "object",
      "value": {},
      "required": false
    },
    {
      "key": "body",
      "label": "Body",
      "type": "object",
      "value": {},
      "required": false
    }
  ],
  "base_output": [
    {
      "key": "response",
      "label": "Response",
      "type": "object",
      "data": {
          "status": {
            "label": "Status",
            "key": "status",
            "type": "number"
          },
          "body": {
            "key": "body",
            "label": "Body",
            "type": "object"
          }
      }
    }
  ]
}
```
---

#### The component .py file
This file must declare a function execute which receives an object with special functions to manage the current plugin state.
```
from  bwf_components.types  import  AbstractPluginHandler
def  execute(plugin:AbstractPluginHandler):
	...
	plugin.set_output({"success": True, data: {}, message: ""})
```
---

#### AbstractPluginHandler abstract class
This class acts like a facade to the object passed from ``bwf_core`` during the execution of a plugin.
Inside ther execution of a plugin these methods can be used. 
**set_output(...)** should always be called to mark the completion of an execution.
 ```
	@abstractmethod
	def collect_context_data(self) -> dict:
        """
        Collect context data for the plugin.
        """
        pass
	@abstractmethod
	def set_output(self, success: bool, data: dict=None, message: str = None):
        """
        Set the output for the plugin.
        """
        pass

	@abstractmethod
	def update_workflow_variable(self, id:str, value):
        """
        Update the workflow variable with the given id and value.
        """
        pass
```