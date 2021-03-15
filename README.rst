moodle\_inscribe
================

Inscribe students into moodle courses by their email, even if the Moodle API is disabled.

.. image:: https://img.shields.io/pypi/v/moodle_inscribe
   :alt: PyPI

.. image:: https://travis-ci.org/JohannesEbke/moodle_inscribe.svg?branch=master
   :target: https://travis-ci.org/JohannesEbke/moodle_inscribe

Usage
-----

As inputs you need two things from a browser where you are logged into moodle:

* The Course ID - look at the URL: https://moodle.example.edu/course/view.php?id=42 (where 42 is the course id)
* A valid MoodleSession cookie value: Open the developer tools, go to "Storage" -> "Cookies" and copy the Value of the "MoodleSession", e.g. AZ42foo

Quick Start::

  mkvirtualenv -p $(which python3) moodle
  python setup.py develop
  moodle_inscribe --host moodle.hm.edu --course-id 42 --email johannes.ebke@hm.edu --moodle-session AZ42foo
