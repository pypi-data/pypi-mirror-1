from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from csci.images.portlets import csciimagesMessageFactory as _

from Products.CMFCore.utils import getToolByName
import random

class Icsciimages(IPortletDataProvider):
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

    portlet_title = schema.TextLine(title=_(u"Title"),
                                    description=_(u"The title of the portlet"),
                                    required=True,
                                    default=_(u"images"))
    
    image_folder = schema.TextLine(title=_(u"Image folder path from root"),
                                   description=_(u"master folder for images"),
                                   required=True,
                                   default=_(u"images"))

    images_number = schema.TextLine(title=_(u"Number of images to display"),
                                   description=_(u"number"),
                                   required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(Icsciimages)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""
    image_folder  = u"images"
    images_number = u"5"
    portlet_title = u"images"

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u"):
    #    self.some_field = some_field

    def __init__(self, image_folder=u"",
                 images_number=u"",
                 portlet_title=u""):
        self.image_folder = image_folder
        self.images_number = images_number
        self.portlet_title = portlet_title

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "CSCI Images"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('csciimages.pt')

    def title(self):
        return self.data.portlet_title
    
    def getimages(self):
        
        urltool = getToolByName(self.context, 'portal_url')
        portal = urltool.getPortalObject() 
        
        local_path = self.data.image_folder + '/'
        local_path += ('/').join(self.context.getPhysicalPath()[2:])
        local_path = local_path.lower()
        
        
        print local_path
        #get the directory with the images in
        try:
            image_folder = portal.restrictedTraverse(str(local_path))
        except:
            #no folder exists
            return None
        
        images_togo = []
        # get the images
        objects_avail = image_folder.contentValues()
        for obj in objects_avail:
            if obj.Type() == 'Image':             
                images_togo.append(obj)
                    
        #randomise the list
        random.shuffle(images_togo)

        return images_togo[:int(self.data.images_number)]


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(Icsciimages)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(Icsciimages)
