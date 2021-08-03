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

    test_dir = os.path.join(settings.BASE_DIR, 'data','processed', 'test_set')
    print(test_dir)
    shutil.rmtree(test_dir)