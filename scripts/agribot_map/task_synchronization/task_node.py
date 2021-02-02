#!/usr/bin/env python

import os
import shutil
import rospy
from agribot_map.task_synchronization.task_synchronization import TaskSynchronization
from agribot_common.agribot_parameters import get_parameter

LOG_TAG = "TaskSynchronizationNode"


def node():
    rospy.init_node('task_node')

    try:
        robot_serial_number = get_parameter('rsn')
        certificate_file = get_parameter('certificate_file')
        certificate_path = get_parameter('certificate_path')
        tasks_path = os.path.join(os.environ.get('AGRIBOT_HOME'),
                                  get_parameter('/agribot_map/tasks_path'))
        remove_cashed_tasks = get_parameter('/agribot_map/remove_cached_tasks')
    except ValueError as exception_msg:
        rospy.logerr("[{}] {}".format(LOG_TAG, exception_msg))
        return

    key_path = os.path.join(os.environ.get('AGRIBOT_HOME'), certificate_path)
    if not os.path.exists(key_path):
        rospy.logerr("[{}] Key folder '{}' not present".format(
            LOG_TAG, key_path))
        return

    task_synchronization = TaskSynchronization(
        robot_serial_number, tasks_path,
        os.path.join(key_path, certificate_file))

    if remove_cashed_tasks:
        shutil.rmtree(tasks_path)
        os.makedirs(tasks_path)

    task_synchronization.run()

    rospy.spin()


if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
