import rospy


def get_rfid_from_tool_doc(doc_tool):
    return [int(i) for i in doc_tool.to_dict()['rfid']]


def get_path_name_from_task_doc(doc):
    if isinstance(doc.to_dict()['path_name'], str):
        path_name = doc.to_dict()['path_name']
    else:
        path_name = doc.to_dict()['path_name'].encode('ascii', 'ignore')
    return path_name


def return_str_from_doc(doc, name):
    if isinstance(doc.to_dict()[name], str):
        con = doc.to_dict()[name]
    else:
        con = doc.to_dict()[name].encode('ascii', 'ignore')
    return con


def return_float_from_doc(doc, name):
    if doc.to_dict()[name] == '*':
        val = 0.0
    else:
        val = float(doc.to_dict()[name])
    return val


def get_weather_conditions_from_task(doc):
    temp_con = return_str_from_doc(doc, 'temperature_condition')
    temp_val = return_float_from_doc(doc, 'temperature_value')
    humi_con = return_str_from_doc(doc, 'humidity_condition')
    humi_val = return_float_from_doc(doc, 'humidity_value')
    wind_con = return_str_from_doc(doc, 'wind_condition')
    wind_val = return_float_from_doc(doc, 'wind_value')
    pres_con = return_str_from_doc(doc, 'pressure_condition')
    pres_val = return_float_from_doc(doc, 'pressure_value')

    weather_conditions = dict(humidity=dict(condition=(humi_con if humi_con != '*' else 'none'),
                                            value=humi_val),
                              temperature=dict(condition=(temp_con if temp_con != '*' else 'none'),
                                               value=temp_val),
                              wind=dict(condition=(wind_con if wind_con != '*' else 'none'),
                                        value=wind_val),
                              pressure=dict(condition=(pres_con if pres_con != '*' else 'none'),
                                            value=pres_val))
    rospy.logwarn(weather_conditions)
    return weather_conditions
