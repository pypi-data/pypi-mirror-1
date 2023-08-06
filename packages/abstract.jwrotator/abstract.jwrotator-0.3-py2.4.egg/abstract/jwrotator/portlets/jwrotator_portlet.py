from plone.portlet.collection.collection import Renderer as collectionRenderer        
from plone.portlet.collection.collection import Assignment as collectionAssignment          
from plone.portlet.collection.collection import AddForm as collectionAddForm        
from plone.portlet.collection.collection import ICollectionPortlet as collectionPortletInterface
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile      
from zope.interface import implements           
import random

global default_values 
default_values = {'height': '155', 'width': '155', 'shownavigation':'false', 'transition':'random' , 'rotatetime':5} 

class IJWRotatorPortlet(collectionPortletInterface):
    """ docstring """
                                         
class JWRotatorRenderer(collectionRenderer):
    """Portlet renderer.
    """
    render = ViewPageTemplateFile('jwrotator_portlet.pt')         
    
    def __init__(self, *args): 
        collectionRenderer.__init__(self, *args)
        self.container_id = random.randint(1,100)
           
    def __getJS__(self):  
        js = """<script type="text/javascript">
          		var s1 = new SWFObject("imagerotator.swf","rotator","%(width)s","%(height)s","7");
          		s1.addVariable("file","%(path)s/@@playlist");\n"""  % {'path':self.collection_url(), 'width': default_values['width'], 'height': default_values['height']}  

        for var in default_values.keys():
            js +=  's1.addVariable("%s","%s");\n' % (var,default_values[var])
        js += 's1.write("%s");\n</script>' % (self.getPortletContainerId(), )

        return js            
    
    def getPortletContainerId(self):
        id = '%s-%s' % (self.collection().getId(), self.container_id)
        return id
    
class JWRotatorAssignment(collectionAssignment):         
    """ docstring"""                                   
    implements(IJWRotatorPortlet)                       
          
class JWRotatorAddForm(collectionAddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """

    def create(self, data):
        return JWRotatorAssignment(**data)
 
