import re

def update_minor_version():
    filename = 'pyproject.toml'
    with open(filename, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith('version ='):
            # Use regex to extract the version string
            match = re.match(r'version\s*=\s*"(.*?)"', stripped_line)
            if match:
                version = match.group(1)
                version_parts = version.split('.')
                if version_parts[-1].isdigit():
                    # Increment the minor version
                    version_parts[-1] = str(int(version_parts[-1]) + 1)
                    new_version = '.'.join(version_parts)
                    # Replace the line with the updated version
                    lines[i] = f'version = "{new_version}"\n'
                    print(f'Updated version to {new_version}')
                    break
                else:
                    print('Error: Last part of the version is not a digit.')
            else:
                print('Error: Could not parse the version string.')
                break
    else:
        print('Error: Version line not found.')

    # Write the updated lines back to the file
    with open(filename, 'w') as f:
        f.writelines(lines)

# Run the function to update the minor version
update_minor_version()
