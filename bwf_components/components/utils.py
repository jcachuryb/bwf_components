def process_base_input_definition(input_item, input_index):
    new_input = {
        'name': input_item.get("label"),
        'key': input_item.get("key"),
        'data_type': input_item.get("type"),
        'value': "",
        'json_value': {
            "type": input_item.get("type"),
            "options": input_item.get("options", None),
            "value_rules": input_item.get("value_rules"),
        },
        'order': input_index,
        'required': input_item.get("required", False)
    }

    if input_item.get("type") == "array":
        structure = input_item.get("value_rules").get("structure", None)
        if not structure:
            pass
        else:
            new_input['json_value']['multi'] = True
            new_input['json_value']['dynamic'] = input_item.get("value_rules").get("dynamic", False)
            new_input['json_value']['structure'] = {}
            structure_index = 0
            for key, value in structure.items():
                new_input['json_value']['structure'][key] = process_base_input_definition(value, structure_index)
                structure_index += 1

    return new_input