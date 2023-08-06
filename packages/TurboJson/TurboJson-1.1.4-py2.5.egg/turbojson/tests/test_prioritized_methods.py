from unittest import TestCase
import dispatch
from turbojson.prioritized_methods import PriorityDisambiguated


class TestPriorityDisambiguated(TestCase):

    def setUp(self):
        self.demo_func.clear()
        self.counter = 0

    def demo_func(self, number):
        pass
    demo_func = dispatch.generic(PriorityDisambiguated)(demo_func)

    def test_no_ambiguous(self):
        """Non-ambiguous methods are processed fine"""
        self.demo_func.when("(number >= 0) and (number < 10)")(lambda s, x: 0)
        self.demo_func.when("(number >= 10) and (number < 20)")(lambda s, x: 10)
        self.demo_func.when("(number >= 20) and (number < 30)")(lambda s, x: 20)

        self.assertEqual(self.demo_func(3), 0)
        self.assertEqual(self.demo_func(13), 10)
        self.assertEqual(self.demo_func(23), 20)

    def test_non_prioritized_ambiguous(self):
        """Non-prioritized ambiguous methods are processed fine"""
        self.demo_func.when("(number >= 0) and (number <= 10)")(lambda s, x: 0)
        self.demo_func.when("(number >= 10) and (number < 20)")(lambda s, x: 10)
        self.demo_func.when("(number >= 20) and (number < 30)")(lambda s, x: 20)

        self.assertEqual(self.demo_func(3), 0)
        self.assertRaises(dispatch.AmbiguousMethod, self.demo_func, 10)
        self.assertEqual(self.demo_func(13), 10)
        self.assertEqual(self.demo_func(23), 20)

    def test_no_applicable_methods(self):
        """NoApplicableMethods is raised when it should"""
        self.demo_func.when("(number >= 0) and (number < 10)")(lambda s, x: 0)
        self.demo_func.when("(number >= 10) and (number < 20)")(lambda s, x: 10)
        self.demo_func.when("(number >= 20) and (number < 30)")(lambda s, x: 20)

        self.assertRaises(dispatch.NoApplicableMethods, self.demo_func, -1)
        #self.assertRaises(dispatch.NoApplicableMethods, self.demo_func, 33) # Fails with RuleDispatch pre r2240

    def test_prioritized_ambiguous(self):
        """Prioritized ambiguous methods are processed fine"""
        self.demo_func.when("(number >= 0) and (number <= 10)",prio=1)(
            lambda s,x: 0
        )
        self.demo_func.when("(number >= 10) and (number < 20)")(lambda s, x: 10)
        self.demo_func.when("(number >= 20) and (number < 30)")(lambda s, x: 20)

        self.assertEqual(self.demo_func(3), 0)
        self.assertEqual(self.demo_func(10), 0)
        self.assertEqual(self.demo_func(13), 10)
        self.assertEqual(self.demo_func(23), 20)
        self.assertRaises(dispatch.NoApplicableMethods, self.demo_func, -1)
        #self.assertRaises(dispatch.NoApplicableMethods, self.demo_func, 33) # Fails with RuleDispatch pre r2240

    def test_before(self):
        """Priority is respected when decorating with before"""

        def between_0_30(self, number):
            return number
        between_0_30 = self.demo_func.when(
            "(number >= 0) and (number < 30)")(between_0_30)

        def before_between_2_4(self, number):
            self.counter = number
        before_between_2_4 = self.demo_func.before(
            "(number >= 2) and (number < 4)")(before_between_2_4)

        def before_between_0_30_1(self, number):
            self.counter += number
        before_between_0_30_1 = self.demo_func.before(
            "(number >= 0) and (number < 30)", prio=1)(before_between_0_30_1)

        def before_between_0_30_2(self, number):
            self.counter *= number
        before_between_0_30_2 = self.demo_func.before(
            "(number >= 0) and (number < 30)")(before_between_0_30_2)

        self.assertEqual(self.demo_func(3), 3)
        self.assertEqual(self.counter, 18)
