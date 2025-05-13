from bwf_components.plugins.approval.models import Approval, BWF_Role
from bwf_components.types import AbstractPluginHandler

def execute(plugin:AbstractPluginHandler):
    inputs = plugin.collect_context_data()
    component_input = inputs['input']
    roles = component_input.get('roles', [])
    task_id = component_input.get("task_id")
    approval_timeout = component_input.get("approval_timeout", 300)

    ids = []
    for role in roles:
        if 'role_id' in role:
            id = role.get('role_id', None).get('id', None)
        elif 'id' in role: 
            id  = role.get('id', None)
        else:
            id = role
        ids.append(id)

    print(BWF_Role.objects.filter(id__in=ids))
    # get Task blueprint
    # fill in fields
    # persist
    # task  -> Send to roles
    # mark as one step complete
    
    try:
        # email_sender.send_static_email(from_email, to, subject, body)
        plugin.set_output(True)
    except Exception as e:
        plugin.set_output(False, message=str(e))

def callback(plugin:AbstractPluginHandler, data={}):
    pass
