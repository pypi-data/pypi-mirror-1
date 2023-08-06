from tw.api import Widget, JSLink, CSSLink, JSSource
from tw.core.resources import Resource

from tw.jsunit.base import *
from tw.jsunit import jsunit_css

__all__ = ["Runner", "RunnerJS", "RunnerSetupJS"]

class RunnerSetupJS(JSSource):
    
    resources = []
    source_vars = ["testpage"]

    src = """
    function jsUnitParseParms(string) {
        var i;
        var searchString = unescape(string);
        var parameterHash = new Object();

        if (!searchString) {
            return parameterHash;
        }

        i = searchString.indexOf('?');
        if (i != -1) {
            searchString = searchString.substring(i + 1);
        }

        var parmList = searchString.split('&');
        var a;
        for (i = 0; i < parmList.length; i++) {
            a = parmList[i].split('=');
            a[0] = a[0].toLowerCase();
            if (a.length > 1) {
                parameterHash[a[0]] = a[1];
            }
            else {
                parameterHash[a[0]] = true;
            }
        }
        return parameterHash;
    }

    function jsUnitConstructTestParms() {
        var p;
        var parms = '';

        for (p in jsUnitParmHash) {
            var value = jsUnitParmHash[p];

            if (!value ||
                p == 'testpage' ||
                p == 'autorun' ||
                p == 'submitresults' ||
                p == 'showtestframe' ||
                p == 'resultid') {
                continue;
            }

            if (parms) {
                parms += '&';
            }

            parms += p;

            if (typeof(value) != 'boolean') {
                parms += '=' + value;
            }
        }
        return escape(parms);
    }

    // var jsUnitParmHash = jsUnitParseParms(document.location.search);
    var jsUnitParmHash = jsUnitParseParms('testpage=$testpage');

    // set to true to turn debugging code on, false to turn it off.
    xbDEBUG.on = jsUnitGetParm('debug') ? true : false;
    """
    template_engine="genshi"
    javascript=[jsunit_js,]
    def update_params(self, d):
        for param in self.source_vars:
            value = getattr(self, param)
        super(RunnerSetupJS, self).update_params(d)
    def post_init(self, *args, **kw):
        pass
    location = Resource.valid_locations.head


class RunnerJS(JSSource):
    
    resources = []
    source_vars = []

    src = """
    var testManager;
    var utility;
    var tracer;


    if (!Array.prototype.push) {
        Array.prototype.push = function (anObject) {
            this[this.length] = anObject;
        }
    }

    if (!Array.prototype.pop) {
        Array.prototype.pop = function () {
            if (this.length > 0) {
                delete this[this.length - 1];
                this.length--;
            }
        }
    }

    function shouldKickOffTestsAutomatically() {
        return jsUnitGetParm('autorun') == "true";
    }

    function shouldShowTestFrame() {
        return jsUnitGetParm('showtestframe');
    }

    function shouldSubmitResults() {
        return jsUnitGetParm('submitresults');
    }

    function getResultId() {
        if (jsUnitGetParm('resultid'))
            return jsUnitGetParm('resultid');
        return "";
    }

    function submitResults() {
        window.mainFrame.mainData.document.testRunnerForm.runButton.disabled = true;
        window.mainFrame.mainResults.populateHeaderFields(getResultId(), navigator.userAgent, JSUNIT_VERSION, testManager.resolveUserEnteredTestFileName());
        window.mainFrame.mainResults.submitResults();
    }

    function wasResultUrlSpecified() {
        return shouldSubmitResults() && jsUnitGetParm('submitresults') != 'true';
    }

    function getSpecifiedResultUrl() {
        return jsUnitGetParm('submitresults');
    }

    function init() {
        var testRunnerFrameset = document.getElementById('testRunnerFrameset');
        if (shouldShowTestFrame() && testRunnerFrameset) {
            var testFrameHeight;
            if (jsUnitGetParm('showtestframe') == 'true')
                testFrameHeight = DEFAULT_TEST_FRAME_HEIGHT;
            else
                testFrameHeight = jsUnitGetParm('showtestframe');
            testRunnerFrameset.rows = '*,0,' + testFrameHeight;
        }
        testManager = new jsUnitTestManager();
        tracer = new JsUnitTracer(testManager);
        if (shouldKickOffTestsAutomatically()) {
            window.mainFrame.mainData.kickOffTests();
        }
    }
    """
    template_engine="genshi"
    javascript=[jsunit_js,]
    def update_params(self, d):
        for param in self.source_vars:
            value = getattr(self, param)
        super(RunnerJS, self).update_params(d)
    def post_init(self, *args, **kw):
        pass
    location = Resource.valid_locations.head


class Runner(Widget):
    runner_setup_js_obj = RunnerSetupJS
    runner_js_obj = RunnerJS
    params = js_params = ["testpage"]
    testpage = "/runpage"
    template = """
<frameset id="testRunnerFrameset" rows="*,0,0" border="0" onload="init()">

    <frame frameborder="0" name="mainFrame" src="toscawidgets/resources/tw.jsunit.base/static/app/main-frame.html">
    <frame frameborder="0" name="documentLoader" src="toscawidgets/resources/tw.jsunit.base/static/app/main-loader.html">
    <frame frameborder="0" name="testContainer" src="toscawidgets/resources/tw.jsunit.base/static/app/testContainer.html">

    <noframes>
        <body>
        <p>Sorry, JsUnit requires support for frames.</p>
        </body>
    </noframes>
</frameset>
    """

    def __init__(self, *args, **kw):
        super(Runner, self).__init__(*args, **kw)
        d = {}
        for param in self.js_params:
            value = getattr(self, param)
            if value is not None:
                d[param] = getattr(self, param)
        runner_setup_js = self.runner_setup_js_obj(**d)
        runner_js = self.runner_js_obj(**d)
        self.javascript = [jsunit_js, jsunit_xbdebug_js, jsunit_test_manager_js, jsunit_tracer_js, jsunit_test_suite_js, runner_setup_js, runner_js]
        self.css = [jsunit_css]

    def update_params(self, d):
        super(Runner, self).update_params(d)

