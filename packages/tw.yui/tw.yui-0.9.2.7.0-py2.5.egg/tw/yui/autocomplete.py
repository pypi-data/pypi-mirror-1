from tw.api import JSLink

from tw.yui import YUICSSLink, YUIJSLink

autocomplete_css    = YUICSSLink(basename='assets/skins/sam/autocomplete', suffix='')
yui_dom_event_js    = YUIJSLink(basename='yahoo-dom-event/yahoo-dom-event', suffix='')
datasource_js       = YUIJSLink(basename='datasource/datasource')
get_js              = YUIJSLink(basename='get/get')
connection_js       = YUIJSLink(basename='connection/connection')
animation_js        = YUIJSLink(basename='animation/animation')
json_js             = YUIJSLink(basename='json/json')
yui_autocomplete_js = YUIJSLink(basename='autocomplete/autocomplete', 
                                css=[autocomplete_css],
                                javascript=[yui_dom_event_js, 
                                            datasource_js,
                                            get_js,
                                            connection_js,
                                            animation_js,
                                            json_js,]
                                )

autocomplete_js = JSLink(
    modname = 'tw.yui',
    filename = 'static/autocomplete/autocomplete.js',
    javascript = [yui_autocomplete_js]
)

from tw.forms import InputField

class AutoCompleteField(InputField):
    javascript = [autocomplete_js,]
    engine = "mako"
    template = "tw.yui.templates.autocomplete"
    params = ['url']
    url = '.json'