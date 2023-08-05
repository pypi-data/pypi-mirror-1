import pkg_resources

from turbogears import widgets
from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory


static_dir = pkg_resources.resource_filename("submodal",
                                             "static")

register_static_directory("submodal", static_dir)

submodal_css = CSSLink("submodal", "css/subModal.css")
submodal_js = [JSLink("submodal", "javascript/common.js",
                      location = widgets.js_location.bodytop),
               JSLink("submodal", "javascript/subModal.js",
                      location = widgets.js_location.bodytop)]

__all__ = [
    'SubModal',
    ]


class SubModal(Widget):
    """
The subModal works by placing a semi-transparent div over the browser,
blocking access to the content below while still providing
visibility. This maintains state and doesn't make someone feel
disoriented or lost by moving them completely to another page. Their
frame of reference is kept while allowing them to perform a new task
(usually closely associated with the content below).
    """

    template = '''
    <div id="popupContainer">
      <div id="popupInner">
        <div id="popupTitleBar">
          <div id="popupTitle"></div>
          <div id="popupControls">
            <img src="${img_close}" onclick="hidePopWin(${hide_pop_win});" />
          </div>
        </div>
        <iframe src="${iframe_src}" 
                style="width:100%;height:100%;background-color:transparent;"
                scrolling="auto" frameborder="0" 
                allowtransparency="true" id="popupFrame" 
                name="popupFrame" width="100%" height="100%">
        </iframe>
      </div>
    </div>
    '''

    css = [submodal_css]
    javascript = submodal_js


    params = ['img_close', 'hide_pop_win', 'iframe_src']
    params_doc = {
        'img_close':'URL for the close image',
        'iframe_src':'HTML that will be used as IFRAME',
        'hide_pop_win':"Use 'true' if you're using a callback function",
        }

    img_close = '/tg_widgets/submodal/images/close.gif'
    iframe_src = '/tg_widgets/submodal/html/loading.html'
    hide_pop_win = 'false'

    def __init__(self, *args, **kwargs):
        super(SubModal, self).__init__(*args, **kwargs)


class SubModalDesc(WidgetDescription):
    for_widget = SubModal()
    template = """
    <div>
      <script type="text/javascript">
      var callback_test_function = function (returnVal) {
          alert('This is a callback!');
          alert(returnVal);
      }
      </script>
      <p>SubModal Testing.</p>
      <p><a href="http://www.turbogears.org"
         onclick="showPopWin('http://www.turbogears.org', 500, 300);
                  return false;">
         Click Here for a SubModal Window</a></p>
      <p><a href="/tg_widgets/submodal/html/testing.html"
         onclick="showPopWin('/tg_widgets/submodal/html/testing.html',
                             500, 300, callback_test_function);
                  return false;">
         Click Here for a SubModal Window with a CallBack Function</a></p>
      <!-- Insert this at the bottom of your page... -->
      ${for_widget(hide_pop_win='true')}
    </div>
    """
