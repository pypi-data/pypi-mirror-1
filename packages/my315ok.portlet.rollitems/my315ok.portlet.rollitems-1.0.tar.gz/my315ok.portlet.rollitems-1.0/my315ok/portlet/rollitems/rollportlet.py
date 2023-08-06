import random
import time

from zope.interface import implements
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from Products.ATContentTypes.interface import IATTopic

from plone.portlet.collection import PloneMessageFactory as _a
from my315ok.portlet.rollitems import RollPortletMessageFactory as _

##class ICollectionPortlet(IPortletDataProvider):
class IRollPortlet(IPortletDataProvider):
    """A portlet which renders the results of a collection object.
    """

    header = schema.TextLine(title=_a(u"Portlet header"),
                             description=_a(u"Title of the rendered portlet"),
                             required=True)

    target_collection = schema.Choice(title=_a(u"Target collection"),
                                  description=_a(u"Find the collection which provides the items to list"),
                                  required=True,
                                  source=SearchableTextSourceBinder({'object_provides' : IATTopic.__identifier__},
                                                                    default_query='path:'))

    limit = schema.Int(title=_a(u"Limit"),
                       description=_a(u"Specify the maximum number of items to show in the portlet. "
                                       "Leave this blank to show all items."),
                       required=False)
                       
    random = schema.Bool(title=_a(u"Select random items"),
                         description=_a(u"If enabled, items will be selected randomly from the collection, "
                                        "rather than based on its sort order."),
                         required=True,
                         default=False)
                       
    show_more = schema.Bool(title=_a(u"Show more... link"),
                       description=_a(u"If enabled, a more... link will appear in the footer of the portlet, "
                                      "linking to the underlying Collection."),
                       required=True,
                       default=True)
                       
    show_dates = schema.Bool(title=_a(u"Show dates"),
                       description=_a(u"If enabled, effective dates will be shown underneath the items listed."),
                       required=True,
                       default=True)
    
    roll_images = schema.Bool(title=_(u"roll images"),
                       description=_(u"If enabled,  will be shown roll image items,else roll text items."),
                       required=True,
                       default=False)
    
    previewmode = schema.Choice(
        title=_(u"image size"),
        description=_(u"Choose source image size"),
        required = True,
        default = "thumb",
        vocabulary = 'rollitems.ImageSizeVocabulary' )
    
    roll_direc = schema.Choice(
        title=_(u"direction"),
        description=_(u"Choose the roll direction"),
        vocabulary = 'rollitems.RollDirectionVocabulary' )
    
    speed = schema.Int(title=_(u"speed"),
                       description=_(u"Specify the speed of the roll items "),                                      
                       required=True)
   
    roll_width = schema.Int(title=_(u"roll_width"),
                       description=_(u"Specify the width of the roll zone ."),
                       required=True)
    roll_height = schema.Int(title=_(u"roll_height"),
                       description=_(u"Specify the height of the roll zone ."),
                       required=True)
     

