#!/usr/bin/env python

"""Run this project's tests by running nose on this distribution of the
project.

Takes the same arguments as nosetests .

This is needed only if you want to run the tests with this project's plugin(s)
enabled, and the project is installed system-wide (otherwise, you might get a
funny-looking exception).
"""

import os


if __name__ == "__main__":
    this_dir = os.path.abspath(os.path.dirname(__file__))
    import pkg_resources
    env = pkg_resources.Environment(search_path=[this_dir])
    project_names = list(env)
    assert len(project_names) == 1
    project_name = project_names[0]
    distributions = env[project_name]
    assert len(distributions) == 1
    dist = distributions[0]
    dist.activate()
    import nose
    nose.run_exit()
