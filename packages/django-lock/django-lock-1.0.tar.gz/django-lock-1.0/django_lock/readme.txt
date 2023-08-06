===========
Django Lock
===========

Django Lock allows you to lock either individual views or your whole site.
You can provide a date to start locking or finish locking

Installation
============

    1. Copy (or symlink) the ``django_lock`` directory to your Python path.

    2. Add ``'django_lock'`` to your INSTALLED_APPS_ setting (only necessary
       if you are going to use the `site-wide lock`_ or the `log out method`_)

.. _INSTALLED_APPS: http://www.djangoproject.com/documentation/settings/#installed-apps
.. _`site-wide lock`: `using a site-wide lock`_
.. _`log out method`: `providing a transparent preview log out method`_


Using a site-wide lock
======================

Add ``'django_lock.middleware.LockMiddleware'`` to your ``MIDDLEWARE_CLASSES``
setting. Use the lock `settings`_ to configure the locking.

Note that the ``django.static.views.serve`` view will not be locked if the
``DEBUG`` setting is ``True``.


Locking a view
==============

First, import the lock decorator generator and create a decorator (you can
create multiple ones if needed) and use it to decorate your views::

    from django_lock.decorators import lock
	protect = lock(preview_password='yourpassword', until_date=datetime(2009,1,1))

	@protect
	def my_view(request):
		...

The arguments you can pass to ``lock`` are all optional. If you don't provide
an argument, it will fall back to looking for it in the lock `settings`_.

Accepted arguments are ``preview_password``, ``until_date`` and ``after_date``
with the same meanings as their related settings below.


Settings
========

The following settings are used for the site-wide middleware and provide
defaults for lock decorators.

LOCK_UNTIL_DATE
  Lock until the date (a ``datetime`` object) is reached.

LOCK_AFTER_DATE
  Lock after the date (a ``datetime`` object) is reached.

LOCK_PREVIEW_PASSWORD
  An administrative preview password (or passwords) allowing for previewing of
  the view/site while the lock is in place. It can be a string for a single
  password or a list/tuple for multiple passwords.

LOCK_PASSTHROUGH
  Only used for the site-wide lock. Set to a list of URLs - any request
  starting with such a URL will not be locked. For example,
  ``LOCK_PASSTHROUGH = ['/unsecure/']`` would allow access to
  ``http://yourserver/unsecure/...``.


Customising the look
====================

``lock/base.htm`` is the base template. You can override this to easily wrap
the "locked" page in your look (using ``{% extends %}``).

``lock/lock.htm`` is where the action happens. You can override this to get
full control over the "locked" page. The template receives the following
context arguments:

    ``accepts_password``
      Whether the lock accepts an administrative preview password (boolean).

    ``preview_password_key``
      The ``name`` attribute you should give to the HTML password input box.

    ``until_date``
      Only provided if an ``until_date`` was entered (a datetime object).

    ``after_date``
      Only provided if an ``after_date`` was entered (a datetime object).


Providing a transparent preview log out method
==============================================

"Transparent" because it'll only show up on locked pages being previewed with
a valid administrative password.

First, add a new line to your URLconf to link to the logout view (the
``next_page`` argument is the url to redirect to)::

    # Log out from the administrator preview of a locked page
    url(r'^/lock-logout/', 'django_lock.views.logout', {'next_page': '/'}, name='lock-logout'),

Next add ``'django_lock.context_processors.lock_previewing'`` to your
``TEMPLATE_CONTEXT_PROCESSORS`` setting (and ensure you are using
``RequestContext`` to render your templates).

This will add a ``lock_previewing`` variable to your contexts for locked
pages, which you can use in a template like so::

	<ul id="nav">
		...
	{% if lock_previewing %}
		<li><a href="{% url lock-logout %}">Preview log out</a></li>
	{% endif %}
	</ul>