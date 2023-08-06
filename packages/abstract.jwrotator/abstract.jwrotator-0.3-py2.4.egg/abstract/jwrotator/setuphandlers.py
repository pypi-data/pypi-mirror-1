from Products.CMFPlone.utils import getToolByName

def addViewMethod(context):          
    site = context.getSite()            
    type_tool = getToolByName(site,'portal_types')           
    view_types = ['Folder','Topic','Large Plone Folder']       
    for view_type in view_types: 
        folder_view_methods = list(type_tool[view_type].view_methods)
        if 'jwrotator_view' not in folder_view_methods:
            folder_view_methods.append('jwrotator_view')
            type_tool[view_type].view_methods = tuple(folder_view_methods)
    
    