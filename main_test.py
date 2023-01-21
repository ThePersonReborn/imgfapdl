import unittest
from main import *

class Test_Gallery_ID_Extraction(unittest.TestCase):
    def test_extract_gallery_id_gives_correct_ID(self):
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
            test_extracted_ID = extract_gallery_id(test_case)
            self.assertEqual(test_extracted_ID, expected, msg=f"No match for URL \"{test_case}\": Expected ID \"{expected}\", got ID \"{test_extracted_ID}\"")
    
    def test_extract_gallery_id_raises_error(self):
        self.assertRaises(RuntimeError, extract_gallery_id, "www.google.com")
        self.assertRaises(RuntimeError, extract_gallery_id, "www.imgfap.com/gallery/12345678")
        self.assertRaises(RuntimeError, extract_gallery_id, "https://www.imagefap.com/galery/12345678")
        self.assertRaises(RuntimeError, extract_gallery_id, "https://www.imagefap.com/gallery.php?xid=12345678")

class Test_Image_URL_Extraction(unittest.TestCase):
    def test_get_image_urls_gives_correct_urls(self):
        # If this test case fails, first check if the gallery is still up, I chose a random one and hardcoded the image sources.
        sample_1_source = "1000000"
        sample_1_expected = [
            "https://www.imagefap.com/photo/475178767/?pgid=&gid=1000000&page=0",
            "https://www.imagefap.com/photo/1921274586/?pgid=&gid=1000000&page=0",
            "https://www.imagefap.com/photo/1405211948/?pgid=&gid=1000000&page=0",
            "https://www.imagefap.com/photo/1425824213/?pgid=&gid=1000000&page=0",
            "https://www.imagefap.com/photo/1369442346/?pgid=&gid=1000000&page=0",
            "https://www.imagefap.com/photo/1847947351/?pgid=&gid=1000000&page=0",
            "https://www.imagefap.com/photo/463452677/?pgid=&gid=1000000&page=0",
            "https://www.imagefap.com/photo/1627727652/?pgid=&gid=1000000&page=0",
            "https://www.imagefap.com/photo/2082821028/?pgid=&gid=1000000&page=0"
        ]

        sample_1_test = get_image_URLs(sample_1_source)
        self.assertListEqual(sample_1_test, sample_1_expected)