Django FlashCookie Application
==============================

This django application provides rails-like flash messages to Django framework.

For installation instructions see the file "INSTALL.txt" in this directory.

Usage::

  request.flash.message = 'some message'

Then on next request you'll have 'flash' dictionary with messages in
RequestContext.
