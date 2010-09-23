import sys
import pylint.lint
args = ['bitgames.py', '--rcfile=pylint_rc']

pylint.lint.Run(args, exit=False)
