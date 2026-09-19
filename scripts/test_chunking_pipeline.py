import unittest
import os
import sys

# Ensure the script directory is on the path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)

from scripts.chunking_pipeline import parse_sections

class TestParseSectionsKnowledgeSource(unittest.TestCase):
    def test_who_detection(self):
        content = """# SECTION

(1) This is a clause from the World Health Organization guidelines.

(2) Another clause.
"""
        chunks = parse_sections("sample.txt", content)
        self.assertTrue(any(c["knowledge_source"] == "WHO" for c in chunks), "WHO not detected")

    def test_wipo_detection(self):
        content = """# SECTION

(1) According to the World Intellectual Property Organization, ...
"""
        chunks = parse_sections("sample.txt", content)
        self.assertTrue(any(c["knowledge_source"] == "WIPO" for c in chunks), "WIPO not detected")

    def test_traditional_detection(self):
        content = """# SECTION

(1) Traditional knowledge about herbal remedies.
"""
        chunks = parse_sections("sample.txt", content)
        self.assertTrue(any(c["knowledge_source"] == "Traditional" for c in chunks), "Traditional not detected")

if __name__ == "__main__":
    unittest.main()

