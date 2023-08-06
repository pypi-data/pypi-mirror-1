# from zope.interface import Interface

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

# from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.image import ImagePortletMessageFactory as _

from collective.namedfile import field
from collective.namedfile.widget import NamedImageWidget

class IImagePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    image = field.NamedImage(title=u'Image field',
                         description=_(u"An image in top of the portlet"),
                         required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IImagePortlet)

    image = None


    def __init__(self, image=None):
       self.image = image

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Image portlet"
    
    

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('imageportlet.pt')


    @property
    def image_tag(self):
        """
        Construct an image tag if possible...
        TODO: not sure about the approach yet 
        
        self.image.filename might be of interest
        but I have problems figuring out how to get the context/request of
        the portlet if possible at all ?
        
        getMultiAdapter((self.context, self.request), name="plone_context_state")
        and then ..++contextportlets++... as done in http://dev.plone.org/collective/browser/collective.portlet.feedmixer/trunk/collective/portlet/feedmixer/portlet.py


        135	    def more_url(self):
        136	        state=getMultiAdapter((self.context, self.request), name="plone_context_state")
        137	        folder=state.folder()
        138	        return "%s/++contextportlets++%s/%s/full_feed" % \
        139	                (folder.absolute_url(),
        140	                 self.manager.__name__,
        141	                 self.data.__name__)


        I had expected something like this:
        
        http://www.plone.local:8080/++contextportlets++plone.rightcolumn/<portlet id like image-portlet>/<field name image>/<image name with extension>
        
        in edit mode its like that -->
        
        <site>/++contextportlets++plone.rightcolumn/image-portlet/edit/@@file/image/<image name with extension>

        I can reproduce that, but this only works whenlogged in.
        
        I have tried 
        

        <site>/++contextportlets++plone.rightcolumn/image-portlet/view/@@file/image/<image name with extension>        
        <site>/++contextportlets++plone.rightcolumn/image-portlet/@@file/image/<image name with extension>
        but just gets 404 for these....
        

        """
        #TODO: move import to top if import
        from zope.component import getMultiAdapter
        state=getMultiAdapter((self.context, self.request), name="plone_context_state")
        folder=state.folder()
        return '<img src="%s/++contextportlets++%s/%s/edit/@@file/image/%s" />' % \
            (folder.absolute_url(),
            self.manager.__name__,
            self.data.__name__,
            self.data.image.filename)


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IImagePortlet)
    form_fields['image'].custom_widget = NamedImageWidget


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
    form_fields = form.Fields(IImagePortlet)
    form_fields['image'].custom_widget = NamedImageWidget

