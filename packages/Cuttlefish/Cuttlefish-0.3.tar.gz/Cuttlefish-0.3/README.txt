Cuttlefish is an example project using the Bottle flyweight Web
framework and the Mako template engine in Python. It's intended to run
on your desktop, and provide a lightweight search engine (using grep)
for your source code.

[[[NOTE]]]
This is an early development alpha. It basically works, but there are
many known issues yet to be fixed.

The cuttlefish command-line tool runs the app using Bottle's
WSGIRefServer support. The cuttlefish-config.plist is in this case read
directly from the cuttlefish package, which is not nice. This will get
fixed, eventually, but in the meantime it's convenient for my debugging.

There is a cuttlefish.wsgi file also embedded in the cuttlefish package.
This can be copied to wherever Apache w/ mod_wsgi would like to see it.
In this case, the cuttlefish-config.plist should either be copied
alongside cuttlefish.wsgi or the latter should be edited to point to
wherever your customized cuttlefish-config.plist resides.

-- Kaelin 10/26/2009
