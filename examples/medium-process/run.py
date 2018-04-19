import shutil
import os
import medium_process
from constants import *

if os.path.exists(STORE):
    shutil.rmtree(STORE)

os.mkdir(STORE)

medium_process.start(STORE)


