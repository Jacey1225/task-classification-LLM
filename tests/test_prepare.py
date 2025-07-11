import unittest
import os
from src.ConditionalRandomFields.CRF import Prepare

class TestPrepareClass(unittest.TestCase):
    def setUp(self):
        self.output_csv = "data/aug_TIM.csv"
        # Remove the file if it exists from a previous test
        if os.path.exists(self.output_csv):
            os.remove(self.output_csv)

    def test_prepare_and_write(self):
        prepare = Prepare()
        prepare.write_to_csv()  # Uses default filename 'data/aug_TIM.csv'
        # Check if the file was created
        self.assertTrue(os.path.exists(self.output_csv))
        # Check if the file is not empty
        self.assertGreater(os.path.getsize(self.output_csv), 0)
if __name__ == "__main__":
    unittest.main()
