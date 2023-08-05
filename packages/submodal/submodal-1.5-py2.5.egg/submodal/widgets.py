import pkg_resources

from turbogears import widgets
from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory


static_dir = pkg_resources.resource_filename("submodal",
                                             "static")

register_static_directory("submodal", static_dir)

submodal_css = CSSLink("submodal", "css/subModal.css")
submodal_js = [JSLink("submodal", "javascript/subModal.js",
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

    css = [submodal_css]
    javascript = submodal_js

    def __init__(self, *args, **kwargs):
        super(SubModal, self).__init__(*args, **kwargs)


class SubModalDesc(WidgetDescription):
    for_widget = SubModal()
    template = """
    <div>
      <script type='text/javascript'>
      var callback_test_function = function (returnVal) {
          alert('This is a callback!');
          alert(returnVal);
      }
      </script>
      <p>SubModal Testing.</p>
      <p><a href='http://www.turbogears.org' class='submodal'>
         Click Here for a SubModal Window (just using the class is enough ;-))
         </a></p>
      <p><a href='/tg_widgets/submodal/html/testing.html'
         onclick='showPopWin("/tg_widgets/submodal/html/testing.html",
                             500, 300, callback_test_function);
                  return false;'>
         Click Here for a SubModal Window with a CallBack Function</a></p>
    </div>
    """
