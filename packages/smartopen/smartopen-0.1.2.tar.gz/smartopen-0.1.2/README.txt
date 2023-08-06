smartopen
=========

smartopen is a command line program that will transform text according
to handlers to URLs and open them 

Usage
-----

``smartopen --help`` displays the program usage:

"""
Usage: smartopen [options]

Options:
  -h, --help            show this help message and exit
  -c CONFIG, --config=CONFIG
                        config file to read
  -u, --url             print the first url handled
  -a, --all             print all handlers that match the query
  -H HANDLERS, --handler=HANDLERS
                        name of the handler to use, in order
  --print-handlers      print all handlers in order they would be tried
"""

smartopen reads text from standard input or command line arguments.
The handlers are then iterated through in a configurable order and, if
the handler can transform the text into a URL, the URL is then
processed.  Unless otherwise specified by command line options
(e.g. --url, --all), the first matching URL is then opened in firefox.


Handlers
--------

smartopen has a pluggable system of configurable handlers.  The
setuptools entry point ``[smartopen.locations]`` is an extension point
for the handlers.  Several handlers come with smartopen, or you can
write your own.

URL:  a resolvable URL
Google: a google search
Wikipedia: a Wikipedia article
GoogleMaps: an address in google maps


Configuration
-------------

smartopen uses a configuration file that defines the order of the
handlers and their behavior.


Interfacing With Your Environment
---------------------------------

While smartopen is useful of its own right, its utility may be
enhanced by using as part of an environment.  For instance, I run the
fluxbox window manager which allows the use of hotkeys.  By binding
smartopen to Ctrl+Alt+s and using xclip, I can open a URL that is
mappable to a smartopen handler with a keyboard shortcut.  The
relevant line from my ~/.fluxbox/keys file reads:

Control Mod1 s :ExecCommand /home/jhammel/python/smartopen.py "$(xclip -o)" # smartopen


