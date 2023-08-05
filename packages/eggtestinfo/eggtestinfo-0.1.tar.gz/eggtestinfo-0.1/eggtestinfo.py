"""setuptools entry point to capture test info in the .egg-info directory

After installing this egg, rerun 'setup.py egg_info' to get the new file
written into the .egg-info directory of your checkouts.
"""
from pkg_resources import yield_lines

_TEMPLATE = """\
test_suite = %s
tests_require = %s
"""

def write_test_info(cmd, basename, filename):
    dist = cmd.distribution
    tests_require = '\n   '.join(yield_lines(dist.tests_require or ()))
    cmd.write_or_delete_file("test_requirements", filename,
                             _TEMPLATE % (dist.test_suite, tests_require))
