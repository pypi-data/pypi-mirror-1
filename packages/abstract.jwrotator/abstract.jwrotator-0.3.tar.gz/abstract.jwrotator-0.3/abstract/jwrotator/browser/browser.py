from Products.Five import BrowserView
from Products.CMFPlone.utils import getToolByName     
from zope.interface import Interface     
from zope import schema          
from Products.Five.formlib import formbase    
from zope.formlib import form          
from zope.app.annotation.interfaces import IAnnotations      
from Products.ATContentTypes.interface.topic import IATTopic         

global flashvars                                   
global default_values

default_values = {'height': '200', 'width': '400', 'shownavigation':'false', 'transition':'random' , 'rotatetime':5} 

class jwr_view(BrowserView):
    
    def __init__(self,context,request):
        self.context = context
        self.request = request         
        
    def test(self, condition, if_true, if_false):
	   if condition:
		return if_true
	   return if_false
		 
    def __getJS__(self):     
        annotated_obj = IAnnotations(self.context)    
        flashvars = {}
        keys = IJWRSettings.names()   
        try:                              
            for key in keys:
                flashvars[key] = annotated_obj[key]
        except:
             for key in keys:
                flashvars[key] = default_values[key]

        js = """<script type="text/javascript">
        		var s1 = new SWFObject("imagerotator.swf","rotator","%(width)s","%(height)s","7");
        		s1.addVariable("file","%(path)s/@@playlist");\n"""  % {'path':self.context.absolute_url(), 'width': flashvars['width'], 'height': flashvars['height']}  
        
        for var in flashvars.keys():
            js +=  's1.addVariable("%s","%s");\n' % (var,flashvars[var])
        js += 's1.write("container");\n</script>'
        
        return js     
        
   
class jwr_playlist_view(BrowserView):   
    
    def __init__(self,context,request):
        self.context = context
        self.request = request
    
    def __call__(self):     
        playlist =  "<playlist version='1' xmlns='http://xspf.org/ns/0/'>\n"
        playlist += "<trackList>\n"   
        if IATTopic.providedBy(self.context):
            images = self.context.queryCatalog()        
        else:                                    
            ct_tool = getToolByName(self.context, "portal_catalog")
            images = ct_tool(Type = 'Image', path = '/'.join(self.context.getPhysicalPath()))
        for image in images:         
            playlist += "\t<track>\n"
            playlist += "\t\t<title>%s</title>\n" % (image.Title,)
            playlist += "\t\t<location>%s</location>\n" % (image.getObject().absolute_url()) 
            playlist += "\t</track>\n"     
        
        playlist += "</trackList>\n"
        playlist += "</playlist>\n"   
        return playlist                                   
                            
class IJWRSettings(Interface):
    height = schema.TextLine(title=u'Height', required=False,)

    width = schema.TextLine(title=u'Width', required=False,)           

    shownavigation = schema.Choice(title=u"ShowNavigation", values = ['true','false'], default = 'true')     
       
    transition = schema.Choice(title=u"Transition", values = ['random','fade', 'bgfade', 'blocks', 'bubbles', 'circles', 'flash', 'fluids', 'lines' , 'slowfade'], default = 'random')     
    
    rotatetime = schema.Int(title=u"RotateTime", required = False)     
                           
class jwr_settings_form(formbase.PageForm):
    form_fields = form.FormFields(IJWRSettings)

    def __init__(self, context, request):
		"""View initialization"""
		self.request = request
		self.context = context                 
		   
    def setUpWidgets(self, ignore_request=False):
        """Manually set the widget values"""
        annotated_obj = IAnnotations(self.context)         
        keys = IJWRSettings.names()
        data = {}      
        try:                          
            for key in keys:
                data[key] = annotated_obj[key]
            self.widgets = form.setUpWidgets( self.form_fields, self.prefix, self.context, self.request, data=data, ignore_request=ignore_request)
    	except:
        	self.widgets = form.setUpWidgets( self.form_fields, self.prefix, self.context, self.request, ignore_request=ignore_request)
		                      
    @form.action("save settings")
    def save(self, action, data):       
        annotated_obj = IAnnotations(self.context)          
        for key in data.keys():
            annotated_obj[key] =  data[key]   

