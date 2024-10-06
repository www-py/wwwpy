import importlib

required = {
    ('pytest',),
    ('xvirt', 'pytest-xvirt'),
    ('playwright',),
    ('pytest_playwright', 'pytest-playwright')
}
missing_pip = set()
installed = set()
for tup in required:

    pip_name = tup[0] if len(tup) == 1 else tup[1]
    try:
        importlib.import_module(tup[0])
        installed.add(pip_name)
    except ImportError:
        missing_pip.add(pip_name)

if len(missing_pip) > 0:
    msg = ('You need to install the following packages to use this plugin:\n   '
           + ', '.join(missing_pip)
           + '\n\nYou can install them by running:\n   `pip install ' + ' '.join(missing_pip) +
           '`\n\n'
           + 'Packages already installed: ' + ', '.join(installed)
           )
    raise ImportError(msg)
