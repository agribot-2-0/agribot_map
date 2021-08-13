def get_rfid_from_tool_doc(doc_tool):
    return [int(i) for i in doc_tool.to_dict()['rfid']]


def get_path_name_from_task_doc(doc):
    if isinstance(doc.to_dict()['path_name'], str):
        path_name = doc.to_dict()['path_name']
    else:
        path_name = doc.to_dict()['path_name'].encode('ascii', 'ignore')
    return path_name
