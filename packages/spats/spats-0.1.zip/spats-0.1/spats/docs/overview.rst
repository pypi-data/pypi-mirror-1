What is spats?
--------------

A SimplePAgeTemplateServer, credit goes to Leo for the name. Basically
a way to make a web server, quickly and simply to serve dynamic stuff
back to the server.

What does it do?
----------------

Serves compiled page templates back to the user. That's all really,
basically it takes the file on the file system and serves it back. If
that file happens to be a page template it compiles it with simpletal
and then spits it back to the user.

It's not a CGI server (it doesn't serve Python scripts back).

It's not Zope, it doesn't do any of that stuff Zope does. It's simple.

It does GET and HEAD, that's it.

It does not make good cups of tea.

Using
-----

See ``example.py``

Make a directory and put a start.py, that reads::

  from spats import SimplePageTemplateServer
  SimplePageTemplateServer.start()

This won't do much however, you need to tell it where to read HTML
from. So you can pass a config dictionary variable through of all the
possible values.

So make a directory called say ``html`` or ``pt``. Stick a PageTemplate,
called say ``index.pt`` in there. Now pass that directory through and
you are on your way::

  from spats import SimplePageTemplateServer
  config = {"html_dir":"html"}
  SimplePageTemplateServer.start(config)

See ``SimplePageTemplateServer.py`` for a commented list of variables.

Scripts
+++++++

Pass through a ``scripts_dir`` value in the config, and everything in
that dir that: ends in .py and contains a ``__main__`` method will be
compiled into the scripts context.

So you can then access in TAL ``scripts/foo`` where foo is your
script. This will call the ``__call__`` function.

Note: in a script the context will be assigned to the script, this is
the context variable in TAL so you can access all TAL variables in the
script. See some examples in the reports site.

You do not serve scripts directly, you serve PageTemplates that call
scripts.

SimpleTal
+++++++++

This is rather quirky if you are used to Zope TAL, but you should get
there quickly. Main quirks:

- elements have to be closed ``<p tal:content="foo" />`` must be ``<p
  tal:content="foo"></p>``

- the context is different because we build that ourselves and it can
  be tricky

- attributes errors fail silently which is kinda nice but confusing

But it doesn't do...?
---------------------

So add it dude, its only a 200 line module. But keep it simple please,
or goal is to be able to throw together things simply and quickly not
rebuild Zope.
