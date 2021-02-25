import shelve
import subprocess

d = shelve.open('last_command')
d.close()

subprocess.call('python telegram_handler.py')
subprocess.call('python test.py')