import requests
import json

from bwf_components.components.actions.base_action import BaseComponentAction
from bwf_components.components.action_utils.emails import email_sender


'''

'''

class HTTPRequestAction(BaseComponentAction):


    def execute(self):
        inputs = self.collect_context_data()
        component_input = inputs['input']
        url = component_input.get("url")
        method = component_input.get("method")
        headers = component_input.get("headers")
        body = json.load(component_input.get("body"))
        response = requests.request(method, url, headers=headers, data=body)
        self.set_output(True, data={"response": {"status_code": response.status_code, "body": json.loads(response.text)}})
        return True
