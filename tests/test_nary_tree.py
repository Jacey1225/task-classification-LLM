import unittest
import logging
from src.ConditionalRandomFields.N_ary_tree import NaryTree

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestNaryTree(unittest.TestCase):
    def test_construct_tree(self):
        # Initialize tree with root values "T" and "O"
        tree = NaryTree(root_values=["T", "O"], n=3)
        # Each child should be ["T", "O"]
        tree.construct_tree(["T", "O"])
        
        # Check root values
        root_values = [root.value for root in tree.roots]
        
        # Check children of each root
        for root in tree.roots:
            child_values = [child.value for child in root.children]