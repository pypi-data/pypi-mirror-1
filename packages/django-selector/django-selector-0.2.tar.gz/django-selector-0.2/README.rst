django-selector is a custom url pattern parser for Django that is based off of
`Luke Arno's Selector <http://lukearno.com/projects/selector/>`_ for WSGI.  It
is designed to simplify the writing and reading of url patterns by providing
recipes for frequently used patterns.  django-selector's parser ignores classic
regex based url patterns, so if you require the flexibility of regexes you
needn't jump through registration hoops for a one-off url pattern. Using these
named patterns in your urls.py clarifies *what* they are matching as well as
*how* they are matching it::

    patterns('foo.views',
    (r'^/(?P<name>[a-zA-Z0-9\-]+)/(?P<foos>\d*.?\d+)/$', 'index', {}, 'foo-index'))

becomes::

    parser.patterns('foo.views',
    (r'/{name:slug}/{foos:number}/', 'index', {}, 'foo-index'))

You can install django-selector with pip::

    pip install johnny-cache

You can fork django-selector `from its hg repository
<http://dev.jmoiron.net/hg/django-selector>`_::

    hg clone http://dev.jmoiron.net/hg/django-selector

You can also read the full `current development documentation
<http://dev.jmoiron.net/django-selector/>`_ or the `release documentation
<http://packages.python.org/django-selector/>`_.

