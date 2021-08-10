def set_rfid(doc_tool):
    rfid = []
    for i in doc_tool.to_dict()['rfid']:
        rfid.append(int(i))
    return rfid


def set_path_name(doc):
    if isinstance(doc.to_dict()['path_name'], str):
        path_name = doc.to_dict()['path_name']
    else:
        path_name = doc.to_dict()['path_name'].encode('ascii', 'ignore')
    return path_name
