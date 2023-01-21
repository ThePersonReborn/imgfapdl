import unittest
from main import *

class FunctionTest(unittest.TestCase):
    def test_extract_ID(self):
        expected = "12345678"
        test_cases = [
            f"http://www.imagefap.com/gallery/{expected}",
            f"https://www.imagefap.com/gallery/{expected}",
            f"imagefap.com/gallery/{expected}",
            f"www.imagefap.com/gallery/{expected}",
            f"https://www.imagefap.com/pictures/{expected}/Name-Of-Gallery",
            f"https://www.imagefap.com/pictures/{expected}/Another-Name-Of-Gallery",
            f"https://www.imagefap.com/photo/98239819283/?pgid=4&gid={expected}&page=0",
            f"https://www.imagefap.com/gallery.php?gid={expected}"
        ]
        for test_case in test_cases:
            test_extracted_ID = extract_ID(test_case)
            self.assertEqual(test_extracted_ID, expected, msg=f"No match for URL \"{test_case}\": Expected ID \"{expected}\", got ID \"{test_extracted_ID}\"")