import os, sys

# monkey-patch stdlib's fileinput so it uses "this" FileInput class
import multifileiter.fileinput
import fileinput
fileinput.FileInput = multifileiter.fileinput.LegacyFileInput

# run the standard test 
from test.test_fileinput import test_main
test_main()