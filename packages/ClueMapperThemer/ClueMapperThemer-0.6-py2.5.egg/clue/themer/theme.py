import os
from deliverance import wsgimiddleware
from deliverance import utils as deliverutils
from paste.request import parse_dict_querystring

WORKINGDIR = 'cluemapper.workingdir'


class Theme(object):
    """A Theme."""

    def __init__(self, themeid, name, path=None,
                 rule_uri=None, theme_uri=None):
        self.themeid = themeid
        self.name = name
        self.path = path
        self.rule_uri = rule_uri
        self.theme_uri = theme_uri

    def __str__(self):
        return '<Theme id=%s; name=%s>' % (self.themeid, self.name)
    __repr__ = __str__

DEFAULT_THEME = Theme(themeid='.DEFAULT_THEME',
                      name='Default Theme',
                      rule_uri='/.defaulttheme/rules/rules.xml',
                      theme_uri='/.defaulttheme/static/theme.html')


class ThemeManager(object):
    """A component for managing what themes are available.

      >>> tmanager = ThemeManager('somewhere')
      >>> tmanager._workingdir
      'somewhere'
      >>> tmanager._lookup_themes()
      {'.DEFAULT_THEME': <Theme id=.DEFAULT_THEME; name=Default Theme>}
      >>> tmanager.themes
      [<Theme id=.DEFAULT_THEME; name=Default Theme>]
      >>> tmanager.get_theme('foo') is None
      True

    """

    def __init__(self, workingdir):
        self._cached_themes = None
        self._workingdir = workingdir

    def _lookup_themes(self):
        p = os.path.join(self._workingdir, 'etc', 'themes')
        themes = {DEFAULT_THEME.themeid: DEFAULT_THEME}
        if os.path.exists(p):
            for x in os.listdir(p):
                if not x.startswith('.'):
                    themes[x] = Theme(x, x, os.path.join(p, x))
        return themes

    @property
    def themes(self):
        if self._cached_themes is None:
            self._cached_themes = self._lookup_themes()
        return self._cached_themes.values()

    def get_theme(self, themeid):
        self.themes # make sure cached value is in place
        return self._cached_themes.get(themeid, None)


class ThemeFilter(object):
    """Middleware for vhost handling for deliverance theming.

      >>> t = ThemeFilter(lambda x, y: None, {})
      >>> t({}, None)
      >>> env = {'HTTP_X_FORWARDED_HOST': 'foo'}
      >>> t._fix_vhost(env)
      >>> env['HTTP_HOST']
      'foo'
      >>> t._act_on_theme(env, {'__clue_set_themeid': 'newtheme'})
      'newtheme'
    """

    def __init__(self, app, global_conf):
        self._app = app
        self._global_conf = global_conf

    def _fix_vhost(self, environ):
        # this is a fix for Deliverance since it doesn't deal with
        # virtual hosts very well
        forwarded = environ.get('HTTP_X_FORWARDED_HOST', None)
        if forwarded:
            environ['HTTP_HOST'] = forwarded

    def _act_on_theme(self, environ, query=None):
        query = query or parse_dict_querystring(environ)
        newthemeid = query.get('__clue_set_themeid',
                               environ.get('cluemapper.themeid', None))
        if newthemeid:
            switch_theme(environ, newthemeid)
            return newthemeid

        newthemeid = self._global_conf.get('cluemapper.defaultthemeid', None)
        if newthemeid:
            switch_theme(environ, newthemeid)
            return newthemeid

        return None

    def __call__(self, environ, start_response):
        self._act_on_theme(environ)
        self._fix_vhost(environ)
        return self._app(environ, start_response)


def make_filter(app, global_conf, *args, **kwargs):
    """Filter factory for theming.

      >>> make_filter(None, {})
      <clue.themer.theme.ThemeFilter object ...>
    """

    deliver = wsgimiddleware.make_filter(app,
                                         global_conf,
                                         theme_uri=DEFAULT_THEME.theme_uri,
                                         rule_uri=DEFAULT_THEME.rule_uri)

    return ThemeFilter(deliver, global_conf)


def switch_theme(environ, themeid):
    """Update deliverance-required environ entries to let it know which theme
    info to use.

      >>> switch_theme({}, 'foo')
      ('/.userthemes/foo/rules/rules.xml', ...)
      >>> switch_theme({}, DEFAULT_THEME.themeid)
      ('/.defaulttheme/rules/rules.xml', '/.defaulttheme/static/theme.html')
    """

    if themeid == DEFAULT_THEME.themeid:
        tbase = '/.defaulttheme'
    else:
        tbase = '/.userthemes/'+themeid
    urls = (tbase + '/rules/rules.xml', tbase + '/static/theme.html')
    deliverutils.set_rule_uri(environ, urls[0])
    deliverutils.set_theme_uri(environ, urls[1])

    return urls
