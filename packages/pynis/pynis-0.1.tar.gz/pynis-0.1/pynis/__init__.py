"""Python NIS

Executes a NIS binary.
"""

import subprocess

execute = lambda args: subprocess.Popen((("nis",) + tuple(args)), stdout=subprocess.PIPE).stdout.read()
