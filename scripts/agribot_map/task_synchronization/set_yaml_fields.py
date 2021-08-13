import rospy


def get_rfid_from_tool_doc(doc_tool):
    return [int(i) for i in doc_tool.to_dict()['rfid']]


def get_path_name_from_task_doc(doc):
    if isinstance(doc.to_dict()['path_name'], str):
        path_name = doc.to_dict()['path_name']
    else:
        path_name = doc.to_dict()['path_name'].encode('ascii', 'ignore')
    return path_name


def get_weather_conditions_from_task(doc):
    if isinstance(doc.to_dict()['temperature_condition'], str):
        temp_con = doc.to_dict()['temperature_condition']
    else:
        temp_con = doc.to_dict()['temperature_condition'].encode('ascii', 'ignore')
    if doc.to_dict()['temperature_value'] == '*':
        temp_val = 0.0
    else:
        temp_val = float(doc.to_dict()['temperature_value'])
    rospy.logwarn(dict(condition=(temp_con if temp_con != '*' else 'none'), value=temp_val))
    if isinstance(doc.to_dict()['humidity_condition'], str):
        humi_con = doc.to_dict()['humidity_condition']
    else:
        humi_con = doc.to_dict()['humidity_condition'].encode('ascii', 'ignore')
    if doc.to_dict()['humidity_value'] == '*':
        humi_val = 0.0
    else:
        humi_val = float(doc.to_dict()['humidity_value'])
    rospy.logwarn(dict(condition=(humi_con if humi_con != '*' else 'none'), value=humi_val))
    if isinstance(doc.to_dict()['wind_condition'], str):
        wind_con = doc.to_dict()['wind_condition']
    else:
        wind_con = doc.to_dict()['wind_condition'].encode('ascii', 'ignore')
    if doc.to_dict()['wind_value'] == '*':
        wind_val = 0.0
    else:
        wind_val = float(doc.to_dict()['wind_value'])
    rospy.logwarn(dict(condition=(wind_con if wind_con != '*' else 'none'), value=wind_val))
    if isinstance(doc.to_dict()['pressure_condition'], str):
        pres_con = doc.to_dict()['pressure_condition']
    else:
        pres_con = doc.to_dict()['pressure_condition'].encode('ascii', 'ignore')
    if doc.to_dict()['pressure_value'] == '*':
        pres_val = 0.0
    else:
        pres_val = float(doc.to_dict()['pressure_value'])
    rospy.logwarn(dict(condition=(pres_con if pres_con != '*' else 'none'), value=pres_val))

    weather_conditions = dict(temperature=dict(condition=(temp_con if temp_con != '*' else 'none'),
                                               value=temp_val),
                              humidity=dict(condition=(humi_con if humi_con != '*' else 'none'),
                                            value=humi_val),
                              wind=dict(condition=(wind_con if wind_con != '*' else 'none'),
                                        value=wind_val),
                              pressure=dict(condition=(pres_con if pres_con != '*' else 'none'),
                                            value=pres_val))
    rospy.logwarn(weather_conditions)
    return weather_conditions
