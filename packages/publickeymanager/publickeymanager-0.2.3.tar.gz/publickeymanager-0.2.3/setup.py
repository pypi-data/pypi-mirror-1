from setuptools import setup, find_packages
import os

def read_file(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

readme = read_file('README.txt')
changes = read_file('CHANGES.txt')

setup(
    name = "publickeymanager",
    version = "0.2.3",
    packages = find_packages('src'),
    package_dir = {'':'src'},
    package_data = { 'publickeymanager': ['*cfg']
            },
    include_package_data = True,

    install_requires = ['paramiko>=1.7.5'],

    author = "Roland van Laar",
    author_email = "roland@micite.net",
    description = "Public Key Manager is designed to generate authorized_keys file and to distribute those to specified servers.",
    long_description='\n\n'.join([readme, changes]),
    classifiers = [
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: System :: Systems Administration"
        ],
    license = "BSD",
    url = "http://launchpad.net/public-key-manager",

    entry_points = {
        'console_scripts':
        ['publickeymanager = publickeymanager.publickeymanager:main']
        }
)