class Assignment(base.Assignment):
    """
    Portlet assignment.    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IRollPortlet)

    header = u""
    target_collection=None
    limit = 5
    random = False
    show_more = True
    show_dates = True
    speed = 35
    roll_width = 110
    roll_height = 70
    previewmode = u"thumb"
    roll_direc = u"top"
    roll_images = False

    def __init__(self, header=u"", target_collection=None, limit=None, random=False, show_more=True,
                 show_dates=False,speed=None,roll_width=None,roll_height=None,previewmode=None,roll_direc=None,roll_images=False):
        self.header = header
        self.target_collection = target_collection
        self.limit = limit
        self.random = random
        self.show_more = show_more
        self.show_dates = show_dates
        self.speed = speed
        self.roll_width = roll_width
        self.roll_height = roll_height
        self.previewmode = previewmode
        self.roll_direc = roll_direc
        self.roll_images = roll_images

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header


class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    _template = ViewPageTemplateFile('rollportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    # Cached version - needs a proper cache key
    # @ram.cache(render_cachekey)
    # def render(self):
    #     if self.available:
    #         return xhtml_compress(self._template())
    #     else:
    #         return ''

    render = _template

    @property
    def available(self):
        return len(self.results())

    def collection_url(self):
        collection = self.collection()
        if collection is None:
            return None
        else:
            return collection.absolute_url()
    @memoize
    def js_settings(self):
##        import pdb
##        pdb.set_trace()
        data = self.data
        out =  []
        jsOut = ''       
##        jsOut  += '\n var LinkDirection = "top";\n'
        jsOut  += '\n var rootdiv = "rootlink";\n'
        jsOut  += ' var son1 = "son1link";\n'
        jsOut  += ' var son2 = "son2link";\n'
        jsOut  += ' var collectScroll;\n'
        jsOut  += ' var Ltab;\n'
        jsOut  += ' var Ltab1;\n'
        jsOut  += ' var Ltab2;\n'
        jsOut  += ' var MyL;\n'  
        jsOut  += '\n var thelinkAutoScroll= new LinkAutoScroll();\n'              
        
        if self.results():
            for obj in self.results():                
                img = obj.getObject()
                Durl = img.absolute_url()
                Dtitle = img.Title()
                Dtime = img.Date()[:10]
                
                if data.roll_images:
##                    img.getImage()
##                    go2url=img.getLink2url()
                    jsOut += 'thelinkAutoScroll.addItem("%s/image_%s","","move_friendly_link","%s","%s","_blank");\n' % (Durl,data.previewmode,Durl,Dtitle)
                else:
                    jsOut += 'thelinkAutoScroll.addItem("","","move_friendly_link","%s","%s(%s)","_blank");\n' % (Durl,Dtitle,Dtime)
##                    jsOut += 'thelinkAutoScroll.addItem("","","move_friendly_link","'+ img.absolute_url()+'","'+img.Title()+'","_blank");\n'
                                                                                    
        jsOut  += 'thelinkAutoScroll.play();'
        out.append('<!--')
        out.append('var LinkDirection = "%s";' %data.roll_direc)
        out.append('var Isimage = "%s";' %data.roll_images)
        out.append('var Lspeed = %s;' %data.speed)
        out.append('var LAWidth = %s;' %data.roll_width)
        out.append('var LAHeight = %s;' %data.roll_height)       
        out.append(jsOut)            
        out.append('-->')
        return '\n'.join(out)

    def results(self):
        """ Get the actual result brains from the collection. 
            This is a wrapper so that we can memoize if and only if we aren't
            selecting random items."""
        if self.data.random:
            return self._random_results()
        else:
            return self._standard_results()

    @memoize
    def _standard_results(self):
        results = []
        collection = self.collection()
        if collection is not None:
            results = collection.queryCatalog()
            if self.data.limit and self.data.limit > 0:
                results = results[:self.data.limit]
        return results
        
    # intentionally non-memoized
    def _random_results(self):
        results = []
        collection = self.collection()
        if collection is not None:
            """
            Kids, do not try this at home.
            
            We're poking at the internals of the (lazy) catalog results to avoid
            instantiating catalog brains unnecessarily.
            
            We're expecting a LazyCat wrapping two LazyMaps as the return value from
            Products.ATContentTypes.content.topic.ATTopic.queryCatalog.  The second
            of these contains the results of the catalog query.  We force sorting
            off because it's unnecessary and might result in a different structure of
            lazy objects.
            
            Using the correct LazyMap (results._seq[1]), we randomly pick a catalog index
            and then retrieve it as a catalog brain using the _func method.
            """
            
            results = collection.queryCatalog(sort_on=None)
            limit = self.data.limit and min(len(results), self.data.limit) or 1
            try:
                results = [results._seq[1]._func(i) for i in random.sample(results._seq[1]._seq, limit)]
            except AttributeError, IndexError:
                # This handles the cases where the lazy objects returned by the catalog
                # are structured differently than expected.
                results = []
        return results
        
    @memoize
    def collection(self):
        """ get the collection the portlet is pointing to"""
        
        collection_path = self.data.target_collection
        if not collection_path:
            return None

        if collection_path.startswith('/'):
            collection_path = collection_path[1:]
        
        if not collection_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(collection_path, default=None)
        
class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRollPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    
    label = _a(u"Add Collection Portlet")
    description = _a(u"This portlet display a listing of items from a Collection.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    form_fields = form.Fields(IRollPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    label = _a(u"Edit Collection Portlet")
    description = _a(u"This portlet display a listing of items from a Collection.")
