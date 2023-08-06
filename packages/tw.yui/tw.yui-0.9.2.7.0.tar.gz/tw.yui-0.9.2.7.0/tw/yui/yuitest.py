from base import YUICSSLink, YUIJSLink

class fonts_css(YUICSSLink):
    basename="fonts/fonts"

class skin_css(YUICSSLink):
    basename="assets/skins/sam/skin"
    default_suffix=""

class logger_css(YUICSSLink):
    basename="logger/assets/skins/sam/logger"
    default_suffix=""

class yuitest_css(YUICSSLink):
    basename="yuitest/assets/skins/sam/yuitest"
    default_suffix=""

class yuiloader_dom_event_js(YUIJSLink):
    basename="yuiloader-dom-event/yuiloader-dom-event"
    default_suffix=''

class logger_js(YUIJSLink):
    basename = "logger/logger"
    css=[fonts_css(),logger_css()]

class profiler_js(YUIJSLink):
    basename="profiler/profiler"
    default_suffix='beta-min'

class profilerviewer_js(YUIJSLink):
    basename="profilerviewer/profilerviewer"
    default_suffix='beta-min'

class element_js(YUIJSLink):
    basename="element/element"
    default_suffix='beta-min'

class yuitest_js(YUIJSLink):
    basename = "yuitest/yuitest"
    javascript=[yuiloader_dom_event_js(), logger_js()]
    css=[fonts_css(), skin_css(), yuitest_css(), logger_css()]
