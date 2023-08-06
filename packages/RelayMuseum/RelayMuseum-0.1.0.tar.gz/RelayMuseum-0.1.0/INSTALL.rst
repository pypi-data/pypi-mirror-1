============
Installation
============

You'll need ``Python 2.5.x`` or newer. As ``django`` currently does not run
on ``Python 3.x``, neither does this.

You will need a database supported by ``django``. ``Python 2.5`` and newer
includes ``sqlite3``, which is adequate.

Either:

1. Install it with ``pip`` 
2. Checkout the source and put it somewhere in your ``PYTHONPATH``
3. Get the source and install with ``setup.py`` as usual

The dependencies are listed in the ``requirements.txt``-file. You can
install everything by running ``git install -r requirements.txt`` once you
have the source.

If running the museum itself as a website you'll need to place the
``django`` database-settings in ``settings_local.py`` in the
``RelayMuseum``-directory and run ``python manage syncdb`` there. If just
using the ``relay``-app, place ``RelayMuseum.relay`` in the ``INSTALLED_APPS``
of the project. 
