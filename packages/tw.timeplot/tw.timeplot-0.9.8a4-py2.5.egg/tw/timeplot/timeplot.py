from base import TimelineCSSLink, TimelineJSLink, JSLink

#class fonts_css(YUICSSLink):
#    basename="fonts/fonts"

class timeplot_js(TimelineJSLink):
    basename = "scripts/timeplot"
    javascript=[]
    css=[]

timeplot_js = timeplot_js()

class timeplot_api_js(TimelineJSLink):
    basename = "timeplot-api"
    javascript=[]
    css=[]

