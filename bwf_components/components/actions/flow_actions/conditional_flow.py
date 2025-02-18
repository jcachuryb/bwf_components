import requests
import json

from actions.base_action import BaseComponentAction
from action_utils.emails import email_sender


'''

condition: 
    - expression_a
    - expression_b
    - operator

'''

class ConditionalFlowAction(BaseComponentAction):


    def execute(self):
        inputs = self.collect_inputs()
        component_input = inputs['input']

        flows = self.component.action_flow.components.all()
        condition_set = component_input.get("condition", [])
        # evaluate condition
        result = True
        for condition in condition_set:
            pre_condition = condition.get("pre_condition", None)
            evaluation = self.evaluate_condition(condition)
            if pre_condition:
                result = eval(f"{result} {pre_condition} {evaluation}")
            else:
                result = evaluation       

        if result:
            # component 
            print("Executing True")
            self.set_output({"result": True})
        else:
            self.set_output({"result": False})
            print("Executing False")
        return True



    def evaluate_condition(self, condition, inputs={}):
        operator = condition.get("operator")
        expression_a = condition.get("expression_a")
        expression_b = condition.get("expression_b")

        value_a  = eval(expression_a, None, inputs)
        value_b  = eval(expression_b, None, inputs)
        return eval(f"{value_a} {operator} {value_b}")


        


        
