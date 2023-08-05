import pkg_resources

import turbogears
from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               FormField, register_static_directory, JSSource
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

    js_head = JSSource(src = """
      function toggleinterpreter() {
        if ($('interpreterswitch')) {
          showElement('interpreter_form');
          $('interpreterswitch').id='interpreterswitchoff';
          $('interpreterswitchoff').innerHTML='Hide Interpreter';
        } else {
          hideElement('interpreter_form')
          $('interpreterswitchoff').id='interpreterswitch';
          $('interpreterswitch').innerHTML='Show Interpreter';
        }
      }
    """)

    javascript = [mochikit, JSLink("mochiinterpreter.javascript",
                                   "interpreter.js"), js_head]
    css = [CSSLink("mochiinterpreter.css", "interpreter.css")]

    template = """
    <div xmlns:py='http://purl.org/kid/ns#' py:if="active">
      <a id='interpreterswitch' onclick='toggleinterpreter()' href='#interpreterswitch'>Show Interpreter</a>
      <form id='interpreter_form' autocomplete='off'>
        <div id='interpreter_area'>
          <div id='interpreter_output'></div>
        </div>
        <div id='oneline'>
          <input id='interpreter_text' name='input_text' type='text' class='textbox' size='100' />
        </div>
        <div id='multiline'>
          <textarea id='interpreter_textarea' name='input_textarea' type='text' class='textbox' cols='97' rows='10'></textarea>
          <br />
        </div>
      </form>   
    </div>
    """

    params = ['active']
    active = True
    if turbogears.config.get("server.environment") != "development":
        # If we're not debugging, then we disable this widgeta s well.
        active = False


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
