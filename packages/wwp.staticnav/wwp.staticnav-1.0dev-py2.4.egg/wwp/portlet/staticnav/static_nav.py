from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from wwp.portlet.staticnav import static_navMessageFactory as _

#our added bits
from Acquisition import aq_inner  #to get context
from Products.CMFCore.utils import getToolByName
import string
from nav_lib import nav_init
from Persistence import Persistent



class nav_store(Persistent):
    def __init__(self):
        # these objects will be stored by zope persistently!
        self.nav_dir = {}




class Istatic_nav(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)

    staticNav_fields = schema.TextLine(
                                 title=_(u"Create Navigation Structure"),
                                 description=_(u"Enter the directory from where the navigation starts"),
                                 required=False)
    run_nav_search = schema.Bool(
                                 title=_(u"Run indexing now?"),
                                 required=False,
                                 default=True)
    update_titles = schema.Bool(
                                 title=_(u"Globally rename objects from filenames"),
                                 required=False,
                                 default=False)
    
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
#    self.context = 'hello'


    implements(Istatic_nav)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""
    run_nav_search = True
    global_nav_dir = nav_store()
    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self, staticNav_fields=u'', 
                       run_nav_search=True,
                       update_titles=False):
        self.staticNav_fields = str(staticNav_fields)
        self.run_nav_search = run_nav_search
        self.update_titles = update_titles


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Static Navigation"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('static_nav.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        nav_status = '.'

        #this covers the case where zope is reset (and dictionary is lost)
        if len(self.data.global_nav_dir.nav_dir)==0:
            self.data.run_nav_search = True
            print '-------navigation dict is blank--------'
        else:
            pass
        if self.data.run_nav_search is True:
            nav_status,nav_dir=nav_init(context,
                                        self.data.staticNav_fields,
                                        self.data.update_titles)
            
            #update changes and append new entries to presistent site dictionary
            for item in nav_dir.iterkeys():
                if self.data.global_nav_dir.nav_dir.has_key(item):
                    self.data.global_nav_dir.nav_dir[item] = nav_dir[item]
                else:
                    self.data.global_nav_dir.nav_dir[item] = nav_dir[item]
            print '-------index updated--------'
        self.nav_status=nav_status
        self.data.run_nav_search = False #only run once per unstall
        
        
        
    def view_nav(self):
        #-------------The actual view of portlet-------------------------------------------------------
        context = aq_inner(self.context)
        
        #construct nav_dir key from path (to get folder location)
        #  there is an issue with special folders such as news and events (aggregator)
        if context.isPrincipiaFolderish == 1:
            path_key = string.join(context.getPhysicalPath(),'/')
        else:
            i=1
            path_key = ''
            while i<(len(context.getPhysicalPath())-1):
                items = context.getPhysicalPath()
                path_key = path_key + '/' + items[i]
                i+=1
        #----------------------------------------------------------------------------------------------
        
        # construct the output for tal --> a list of links, which have dicts with name and linkURL:
        navoutput = []
        for navitem in self.data.global_nav_dir.nav_dir[path_key]:
            itemdict={}
            itemdict['name'] = navitem[0]
            itemdict['linkURL'] = navitem[3]
            navoutput.append(itemdict)
        return navoutput
        #






class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(Istatic_nav)

    def create(self, data):
        return Assignment(**data)


# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()


# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(Istatic_nav)
    



