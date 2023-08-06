from base import TimelineCSSLink, TimelineJSLink, JSLink

#class fonts_css(YUICSSLink):
#    basename="fonts/fonts"

class timeline_api_js(TimelineJSLink):
    basename = "timeline-api"
    javascript=[]
    css=[]

demo_js = JSLink(modname=__name__, filename="static/2.2.0/demo.js")