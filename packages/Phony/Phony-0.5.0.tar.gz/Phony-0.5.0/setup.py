import os
from distutils.core import setup

APP_NAME = 'phony'

#####
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this. Stolen from Django.
def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)
 
 
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
project_dir = '.'
 
for dirpath, dirnames, filenames in os.walk(project_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])
#####


setup(
    name = 'Phony', 
    description = "Generate phony data, including addresses, names, phone numbers, etc.", 
    author = "Brian Tol", 
    author_email = "btol45@gmail.com", 
    version = '0.5.0',  
    packages = packages,
    data_files=data_files,
    license = 'BSD',
)
