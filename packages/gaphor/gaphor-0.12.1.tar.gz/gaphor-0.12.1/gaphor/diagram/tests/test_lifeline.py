"""
Unnit tests for simple items.
"""

import unittest

from gaphor import UML
from gaphor.diagram.lifeline import LifelineItem
from gaphas import View


class SimpleItemTestCase(unittest.TestCase):

    def setUp(self):
        self.diagram = diagram = UML.ElementFactory().create(UML.Diagram)
        self.view = View(diagram.canvas)

    def tearDown(self):
        pass

    def test_lifeline(self):
        """
        """
        self.diagram.create(LifelineItem)
        

# vim:sw=4:et:ai
