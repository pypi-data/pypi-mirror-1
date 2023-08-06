from Products.CMFCore.utils import getToolByName
from plone.browserlayer import utils
import string
from AccessControl import getSecurityManager
from Acquisition import aq_parent


def nav_init(context, basePath=None, update_titles=False):

    #get stie catalog
    urltool = getToolByName(context, 'portal_url')
    catalog = getToolByName(context, 'portal_catalog')

#params
    levels = 1       #for each directory, only include the children
    types=None       #list of types of items to include
#init
    nav_dir = {}     #Dict of path locations and new properties
    nav_list = []    #list of directories to search
                     #  initially only site root, but child dirs get added in first loop
    nav_status = 'Started...\n'

    # if no base path is given, use the portal root
    print basePath
    if basePath is None:
        basePath = urltool.getPortalPath()
        print '----this works----'
    elif basePath == 'None':
        basePath = urltool.getPortalPath()      
    elif basePath == '':
        basePath = urltool.getPortalPath()
    print basePath
    
    #add it to the list of directories to index
    nav_list.append(basePath)
    
    nav_status = nav_status + 'Update from: ' + basePath 
    
    #loop over all the paths in the navigation list (gets updated within loop)
    for nav_item in nav_list:

        basePath = nav_item
        
        #------creates query dictionary-----------
        query = {}
        query['sort_on'] = 'getObjPositionInParent'
        if levels is not None and levels > 0:
            query['path'] = {'query' : basePath, 'depth' : levels}
        else:
            query['path'] = basePath

        if types:
            query['portal_type'] = types
        #
        # query 'sort_on'     : 'getObjPositionInParent'               ---action
        #       'path'        : { 'query' : '/portal_root/directory'   ---location
        #                         'depth' : '1' }                      ---optional entry -depth of search for each folder
        #       'portal_type' : ['Folder', 'Document', 'ATFolder']     ---optional list  -types of files to index
        #                             #---------run the search -------------   
        results = catalog.searchResults(query)
        # --------portal catalog searched-------------        
        
        #the base path is the key of the dict, each entry is a list of link properties
        nav_dir[basePath] = []

        #add the 'back' link (where appropriate):
        app = context.restrictedTraverse(basePath)
        if ('/'+str(app.virtual_url_path())) == urltool.getPortalPath():
            pass #if we are in the portal root
        else:
            parent = aq_parent(app)
            nav_dir[str(basePath)].append(['- Back -',app.Title,app.Type,parent.absolute_url()])
        
        #loop over search results
        for r in results:
            #use the path to transform the item's filename into link name:
            link_name = r.getPath()
            link_name = link_name.split('/')
            link_name = link_name[-1]         #use the 'word' following last '/'
            link_name = link_name.split('.')
            link_name = link_name[0]          #cut off any file extensions
            link_name = link_name.split('-')  #split words separated by '-' into list for capitalisation
            i=0
            for word in link_name:
                word = word.capitalize()
                link_name[i] = word          # capilalise words
                i+=1            
            
            link_name = string.join(link_name)  #re-construct the string with spaces
            
            #construct the list of properties
            app = context.restrictedTraverse(r.getPath()) # chechout the object
            obj_viewed = [x for x in app.permissionsOfRole('Anonymous') if x['name']=='View']
            if obj_viewed[0]['selected'] == 'SELECTED':
                nav_dir[str(basePath)].append([link_name,r.Title,r.Type,r.getURL()])
            else:
                pass
            
            #-----------now update the objects title using the files name-----------
            if update_titles:
                #grabs the zope object by path

                app.setTitle(link_name) # rename
                app.reindexObject() # update the zope indexing
  
            #If the item is a folder, add it to the list of folders to be scanned.
            if r.Type == "Folder" or r.Type == "Large Folder":
                nav_list.append(r.getPath())
                basePath


        
#    getSecurityManager().checkPermission(permission, object)
    
    nav_status = nav_status + 'Re-Indexing and Renaming Complete' 
    return nav_status, nav_dir







