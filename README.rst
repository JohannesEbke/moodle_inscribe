moodle\_inscribe
================

Inscribe students into moodle courses by their email

.. image:: https://img.shields.io/pypi/v/moodle_inscribe
   :alt: PyPI

.. image:: https://travis-ci.org/JohannesEbke/moodle_inscribe.svg?branch=master
   :target: https://travis-ci.org/JohannesEbke/moodle_inscribe

Usage
-----

Quick Start::

  mkvirtualenv -p $(which python3) moodle
  python setup.py develop
  moodle_inscrible --host moodle.hm.edu --course-id 42 --email johannes.ebke@hm.edu --moodle-session AZ42foo
