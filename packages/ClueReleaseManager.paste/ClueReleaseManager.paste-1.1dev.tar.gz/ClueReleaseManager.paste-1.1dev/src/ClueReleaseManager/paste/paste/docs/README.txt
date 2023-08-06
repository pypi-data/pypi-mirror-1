What is ClueReleaseManager.paste
=======================================

It is just another wsgi wrapper to use a ClueReleaseManager application
into a paster configuration

How to use ClueReleaseManager.paste
==========================================


Calling the App
----------------

::

    [composite:main]
    use = egg:Paste#urlmap
    / = foo
    [app:foo]
    use=egg:ClueReleaseManager.paste
    basefiledir=%(here)s/test_files
    baseurl=http://localhost:8096
    self_register=true
    backup_pypis=http://localhost:8096

Configuration options
----------------------------

 * baseurl: baseurl of the application [optionnal] [default: localhost]
 * basefiledir: where to store distributions [optionnal] [default: files]
 * self_register: enable auto registration [optionnal]  [default:false]
 * backup_pypis: line separted pypi backup servers [optionnal]  [default:[]]
 * sqluri: SQLAlchemy database URI [optionnal] [default: sqlite:///cluerelmgr.db']

