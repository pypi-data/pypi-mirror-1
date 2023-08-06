Welcome to Cogbin. If you want to use cogbin for your python software community you are just few steps away. Example: Turbogears project has modified the keywords in cogbin and it uses cogbin to display projects related to turbogears web framework. They look for keywords like: turbogears2, turbogears2.application. Cogbin finds these keywords in pypi and displays a list of packages that have the appropriate keywords in them. 

If you want to use cogbin for your software community please modify the categories (pypi keywords) in cogbin/controllers/root.py. These keywords are displayed on the main page. 

First time:Download pypi.cPickle from our project site, or run pypisync.py for at least 10h+

Please setup pypisync.py to run in a cronjob once a day between 1am-3am. 
Please setup pypiload.py to run an hour later.
Both files can be found in cogbin/controllers/.


Installation and Setup
======================

Install ``cogbin`` using the setup.py script::

    $ cd cogbin
    $ python setup.py install

Create the project database for any model classes defined::

    $ paster setup-app development.ini

Start the paste http server::

    $ paster serve development.ini

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ paster serve --reload development.ini

Then you are ready to go.

Thank you and enjoy.
This software was designed in Chicago IL. You can find the sourcode in https://launchpad.net/cogbin/
or
https://launchpad.net/cogbin/+download


