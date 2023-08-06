# bad monkey patches

# Patching deliverance is required because as it stands the decoding routine
# is not converting back and forth to utf-8 properly.


def patch():
    patch_deliverance()
    patch_trac_prefs()


def unpatch():
    unpatch_trac_prefs()
    unpatch_deliverance()


def deliver_decodeAndParseHTML(text):
    """A replacement function for decoding to utf-8.

      >>> deliver_decodeAndParseHTML('<html><body></body></html>')
      <Element html at ...>
    """

    if not isinstance(text, unicode):
        text = text.decode('utf-8')
    from lxml import etree
    content = etree.HTML(text)
    assert content is not None
    return content


def patch_deliverance():
    """Change htmlserialize.decodeAndParseHTML to convert to unicode
    as necessary.

      >>> ignored = unpatch_deliverance()

      >>> patch_deliverance()
      True
      >>> from deliverance import htmlserialize
      >>> hasattr(htmlserialize.decodeAndParseHTML, '_cluemapper_patched')
      True
      >>> patch_deliverance()
      False

      >>> unpatch_deliverance()
      True
      >>> hasattr(htmlserialize.decodeAndParseHTML, '_cluemapper_patched')
      False
      >>> unpatch_deliverance()
      False
    """

    from deliverance import htmlserialize
    if hasattr(htmlserialize.decodeAndParseHTML, '_cluemapper_patched'):
        return False

    htmlserialize.decodeAndParseHTML._cluemapper_patched = \
        htmlserialize.decodeAndParseHTML.func_code
    htmlserialize.decodeAndParseHTML.func_code = \
        deliver_decodeAndParseHTML.func_code

    return True


def unpatch_deliverance():
    """Remove the deliverance patch."""

    from deliverance import htmlserialize
    if not hasattr(htmlserialize.decodeAndParseHTML, '_cluemapper_patched'):
        return False

    htmlserialize.decodeAndParseHTML.func_code = \
        htmlserialize.decodeAndParseHTML._cluemapper_patched
    del htmlserialize.decodeAndParseHTML._cluemapper_patched

    return True


def trac_get_preference_panels(self, req):
    """Replacement for trac preferences panel function.

      >>> from clue.tools.testing import Mock
      >>> req = Mock(authname='anonymous')
      >>> [x for x in trac_get_preference_panels(None, req)]
      [(None, 'Date & Time'), ...]
    """
    yield (None, 'Date & Time')
    yield ('keybindings', 'Keyboard Shortcuts')
    if not req.authname or req.authname == 'anonymous':
        yield ('advanced', 'Advanced')


def trac_render_preference_panel(self, req, panel):
    """Replacement for trac render preferences function.

      >>> from clue.tools.testing import Mock
      >>> context = Mock(_do_load=lambda x: None, _do_save=lambda x: None)
      >>> req = Mock(method='POST', args={'restore': None},
      ...            session=Mock(sid=None),
      ...            redirect=lambda x: None, href=Mock(prefs=lambda x: None))
      >>> trac_render_preference_panel(context, req, None) is not None
      True
      >>> del req.args['restore']
      >>> trac_render_preference_panel(context, req, None) is not None
      True

    """

    from trac.prefs import web_ui
    if req.method == 'POST':
        if 'restore' in req.args:
            self._do_load(req)
        else:
            self._do_save(req)
        req.redirect(req.href.prefs(panel or None))

    kwargs = {
        'settings': {'session': req.session,
                     'session_id': req.session.sid},
        'timezones': web_ui.all_timezones,
        'timezone': web_ui.get_timezone,
        }
    return ('prefs_%s.html' % (panel or 'datetime'), kwargs)


def patch_trac_prefs():
    """Since we are using UserManager, we need to disable the general tab
    preferences.

      >>> orig = unpatch_trac_prefs()
      >>> patch_trac_prefs()
      True
      >>> patch_trac_prefs()
      False
      >>> unpatch_trac_prefs()
      True
      >>> unpatch_trac_prefs()
      False
      >>> if orig: ignored = patch_trac_prefs()

    """

    from trac.prefs import web_ui
    if hasattr(web_ui.PreferencesModule,
               '_cluemapper_get_pref_panels_patched'):
        return False

    web_ui.PreferencesModule._cluemapper_get_pref_panels_patched = \
        web_ui.PreferencesModule.get_preference_panels
    web_ui.PreferencesModule.get_preference_panels = \
        trac_get_preference_panels

    web_ui.PreferencesModule._cluemapper_render_pref_patched = \
        web_ui.PreferencesModule.render_preference_panel
    web_ui.PreferencesModule.render_preference_panel = \
        trac_render_preference_panel

    return True


def unpatch_trac_prefs():
    """Remove trac patch."""

    from trac.prefs import web_ui
    if not hasattr(web_ui.PreferencesModule,
                   '_cluemapper_get_pref_panels_patched'):
        return False

    web_ui.PreferencesModule.get_preference_panels = \
        web_ui.PreferencesModule._cluemapper_get_pref_panels_patched
    del web_ui.PreferencesModule._cluemapper_get_pref_panels_patched

    web_ui.PreferencesModule.render_preference_panel = \
        web_ui.PreferencesModule._cluemapper_render_pref_patched
    del web_ui.PreferencesModule._cluemapper_render_pref_patched

    return True
