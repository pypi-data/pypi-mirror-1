import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               FormField, register_static_directory
from turbogears.widgets.base import mochikit

js_dir = pkg_resources.resource_filename("mochiinterpreter",
                                         "static/javascript")
register_static_directory("mochiinterpreter.javascript", js_dir)
css_dir = pkg_resources.resource_filename("mochiinterpreter",
                                         "static/css")
register_static_directory("mochiinterpreter.css", css_dir)


class MochiInterpreter(FormField):
    """
    This widget is an implementation of the interpreter example from MochiKit
    code.  It is provided as a facility to develop TurboGears applications
    that needs JavaScript.

    It is based on code provided in
    http://trac.turbogears.org/turbogears/ticket/255 
    """

    javascript = [mochikit, JSLink("mochiinterpreter.javascript",
                                   "interpreter.js")]
    css = [CSSLink("mochiinterpreter.css", "interpreter.css")]

    template = """
    <div xmlns:py='http://purl.org/kid/ns#'>
    <script language="JavaScript" py:if="active">
    function interpreter() {
      if (!interpreter.box) {
        interpreter.box = document.createElement("div");
        interpreter.box.setAttribute('style',
                                     'background-color: white; ' +
                                     'border: solid black 3px; ' +
                                     'padding: 10px;' +
                                     'width: 610px;');
         document.body.appendChild(interpreter.box);
      }

      // Start Mochikit interpreter
      if (!(typeof(interpreterManager) == 'undefined')) {
        interpreterString = '<h5>Interactive Javascript Interpreter/Debugger</h5>' +
        '<form id="interpreter_form"><div id="interpreter_area"><div id="interpreter_output"></div></div>'+
        '<input id="interpreter_text" name="input_text" type="text" class="textbox" size="100" />'+
        '</form>';
        interpreter.box.innerHTML = interpreterString;
        interpreterManager.initialize();
      } else {
        interpreterString = '<h5>MochiKit Interactive Interpreter/Debugger Not Found</h5>';
        interpreter.box.innerHTML = interpreterString;
      }
    }
    </script>
    <div class='mochiinterpreter' py:if="active">
      <p><a href='javascript:window.interpreter()'>MochiKit Interpreter</a></p>
    </div>
    </div>
    """

    params = ['active']
    active = True


class MochiInterpreterDesc(WidgetDescription):
    name = "MochiKit Interpreter"

    template = """
    <div>
      ${for_widget.display()}
    </div>
    """

    def __init__(self, *args, **kw):
        super(MochiInterpreterDesc, self).__init__(*args, **kw)
        # Finally, below is how you declare your widget.
        self.for_widget = MochiInterpreter(
            name="mochiinterpreter_demo",
            )
