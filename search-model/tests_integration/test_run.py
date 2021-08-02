import pytest
from dotenv import load_dotenv
from pathlib import Path
import os,sys
sys.path.append('../src')
load_dotenv(Path("../.env.testing"))

import run
import settings

class TestRun():

    def test_end_to_end(self):
        """
        check that the whole data processing and training process can run end-to-end with the sample dataset
        """

        assert 1 == run.main()


    def test_files_were_removed_successfully(self):
        """
        check that the images in the image_to_remove directory 
        are not in the processed data
        """

        imgs_to_remove = os.listdir(settings.removal_image_dir)
        print(imgs_to_remove)
        processed_image_names = []

        for dirpath, dirnames, filenames in os.walk(settings.processed_image_dir):
            for fname in filenames:
                print(fname)
                assert fname not in imgs_to_remove



