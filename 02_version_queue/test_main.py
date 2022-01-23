import unittest
import main
import sys


class TestVersionQueue(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.arguments = main.sanitise_args(['e 1', 'e 4', 'd', 'e 5', 'p 2', 'p 4'])
        main.log = main.init_logger()

    def test_compute(self):
        with self.assertLogs() as captured:
            main.process_queue(self.arguments, main.Mode.COMPUTE)
            self.assertEqual(len(captured.records), 2)
            self.assertIn("['1', '4']", captured.records[0].message)
            self.assertIn("['4', '5']", captured.records[1].message)

    def test_disk(self):
        with self.assertLogs() as captured:
            main.process_queue(self.arguments, main.Mode.DISK)
            self.assertEqual(len(captured.records), 2)
            self.assertIn("['1', '4']", captured.records[0].message)
            self.assertIn("['4', '5']", captured.records[1].message)

    def test_memory(self):
        with self.assertLogs() as captured:
            main.process_queue(self.arguments, main.Mode.MEMORY)
            self.assertEqual(len(captured.records), 2)
            self.assertIn("['1', '4']", captured.records[0].message)
            self.assertIn("['4', '5']", captured.records[1].message)

    def test_compute_using_stdin(self):
        stdin = sys.stdin
        sys.stdin = open('input.txt', 'r')
        with self.assertLogs() as captured:
            main.main()
            self.assertEqual(len(captured.records), 3)
            self.assertIn("['1', '4']", captured.records[1].message)
            self.assertIn("['4', '5']", captured.records[2].message)


if __name__ == '__main__':
    unittest.main()
