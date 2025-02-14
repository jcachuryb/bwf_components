
from actions.base_action import BaseComponentAction
from action_utils.emails import email_sender


class SendStaticEmailAction(BaseComponentAction):


    def execute(self):
        inputs = self.collect_inputs()
        from_email = inputs.get("from_email")
        to = inputs.get("to")
        subject = inputs.get("subject")
        body = inputs.get("body")
        email_sender.send_static_email(from_email, to, subject, body)



        

        


        
