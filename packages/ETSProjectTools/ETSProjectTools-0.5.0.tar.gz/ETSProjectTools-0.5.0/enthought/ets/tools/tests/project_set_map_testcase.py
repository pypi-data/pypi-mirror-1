"""
Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""


import unittest


from enthought.ets.tools.project_set import ProjectSet


PROJECT_MAP = """
[A]
name = A
version = 1.0
url = http://A
install_requires = ['B[c]']
extras_require = {'d': ['D[e] >= 1.0']}

[B]
name = B
version = 1.0
url = http://B
install_requires = []
extras_require = {'c': ['C']}

[C]
name = C
version = 1.0
url = http://C
install_requires = []
extras_require = {}

[D]
name = D
version = 1.0
url = http://D
install_requires = []
extras_require = {'e': ['E']}

[E]
name = E
version = 1.0
url = http://E
install_requires = []
extras_require = {}

[F]
name = F
version = 1.0
url = http://F
install_requires = []
extras_require = {}

"""
class ProjectSetMapTestCase(unittest.TestCase):
    """
    Test cases for the project set.

    """

    def setUp(self):
        self.ps = ProjectSet()
        self.ps.load_project_map(PROJECT_MAP)

        return

    def test_map_contents(self):
        current = self.ps._project_map.keys()
        expected = ['A', 'B', 'C', 'D', 'E', 'F']
        self._validate_lists(expected, current, 'project map')

        return


    def test_add_without_dependencies(self):
        self.ps.add('A[d]')

        current = self.ps._projects.keys()
        expected = ['A']
        self._validate_lists(expected, current, 'projectS')

        return


    def test_add_with_dependencies(self):
        self.ps.add('A[d]')
        self.ps.add_dependencies()

        current = self.ps._projects.keys()
        expected = ['A', 'B', 'C', 'D', 'E']
        self._validate_lists(expected, current, 'projectS')

        return

    def _validate_lists(self, expected, current, current_name):
        self.assertEqual(len(expected), len(current),
            '%s not equal in length to %s' % (expected, current))
        for i in expected:
            self.assertTrue(i in current, '%s not in %s' % (i, current_name))
        for i in current:
            self.assertTrue(i in expected, '%s not in expected' % i)

        return


if __name__ == '__main__':
    unittest.main()


#### EOF ######################################################################

