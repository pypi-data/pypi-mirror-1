from turbogears.widgets import CSSSource
from turbogears.view import load_engines

from dominclude import DOMincConfig, DOMinclude
from dominclude.widgets import dominc_js, dominc_css

def test_dominc_config():
    load_engines()
    config = DOMincConfig()
    output = config.render()
    print output
    assert """
    DOMinccfg={
    // CSS classes
    // trigger DOMinclude
      triggerClass:'DOMpop',
    // class of the popup
      popupClass:'popup',
    // class of the link when the popup
    // is open
      openPopupLinkClass:'popuplink',
    // text to add to the link when the
    // popup is open
      displayPrefix:'Hide ',
    // filter to define which files should
    // not open in an iframe
      imagetypes:'jpg|JPG|JPEG|jpeg|gif|GIF|png|PNG',
    // dimensions of the popup
      frameSize:[320,180]
    }
""" in output

def test_dominc_custom_config():
    load_engines()
    config = DOMincConfig(trigger_class="1", popup_class="2",
        open_popup_link_class="3", display_prefix="4",
        image_types="5", frame_size = "[2,4]")
    output = config.render()
    print output
    assert """DOMinccfg={
    // CSS classes
    // trigger DOMinclude
      triggerClass:'1',
    // class of the popup
      popupClass:'2',
    // class of the link when the popup
    // is open
      openPopupLinkClass:'3',
    // text to add to the link when the
    // popup is open
      displayPrefix:'4',
    // filter to define which files should
    // not open in an iframe
      imagetypes:'5',
    // dimensions of the popup
      frameSize:[2,4]
    }
""" in output

def test_dominclude_js():
    popup = DOMinclude()
    assert popup.javascript == [DOMincConfig(), dominc_js]

def test_dominclude_custom_js():
    config = DOMincConfig(trigger_class="foo")
    popup = DOMinclude(config=config)
    assert popup.javascript == [config, dominc_js]

def test_dominclude_render():
    load_engines()
    popup = DOMinclude()
    output = popup.render(href="/foo/bar", text="My Link Text")
    print output
    assert output == '<a href="/foo/bar" class="DOMpop">My Link Text</a>'

def test_dominclude_css():
    popup = DOMinclude()
    assert popup.css == [dominc_css]

def test_dominclude_custom_css():
    css = CSSSource("popup { font-weight: bold }")
    popup = DOMinclude(css = css)
    assert popup.css == [css]
