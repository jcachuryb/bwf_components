from datetime import datetime

def generate_workflow_definition(name, description="", version="0.0.1"):
    info = {
        'name': name,
        'description': description,
        'version': version,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'workflow': {},
        'inputs': {},
        'variables': {},
    }
    return info
