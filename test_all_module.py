# test_all_modules.py
import unittest

class TestDummy(unittest.TestCase):
    def test_dummy(self):
        # This is a dummy test that always passes
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()
