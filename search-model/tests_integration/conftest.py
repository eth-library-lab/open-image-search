import shutil
import sys, os
sys.path.append("../src")

from dotenv import load_dotenv
load_dotenv("../.env.testing")

import settings

def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """

    print(f"exitstatus: {exitstatus}")
    print(f"session: {session}")

    output_test_dir = os.path.join(settings.BASE_DIR, 'data','processed', 'test_set')
    print(output_test_dir)
    delete_after_test = int(os.environ.get("DELETE_FILES_AFTER_TEST", 0))

    if delete_after_test:
        # TO DO confirm with user if files should be deleted
        # shutil.rmtree(output_test_dir)
        # print(f"removed output test files from: {output_test_dir}")