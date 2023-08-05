import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory

from scriptaculous import prototype_js, scriptaculous_js

from turbojson import jsonify

js_dir = pkg_resources.resource_filename("div_dialogs", "static/javascript")
register_static_directory("div_dialogs.js", js_dir)

css_dir = pkg_resources.resource_filename("div_dialogs", "static/css")
register_static_directory("div_dialogs.css", css_dir)

js_dir = 'div_dialogs.js'
css_dir = 'div_dialogs.css'
themes_dir = css_dir + '/themes'

dimming_div_js = JSLink(js_dir, 'dimmingdiv.js')
dimming_div_css = CSSLink(css_dir, 'dimming.css')

class DialogBox(Widget):
    javascript = [dimming_div_js, scriptaculous_js]
    
    css = [dimming_div_css]
    
    template = """
    <script xmlns:py="http://purl.org/kid/ns#" type="text/javascript">
        function show_${dom_id}_window() {
            open_dialog('${dom_id}', '${title}', '${width}', '${height}', ${x}, ${y}, ${modal and 'true' or 'false'}, '${on_open}', '${on_close}');
        }
        ${dom_id}_window = {show: show_${dom_id}_window};
        <div py:if="show" py:strip="True">
        ${dom_id}_window.show();
        </div>
    </script>
    """
    
    params = ['dom_id', 'title', 'width', 'height', 'x', 'y',
              'modal', 'show', 'on_open', 'on_close']
    
    params_doc = {'dom_id': 'ID of the DOM object that will be converted to ' \
                            'a dialog box'}
                  
    title = ''
    width = 400
    height = 200
    x = -1
    y = -1
    modal = False
    show = False

class DialogBoxLink(Widget):
    javascript = [dimming_div_js, scriptaculous_js]
    
    css = [dimming_div_css]
    
    template = """
    <span xmlns:py="http://purl.org/kid/ns#">
        <a href="javascript:open_dialog('${dom_id}', '${title}', '${width}', '${height}', ${x}, ${y}, ${modal and 'true' or 'false'}, '${on_open}', '${on_close}')">
            ${link_text}
        </a>
    </span>
    """
    
    params = ['dom_id', 'link_text', 'title', 'width', 'height', 'x', 'y',
              'modal', 'on_open', 'on_close']
    
    params_doc = {'dom_id': 'ID of the DOM object that will be converted to ' \
                            'a dialog box'}
                  
    title = ''
    width = 400
    height = 200
    x = -1
    y = -1
    modal = False

class DialogBoxLinkDescription(WidgetDescription):
    for_widget = DialogBoxLink()
    name = "Dialog Box Link"
    template = """
        <div xmlns:py="http://purl.org/kid/ns#">
            Click ${for_widget.display(link_text='here', title='Greetings!', dom_id='dialog_box',)}
            to open the dialog.<br/>
            Click ${for_widget.display(link_text='here', title='Greetings!', dom_id='dialog_box', modal=True)}
            to see the modal version.
            <div id="dialog_box" style="position: absolute; visibility: hidden;">
                <h1>Hello there!</h1>
            </div>
        </div>
    """

window_js = JSLink(js_dir, 'window.js')
window_ext_js = JSLink(js_dir, 'window_ext.js')
debug_js = JSLink(js_dir, 'debug.js')
default_css = CSSLink(themes_dir, 'default.css')
alphacube_css = CSSLink(themes_dir, 'alphacube.css')

class BaseWindow(Widget):
    template = """
    <script xmlns:py="http://purl.org/kid/ns#" type="text/javascript">
        ${id} = new Window('${id}', ${options});
        function display(e) {
            ${id}.toFront();
            ${id}.setContent('${dom_id}',
                             ${inherit_dimensions and 'true' or 'false'},
                             ${inherit_position and 'true' or 'false'});
            <div py:if="show" py:strip="True">${id}.${show_func}(${modal and 'true' or 'false'});</div>
        }
        Event.observe(window, 'load', display);
    </script>
    """
    
    css = [CSSLink(themes_dir, 'default.css'),
           CSSLink(themes_dir, 'alphacube.css')]
    javascript = [prototype_js, window_js]
    
    params = ['dom_id', 'link_text', 'title', 'width', 'height', 'x', 'y',
              'modal', 'on_open', 'on_close', 'centered', 'resizable',
              'show', 'theme', 'minimizable', 'maximizable', 'closable',
              'draggable', 'wired_drag']
    
    # -1 means autosizing
    width = -1
    height = -1
    
    # -1 means autopositioning
    x = -1
    y = -1
    
    static = True
    show = False
    
    title = ''
    centered = False
    modal = False
    resizable = True
    minimizable = True
    maximizable = True
    draggable = True
    closable = True
    theme = 'alphacube'
    wired_drag = False
    
    def get_options(self, d):
        opt = dict()
        
        if d['centered']:
            opt['show_func'] = 'showCenter'
        else:
            opt['show_func'] = 'show'
        
        opt['className'] = d['theme']
        opt['wiredDrag'] = d['wired_drag']
        
        for i in ['minimizable', 'maximizable', 'closable', 'theme',
                  'title', 'draggable']:
            opt[i] = d[i]
        
        if d.get('x') >= 0 or d.get('y') >= 0:
            d['inherit_position'] = False
            opt['left'] = int(d['x'])
            opt['top'] = int(d['y'])
        else:
            d['inherit_position'] = True
        
        if d.get('width') >= 0 or d.get('height') >= 0:
            d['inherit_dimensions'] = False
            opt['height'] = int(d['height'])
            opt['width'] = int(d['width'])
        else:
            d['inherit_dimensions'] = True
        return opt
    
    def update_params(self, d):
        super(BaseWindow, self).update_params(d)
        d['options'] = jsonify.encode(self.get_options(d))
        d['id'] = d['dom_id'] + '_window'

class AjaxWindow(BaseWindow):
    template = """
    <script xmlns:py="http://purl.org/kid/ns#" type="text/javascript">
        ${id} = new Window('${id}', ${options});
        function init(e) {
            ${id}.toFront();
            <div py:if="show" py:strip="True">${id}.${show_func}(${modal and 'true' or 'false'});</div>
        }
        Event.observe(window, 'load', init);
    </script>
    """
    params = ['url']
    def get_options(self, d):
        opt = super(AjaxWindow, self).get_options(d)
        opt['url'] = d['url']
        return opt

class Window(BaseWindow):
    template = """
    <script xmlns:py="http://purl.org/kid/ns#" type="text/javascript">
        ${id} = new Window('${id}', ${options});
        function init(e) {
            ${id}.toFront();
            ${id}.setContent('${dom_id}',
                             ${inherit_dimensions and 'true' or 'false'},
                             ${inherit_position and 'true' or 'false'});
            <div py:if="show" py:strip="True">${id}.${show_func}(${modal and 'true' or 'false'});</div>
        }
        Event.observe(window, 'load', init);
    </script>
    """

class WindowDescription(WidgetDescription):
    for_widget = Window()
    name = "Window"
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        <div id="my_window" style="width: 300px">
            This is a div.<br/>
            This is a div.<br/>
            This is a div.<br/>
            This is a div.<br/>
            <form>
                 Test: <input type="text" />
            </form>
        </div>
        ${for_widget.display(dom_id='my_window', show=True)}
    </div>
    """
    show_separately = True

class StaticWindow(Widget):
    template = """
    <div xmlns:py="http://purl.org/kid/ns#">
        Static window goes here
    </div>
    """

class StaticWindowDescription(Widget):
    for_widget = StaticWindow()


   