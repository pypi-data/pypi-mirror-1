import os
from deliverance import wsgimiddleware
from deliverance import utils as deliverutils
from paste.request import parse_dict_querystring

WORKINGDIR = 'cluemapper.workingdir'
CONFIG = 'cluemapper.config'


class Theme(object):
    """A Theme.

      >>> t = Theme('foo', 'bar', '1', '2', '3')
      >>> t
      <Theme id=foo; name=bar>
      >>> t.copy('abc', 'def')
      <Theme id=abc; name=def>
      >>> t.link('ghi', 'jkl')
      <LinkedTheme id=ghi; name=jkl>
      >>> t.link('ghi', 'jkl').path
      '1'
      >>> t.link('ghi', 'jkl').srctheme
      <Theme id=foo; name=bar>
      >>> t.link('ghi', 'jkl').link('xyz', 'abc').srctheme
      <Theme id=foo; name=bar>
      """

    def __init__(self, themeid, name, path=None,
                 rule_uri=None, theme_uri=None):
        self.themeid = themeid
        self.name = name
        self.path = path
        self.rule_uri = rule_uri
        self.theme_uri = theme_uri

    def __str__(self):
        return '<%s id=%s; name=%s>' % (self.__class__.__name__,
                                        self.themeid, self.name)
    __repr__ = __str__

    def copy(self, newthemeid=None, newname=None):
        return Theme(newthemeid or self.themeid,
                     newname or self.name,
                     self.path, self.rule_uri, self.theme_uri)

    def link(self, newthemeid=None, newname=None):
        return LinkedTheme(newthemeid or self.themeid,
                           newname or self.name,
                           self)


class LinkedTheme(Theme):

    def __init__(self, themeid, name, srctheme):
        self.themeid = themeid
        self.name = name
        self.srctheme = srctheme

    @property
    def path(self):
        return self.srctheme.path

    @property
    def rule_uri(self):
        return self.srctheme.rule_uri

    @property
    def theme_uri(self):
        return self.srctheme.theme_uri

    def link(self, newthemeid=None, newname=None):
        return LinkedTheme(newthemeid or self.themeid,
                           newname or self.name,
                           self.srctheme)

DEFAULT_CM_THEME = Theme(themeid='$DEFAULT_CM_THEME',
                         name='Default ClueMapper Theme',
                         rule_uri='/.defaulttheme/rules/rules.xml',
                         theme_uri='/.defaulttheme/static/theme.html')


DEFAULT_CONFIG_THEME = DEFAULT_CM_THEME.link('$DEFAULT_CONFIG_THEME',
                                             'Default Configured Theme')


def themecmp(x, y):
    if x.themeid.startswith('$') and y.themeid.startswith('$'):
        return cmp(x.name, y.name)
    elif x.themeid.startswith('$'):
        return -1
    elif y.themeid.startswith('$'):
        return 1

    return cmp(x.name, y.name)


class ThemeManager(object):
    """A component for managing what themes are available.

      >>> tmanager = ThemeManager('somewhere', {})

    """

    def __init__(self, workingdir, config):
        self._config = config
        self._cached_themes_dict = None
        self._workingdir = workingdir

    def _setup_themes(self):
        p = os.path.join(self._workingdir, 'etc', 'cluemapper', 'themes')
        themes = {DEFAULT_CM_THEME.themeid: DEFAULT_CM_THEME}
        if os.path.exists(p):
            for x in os.listdir(p):
                if x[0] in '_.$':
                    continue
                path = os.path.join(p, x)
                rule_uri = '/.userthemes/%s/rules/rules.xml' % x
                theme_uri = '/.userthemes/%s/static/theme.html' % x
                themes[x] = Theme(x, x, path, rule_uri, theme_uri)

        default_theme_id = self._config['base'].get('defaulttheme', None)
        if default_theme_id is None:
            default_theme_id = DEFAULT_CM_THEME.themeid
        srctheme = themes[default_theme_id]
        themes[DEFAULT_CONFIG_THEME.themeid] = srctheme.link(
            DEFAULT_CONFIG_THEME.themeid,
            DEFAULT_CONFIG_THEME.name)

        self._cached_themes_dict = themes
        self._cached_themes = [x for x in sorted(themes.values(), themecmp)]

    def load_themes(self, refresh=False):
        if refresh or self._cached_themes_dict is None:
            self._setup_themes()

    @property
    def themes(self):
        self.load_themes()
        return self._cached_themes

    def get_theme(self, themeid):
        self.load_themes()
        return self._cached_themes_dict.get(themeid, None)

    @property
    def default_theme(self):
        self.load_themes()
        return self._cached_themes_dict[DEFAULT_CONFIG_THEME.themeid]


class ThemeFilter(object):
    """Middleware for vhost handling for deliverance theming.

      >>> t = ThemeFilter(lambda x, y: None, {})
    """

    _tmanager_factory = staticmethod(ThemeManager)

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

        tmanager = self._tmanager_factory(environ[WORKINGDIR],
                                          environ[CONFIG])
        if not newthemeid:
            newthemeid = tmanager.default_theme.themeid

        switch_theme(tmanager, environ, newthemeid)
        return newthemeid

    def __call__(self, environ, start_response):
        newthemeid = self._act_on_theme(environ)
        self._fix_vhost(environ)
        return self._app(environ, start_response)


def make_filter(app, global_conf, *args, **kwargs):
    """Filter factory for theming.

      >>> make_filter(None, {})
      <clue.themer.theme.ThemeFilter object ...>
    """

    deliver = wsgimiddleware.make_filter(
        app,
        global_conf,
        theme_uri=DEFAULT_CONFIG_THEME.theme_uri,
        rule_uri=DEFAULT_CONFIG_THEME.rule_uri)

    return ThemeFilter(deliver, global_conf)


def switch_theme(tmanager, environ, themeid):
    """Update deliverance-required environ entries to let it know which theme
    info to use.
    """

    theme = tmanager.get_theme(themeid)
    deliverutils.set_rule_uri(environ, theme.rule_uri)
    deliverutils.set_theme_uri(environ, theme.theme_uri)

    return (theme.rule_uri, theme.theme_uri)
