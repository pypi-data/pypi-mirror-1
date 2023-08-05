"""
    AccordionWidget. Luigi S. Palese 2007
    
    This is in alpha state, so don't expect to see it 
    working very very well.
    
Install it by executing (as root if needed):    
    $ python setup.py develop     
    in the project's root dir and view the example in TG's toolbox.
"""

import pkg_resources
from turbogears import widgets, expose
#from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               #register_static_directory

js_dir = pkg_resources.resource_filename("accordionwidget",  "static/javascript")
widgets.register_static_directory("js", js_dir)
css_dir =  pkg_resources.resource_filename("accordionwidget", "static/css")
widgets.register_static_directory("css", css_dir)


class AccordionWidget(widgets.Widget):
    r"""
AccordionWidget makes use of Minikit Accordion function to build an 
accordion widget.  
Minikit is a collection of visual effects and widgets for 
javascript/html. 
I use Minikit because it is transparently compatible with mochikit. 
Go to http://candyscript.com/projects/minikit/ to know more.
    
AccordionWidget accepts follow parameters:
    template    -   The template we want to use containing any 
                        number of A/DIV pairs. 
                        The A element is called the toggler and the 
                        DIV contains the contents :-)
    ccs_extra   -   Any extra CCS to load with widget as TG CCSLink() 
                        widget
    params_extra - Any extra parameters to pass to the kid template. 
                        For instance if a kid template contains a ${w1} 
                        variable we need to add that to params_extra 
                        parameter list.
    """
    template = "<div/>"
    
    css = [widgets.base.CSSLink("js", "minikit/minikit.widget.css")]
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
        #
        if self.params.__len__() == self.params_copy.__len__():
            self.css.extend(d['css_extra'])
            self.params.extend(d['params_extra'])
            # Some hints: To make widgets display() method working in deeper widget injection
            for k in d.keys():
                if isinstance(d[k], widgets.Widget):
                    self.javascript.extend(d[k].javascript)
                    self.css.extend(d[k].css)
                    #self.params.extend(d[k].params)
        super(AccordionWidget, self).__init__(self, *args, **kw)
        
    def update_params(self, d):
        super(AccordionWidget, self).update_params(d)

        
class AccordionWidgetDesc(widgets.WidgetDescription):
    """AccordionWidget simple example."""
    template = """ 
    <div xmlns:py="http://purl.org/kid/ns#">
        ${for_widget.display()}
    </div>
    """
    
    name = "AccordionWidget simple example"
    full_class_name = "accordionwidget.AccordionWidget"
    def __init__(self, *args, **kw):
        super(AccordionWidgetDesc, self).__init__(*args, **kw)
        accordion_template = """
    <div id="accordiontest" xmlns:py="http://purl.org/kid/ns#">
        <div class="toggler" style="background:#A775F3;padding-left:1em;padding-right:1em;"><a class="toggler">${t1}</a></div>
        <div class="accordion">
        <div class="accordion_body">
            This example using a kid template fragment, but can be any kid template.<br/>
            In this example four accordion screen are defined and here we can have any kind of content.<br/> 
            For example, you can fill template with (any combination) <b>TG widgets</b>, too. <br/>
            Like that: ${c1.display()} <br/>
            And yes, really works !!!
        </div>
        </div>
        <div class="toggler" style="background:#A775F3;padding-left:1em;padding-right:1em"><a class="toggler">${t2}</a></div>
        <div class="accordion">
        Thanks to the <b>Minikit niftyRound</b> function for the rounded corners !!!
        </div>
        <div class="toggler" style="background:green;padding-left:1em;padding-right:1em"><a class="toggler">${t3}</a></div>
        <div class="accordion">
        <b>WOW</b> Experience !
        </div>    
        <div class="toggler" style="background:#A775F3;padding-left:1em;padding-right:1em"><a class="toggler">${t4}</a></div>
        <div class="accordion">
        <b>That's all folks !</b><br/>
        Does Someone want to help in development of this widget ? <a href="mailto:ultrabit@gmail.com" ><b>Send me yours enhancements !</b> </a>
        </div>    
    </div>
    """
        params_extra = ["t1","t2","t3","t4","t5", "c1"]
        c1= widgets.AutoCompleteField(name="state",  
                                     search_controller="turbogears.widgets.AutoCompleteField/search",  
                                     search_param="statename",  
                                     result_name="states")
   
        css_extra = [widgets.base.CSSLink("css", "accordion/accordion.css")]
        self.for_widget = AccordionWidget(template=accordion_template, params_extra=params_extra, css_extra=css_extra,
                                            t1="Title One - What's happen", 
                                            t2="Title Two - Isn't Cool ?",
                                            t3="Title Three - Great Visual Python lovers !!! ",
                                            t4="Title Four - Thanks ! ",
                                            c1=c1,
                                            )
