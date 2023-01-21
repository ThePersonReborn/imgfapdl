import unittest
from main import *

class Test_ID_Extraction(unittest.TestCase):
    def test_extract_ID_gives_correct_ID(self):
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
    
    def test_extract_ID_raises_error(self):
        self.assertRaises(RuntimeError, extract_ID, "www.google.com")
        self.assertRaises(RuntimeError, extract_ID, "www.imgfap.com/gallery/12345678")
        self.assertRaises(RuntimeError, extract_ID, "https://www.imagefap.com/galery/12345678")
        self.assertRaises(RuntimeError, extract_ID, "https://www.imagefap.com/gallery.php?xid=12345678")