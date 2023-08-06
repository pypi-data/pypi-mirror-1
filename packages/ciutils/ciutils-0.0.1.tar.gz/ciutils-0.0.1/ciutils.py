
import os
from xmlrunner import XMLTestRunner

def junitrunner():
  return XMLTestRunner(output=os.environ.get('BUILD_REPORT', '.') + '/xunit')

