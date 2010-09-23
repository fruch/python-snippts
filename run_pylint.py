import sys
import pylint.lint
args = ['bitgames.py','-f', 'parseable','--max-line-length=120']

pylint.lint.Run(args, exit=False)
