

DOCTESTS
================

ClueReleaseManager factory
-----------------------------------------

Checking that everything is in place::

    >>> resp = app.get('/')
    >>> 'href="http://localhost:8096/login"' in resp.body
    True
    >>> os.path.exists(os.path.join(here_dir, 'db.db'))
    True

