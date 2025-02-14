import requests
import json

from actions.base_action import BaseComponentAction
from action_utils.emails import email_sender


'''

'''

class HTTPRequestAction(BaseComponentAction):


    def execute(self):
        inputs = self.collect_inputs()
        url = inputs.get("url")
        method = inputs.get("method")
        headers = inputs.get("headers")
        body = json.load(inputs.get("body"))
        response = requests.request(method, url, headers=headers, data=body)

        self.set_output({"response", {
            "status_code": response.status_code,
            "body": json.loads(response.text)
        }})

        return True


        

        


        
