from tw.api import Widget, JSLink, CSSLink

#__all__ = ["Twtools"]

# declare your static resources here

## JS dependencies can be listed at 'javascript' so they'll get included
## before
#my_js = JSLink(modname=__name__, 
#                filename='static/twtools.js', javascript=[])

jsunit_js         = JSLink(modname=__name__, filename='static/jsUnitCore.js', javascript=[])
jsunit_version_check_js= JSLink(modname=__name__, filename='static/jsUnitVersionCheck.js', javascript=[])
jsunit_mock_timeout_js = JSLink(modname=__name__, filename='static/jsUnitMockTimeout.js', javascript=[])
jsunit_tracer_js       = JSLink(modname=__name__, filename='static/jsUnitTracer.js', javascript=[])
jsunit_test_manager_js = JSLink(modname=__name__, filename='static/jsUnitTestManager.js', javascript=[])
jsunit_test_suite_js   = JSLink(modname=__name__, filename='static/jsUnitTestSuite.js', javascript=[])
jsunit_xbdebug_js      = JSLink(modname=__name__, filename='static/xbDebug.js', jsvascript=[])

jsunit_css = CSSLink(modname=__name__, filename='static/css/jsUnitStyle.css')

