import sys
import pylint.lint
args = ['bitgames.py','-f', 'parseable','--max-line-length=120', '--files-output=y']

pylint.lint.Run(args, exit=False)
