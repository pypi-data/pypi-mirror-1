# Sample setup.py file for demonstrating how to use examples_map and docs_map.
#
# Just run "setup.py bdist_egg" to generate an egg that contains the examples
# specified in the examples_map/examples.cfg file.

from setuptools import setup

# Define a list of example files using find_examples()
from enthought.setuptools.find_examples import find_examples
examples = find_examples(
                "examples_map/file1.py",
                "examples_map/old/old*.py",
                ("Tutorial 1", "examples_map/tutorial/tut1.py"),
                ("Tutorial 2", "examples_map/tutorial/tut2.py", "tutorial2.py"),
                destdir="my_package",
                commonprefix="examples_map",
                )


setup(
    packages = [],
    examples_map = 'examples_map/examples.cfg',
    examples = examples,
    name = "examples_map_test",
    zip_safe = False,
    )



