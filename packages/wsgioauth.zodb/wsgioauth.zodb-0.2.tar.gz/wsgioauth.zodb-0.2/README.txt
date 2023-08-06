--------
Overview
--------

The wsgioauth.zodb package is a library that extends the wsgioauth parent package by adding support for the Zope Object Database (ZODB).

Example
=======

The example requires you to setup a ZEO instance.  You can setup a ZEO instance using the following two commands (setup may very depending on your system setup)::

    $ $PATH_TO/mkzeoinst myzeo
    $ myzeo/bin/zeoctl start

At this point the ZEO instance should be running on the default port 8100.  Next, you run the example using PasteDeploy and the wsgioauth package's consumer example with the following commands::

    $ cd $PATH_TO/wsgioauth.zodb
    $ paster serve run.ini &
    $ cd $PATH_TO/wsgioauth
    $ python example/consumer.py &

Open your web browser and go to the address http://localhost:8081/ (location where the consumer is running).  There you will be given a link to print your vacation picture (see the OAuth specification for details about this example use-case).  After clicking this link the consumer obtains the access token to make a call to the protected resource for the image.  In this case we are simply using an echo application to echo the parameters.  The results will show on the http://localhost:8081/print_vacation page, along with a link back to the index page.  The access token information will be displayed on the index page after it has been acquired.
