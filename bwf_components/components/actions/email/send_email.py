
from actions.base_action import BaseComponentAction
from action_utils.emails import email_sender


class SendStaticEmailAction(BaseComponentAction):


    def execute(self):
        inputs = self.collect_inputs()
        component_input = inputs['input']
        
        from_email = component_input.get("from_email")
        to = component_input.get("to")
        subject = component_input.get("subject")
        body = component_input.get("body")
        email_sender.send_static_email(from_email, to, subject, body)



        

        


        
