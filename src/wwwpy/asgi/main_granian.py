import subprocess

# pip install granian
subprocess.run(['granian', '--interface', 'asgi', 'echo_handler:app'])
