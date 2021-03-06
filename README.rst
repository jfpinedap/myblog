My Blog - Group G
=================

This app is based on the basic blog app built in the Flask `tutorial`_.

.. _tutorial: https://flask.palletsprojects.com/tutorial/

Users will be able to register, log in, create blogs, edit or delete their own blogs and comment the public blogs.

.. contents:: Table of Contents
   :depth: 2

Dependencies
------------

Be sure you have installed this `dependencies`_.

.. _dependencies: https://flask.palletsprojects.com/en/1.1.x/installation/


Install
-------

Clone the repository ::
    
    $ git clone https://github.com/jfpinedap/myblog.git
    $ cd myblog
    $ git checkout develop

Create a virtualenv and activate it::

    $ python3 -m venv venv
    $ . venv/bin/activate

Or on Windows cmd::

    $ py -3 -m venv venv
    $ venv\Scripts\activate.bat

Install Myblog::

    $ pip install -e .

Or if you are using the master branch, install Flask from source before
installing Myblog::

    $ pip install -e ../..
    $ pip install -e .


Run
---

::

    $ export FLASK_APP=myblog
    $ export FLASK_ENV=development
    $ flask init-db
    $ flask run

Or on Windows cmd::

    > set FLASK_APP=myblog
    > set FLASK_ENV=development
    > flask init-db
    > flask run

Open http://127.0.0.1:5000 in a browser.


Test
----

::

    $ pip install '.[test]'
    $ pytest

Run with coverage report::

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser
