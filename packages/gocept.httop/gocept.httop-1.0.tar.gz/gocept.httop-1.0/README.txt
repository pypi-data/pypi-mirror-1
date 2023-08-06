=====
httop
=====

httop is a console tool to monitor the responsiveness of websites (or any URL)
like monitoring  your system processes with ``top``.

URLs are re-checked 3 seconds after their last result was received.

Usage
=====

Create a configuration file in your home directory called ``.httop`` listing
the URLs that should be monitored::

    http://localhost:8080
    http://www.foodibar.com

Then, start the script without any parameters::

    $ httop

While running, you can update the configuration file. New URLs will be
picked up automatically and removed URLs will be dropped.
