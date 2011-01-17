dj-cookieauth
-------------

Simple secure cookie authentication.


Install
-------
::

    $ python setup.py install

Configure
---------

Add *djcookieauth.middleware.CookieAuthMiddleware* to your middlewares::

    MIDDLEWARE_CLASSES = (
        ...
        'djcookieauth.middleware.CookieAuthMiddleware'
    )

Add **djcookieauth** to your installed::

    INSTALLED_APPS = (
        ...
        'djcookieauth'
    )

Add urls.py to your url and set the login and logout url to the login view in *djcookieauth.view* . And voilà.


Note: If you want sha256 encoded password, add these lines on top of
your settings.py::

    from djcookieauth.auth import patch_auth
    patch_auth()
