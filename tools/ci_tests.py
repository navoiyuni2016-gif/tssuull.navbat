"""Run existing tests and expose actionable CI diagnostics as annotations."""
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover('tests'))
if os.environ.get('GITHUB_ACTIONS'):
    for test,error in result.failures+result.errors:
        text=error.replace('%','%25').replace('\r','%0D').replace('\n','%0A')
        print('::error title='+str(test)+'::'+text,flush=True)
sys.exit(0 if result.wasSuccessful() else 1)
