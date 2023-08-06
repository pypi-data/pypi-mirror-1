import pkg_resources

from turbogears import expose

from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory, JSSource

static_dir = pkg_resources.resource_filename("dominclude",
                                         "static")
register_static_directory("dominclude", static_dir)
dominc_css = CSSLink("dominclude", "css/DOMinclude.css")
dominc_js = JSLink("dominclude", "javascript/DOMinclude.js")

class DOMincConfig(JSSource):
    """Configuration for DOMinclude. When creating this widget,
    you can specify frame_size (example '[320,180]' for 320 width,
    and 180 height), display_prefix which is shown when the popup
    is displayed (default "Hide "), popup_class, open_popup_link_class,
    image_types (default "jpg|JPG|JPEG|jpeg|gif|GIF|png|PNG") and
    trigger_class (the name of the CSS class that is used to find links
    to change).
    """

    def __init__(self, trigger_class="DOMpop", popup_class="popup",
        open_popup_link_class="popuplink", display_prefix="Hide ",
        image_types="jpg|JPG|JPEG|jpeg|gif|GIF|png|PNG",
        frame_size="[320,180]"):
        src = """
    DOMinccfg={
    // CSS classes
    // trigger DOMinclude
      triggerClass:'%s',
    // class of the popup
      popupClass:'%s',
    // class of the link when the popup
    // is open
      openPopupLinkClass:'%s',
    // text to add to the link when the
    // popup is open
      displayPrefix:'%s',
    // filter to define which files should
    // not open in an iframe
      imagetypes:'%s',
    // dimensions of the popup
      frameSize:%s
    }
""" % (trigger_class, popup_class, open_popup_link_class, display_prefix,
    image_types, frame_size)
        super(DOMincConfig, self).__init__(src)

class DOMincConfigDesc(WidgetDescription):
    for_widget = DOMincConfig()
    template = "<div>Configuration for the DOMinclude widget.</div>"
    full_class_name = "dominclude.DOMincConfig"

default_config = DOMincConfig()

class DOMinclude(Widget):
    """Creates a DOM-based "popup" window when a link is clicked.
    You can pass in a DOMincConfig instance as 'config' to change
    the settings. You can also pass in your own CSS. You must only
    use one DOMincConfig per page, otherwise you will get
    unpredictable results.
    """

    params = ["href", "text"]
    params_doc = dict(href="URL of the resource to display on click",
        text="Text of the link to be displayed")
    template = """<a href="${href}" class="DOMpop">${text}</a>"""

    def __init__(self, config=default_config, css=dominc_css, **params):
        if isinstance(css, Widget):
            css = [css]
        self.css = css
        self.javascript = [config, dominc_js]
        super(DOMinclude, self).__init__(**params)

class DOMincludeDesc(WidgetDescription):
    for_widget = DOMinclude()
    template = """<div>Need to do a
    ${for_widget.display(href='http://www.google.com/', text='Google search')}?
    How about the ${for_widget.display(href='dominclude.DOMinclude/answer', text='answer')} to the
    ultimate question of life, the universe and everything?
    </div>
    """
    full_class_name = "dominclude.DOMinclude"

    @expose()
    def answer(self):
        return "42"
