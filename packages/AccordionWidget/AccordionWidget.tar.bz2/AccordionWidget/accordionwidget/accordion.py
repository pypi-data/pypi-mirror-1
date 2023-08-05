import pkg_resources
import logging
import itertools
from turbogears import controllers, expose
from turbogears import widgets

log = logging.getLogger(".widgets.Accordion")
accordionAutoId = itertools.count()

class Accordion(widgets.Widget):
    """ Accordion Widget
    """
    template = "<div/>"
    css_dir =  pkg_resources.resource_filename("cookedeggs", "static/css")
    widgets.register_static_directory("css", css_dir)
    js_dir =  pkg_resources.resource_filename("cookedeggs", "static/javascript")
    widgets.register_static_directory("js", js_dir)    
    
    css = [widgets.base.CSSLink("css", "accordion/accordion.css"), widgets.base.CSSLink("js", "minikit/minikit.widget.css")]
    javascript = [widgets.base.mochikit, 
                    widgets.base.JSLink("js", "minikit/minikit.core.js"),
                    widgets.base.JSLink("js", "minikit/minikit.fx.js"),
                    widgets.base.JSSource(r"""
                                AccordionWidget = function() {
                                    makeAccordion(getElementsBySelector("a.toggler"), getElementsBySelector("div.accordion"), {hash: true});
                                    forEach(
                                        getElementsBySelector("div.toggler"),
                                        niftyRound
                                    );
                                };                                
                                addLoadEvent(AccordionWidget);
                    """)]
    params = params_copy = ["css_extra", "params_extra"]
    css_extra = []
    params_extra = []
    
    def __init__(self, *args, **kw):
        d = dict(**kw)
        if self.params.__len__() == self.params_copy.__len__():
            self.css.extend(d['css_extra'])
            self.params.extend(d['params_extra'])
            for k in d.keys():
                if isinstance(d[k], widgets.Widget):
                    self.javascript.extend(d[k].javascript)
                    self.css.extend(d[k].css)
                    #self.params.extend(d[k].params)
        super(Accordion, self).__init__(self, *args, **kw)
        print self.params
        
        
    def update_params(self, d):
        super(Accordion, self).update_params(d)

