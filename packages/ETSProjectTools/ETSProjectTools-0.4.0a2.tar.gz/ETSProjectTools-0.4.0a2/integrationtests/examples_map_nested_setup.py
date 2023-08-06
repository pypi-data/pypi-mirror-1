# Sample setup.py file for demonstrating how to use examples_map and docs_map.
#
# Just run "setup.py bdist_egg" to generate an egg that contains the examples
# specified in the examples_map/examples.cfg file.

from setuptools import setup

setup(
    packages = [],
    examples_map = 'examples_map_nested/nest1/nest2/nest3/examples.cfg',
    name = "examples_map_test",
    zip_safe = False,
    )



