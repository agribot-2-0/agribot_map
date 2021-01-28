## ! DO NOT MANUALLY INVOKE THIS setup.py, USE CATKIN INSTEAD

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

# fetch values from package.xml
setup_args = generate_distutils_setup(
    packages=[
        'agribot_map', 'agribot_map.path_synchronization',
        'agribot_map.task_synchronization'
    ],
    package_dir={'': 'scripts'},
)

setup(**setup_args)