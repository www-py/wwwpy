import subprocess

# pip install daphne
subprocess.run(['daphne', 'wwwpy.asgi.echo_handler:app'])
