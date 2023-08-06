import sys
# force module loading from my zip file first
sys.path.insert('bruce-library.zip')

from bruce import run
run.main()
