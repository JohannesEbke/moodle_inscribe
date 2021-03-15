from codecs import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='moodle_inscribe',
    version='3.9.1',
    description='Inscribe students into moodle courses by their email. Works with Moodle 3.9.',
    long_description=long_description,
    url='https://github.com/JohannesEbke/moodle_inscribe',
    author='Johannes Ebke',
    author_email='johannes.ebke@hm.edu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='moodle education',
    packages=['moodle_inscribe'],
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'moodle_inscribe=moodle_inscribe.__main__:main',
        ],
    },
)
