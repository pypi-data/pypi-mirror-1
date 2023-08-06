import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "pygora",
    version = "0.0.1",
    packages = find_packages(),
    scripts = ['pygora.py'],
    entry_points = {
        'console_scripts': [
            'pygora = pygora:main'
            ]
        },

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt'],
        },

    # metadata for upload to PyPI
    author = "Alfredo Deza",
    author_email = "alfredodeza@gmail.com",
    description = "A simple way to get a nice ratio between your test code and your source code",
    license = "MIT",
    keywords = "test code ratio compare count lines",
    url = "http://code.google.com/p/pygora",   

)

