import subprocess

def install_requirements():
    requirements_files = [
        'requirements.txt',
        'requirements-dev.txt',
        'requirements-test.txt',
        'requirements-pypi.txt'
    ]

    for req_file in requirements_files:
        subprocess.run(['pip', 'install', '-r', req_file], check=True)

    subprocess.run(['pip', 'install', '-e', '.'], check=True)
    subprocess.run(['playwright', 'install-deps', 'chromium'], check=True)

if __name__ == "__main__":
    install_requirements()