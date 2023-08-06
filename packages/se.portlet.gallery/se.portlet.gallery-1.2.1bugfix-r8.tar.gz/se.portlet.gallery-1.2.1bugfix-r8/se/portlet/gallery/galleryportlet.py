from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey


from Acquisition import aq_inner
from DateTime.DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from random import shuffle
import random 
from se.portlet.gallery import GalleryPortletMessageFactory as _


from types import UnicodeType
_default_encoding = 'utf-8'

def _encode(s, encoding=_default_encoding):
    try:
        return s.encode(encoding)
    except (TypeError, UnicodeDecodeError, ValueError):
        return s
    
def _decode(s, encoding=_default_encoding):
    try:
        return unicode(s, encoding)
    except (TypeError, UnicodeDecodeError, ValueError):
        return s




class IGalleryPortlet(IPortletDataProvider):


    name = schema.TextLine(title=_(u"Title"),
                        description=_(u"The title of the gallery. Leave blank to not display the title."),
                        default=u'',
                        required=False
                        )
                        
    width = schema.Int(title=_(u'Width of the portlet'),
                        description=_(u'Width in pixels. Enter 0 to allow default portlet width.'),
                        required=True,
                        default=0
                        )
    
    height = schema.Int(title=_(u'Height of the portlet'),
                        description=_(u'Height in pixels.'),
                        required=True,
                        default=128
                        )
                        
    omit_border = schema.Bool(title=_(u"Omit portlet border"),
                        description=_(u"Tick this box if you want to render the text above without the standard header, border or footer."),
                        required=True,
                        default=False
                        )

    display_desc = schema.Bool(title=_(u"Display image description"),
                        description=_(u"Tick to let portlet gallery display description of the image."),
                        required=True,
                        default=True
                        )
    
    desc_font_size = schema.TextLine(title=_(u"Description font size"),
                        description=_(u"Font size of description"),
                        default=(u'7px'),
                        required=True
                        )

    desc_font_color = schema.TextLine(title=_(u"Description font color"),
                        description=_(u"Font color of description"),
                        default=(u'#CCCCCC'),
                        required=True
                        )
    
    desc_height = schema.TextLine(title=_(u"Description height"),
                        description=_(u"Height of description field under images."),
                        default=(u'15px'),
                        required=True
                        )

    count = schema.Int(title=_(u'Maximum number of pictures to display in gallery'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)
    
    shuffle = schema.Bool(title=_(u"Shuffle"),
                        description=_(u"Check to shuffle images."),
                        default=True,
                        required=False
                        )
    
    image_types = schema.Tuple(title=_(u"Image Types"),
                         description=_(u"Image types to be included into search"),
                         default=('Image', ),
                         required=False,
                         value_type=schema.Choice(
                             vocabulary="plone.app.vocabularies.PortalTypes")
                         )


    state = schema.Tuple(title=_(u"Workflow state"),
                         description=_(u"Items in which workflow state to show. Leave blank to not include this criterium."),
                         default=( ),
                         required=False,
                         value_type=schema.Choice(
                             vocabulary="plone.app.vocabularies.WorkflowStates")
                         )
                         
    paths = schema.Text(title=_(u"Paths"),
                         description=_(u"List of paths to be included in searching images (it will include all sub-folders). The path is relative to the Zope root, so if your Plone side id is Plone and you would like include all folders under it, you should enter /Plone"),
                         default=(u'/'),
                         required=True,
                        )
                     
                         
                         
    div_id = schema.TextLine(title=_(u"ID"),
                        description=_(u"Unique identifier for the gallery."),
                        default=(u'slideshow'+str(random.randrange(0, 10001))),
                        required=True
                        )
    image_size = schema.TextLine(title=_(u"Image size"),
                        description=_(u"Choose image resize function (e.g. large, preview, mini, thumb, title, icon, listing) or leave blank."),
                        default=u'thumb',
                        required=False
                        )
                        
    anim_interval = schema.Int(title=_(u'Animation Interval.'),
                       description=_(u'Time interval between slides change (in ms).'),
                       required=True,
                       default=5000)

    anim_steps = schema.Int(title=_(u'Animation duration.'),
                       description=_(u'Duration of fade in/out animation (in ms).'),
                       required=True,
                       default=500)

    jquery_symbol = schema.TextLine(title=_(u"JQuery symbol"),
                        description=_(u"JQuery introduce $ symbol, which in some versions of Plone is replaced by jq to avoid name-conflict. However in some versions it may still be $ or some of products you have installed might also changed it to $ or any different name."),
                        default=u'jq',
                        required=True)

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IGalleryPortlet)
    
    def __init__(self, name=u'', width=0, height=128, omit_border=False,display_desc=True,desc_font_size=u'7px',desc_font_color=u'#CCCCCC',desc_height=u'15px', count=5,shuffle=True, image_types=('Image',), state=( ), paths=(u'/',),div_id=(u'slideshow'+str(random.randrange(0, 10001))),image_size=u'thumb', anim_interval=5000, anim_steps=500, jquery_symbol=u'jq'):
        self.name = name
        self.width =width
        self.height = height
        self.omit_border=omit_border
        self.display_desc=display_desc
        self.desc_font_size=desc_font_size
        self.desc_font_color=desc_font_color
        self.desc_height=desc_height
        self.count = count
        self.shuffle = shuffle
        self.image_types = image_types
        self.state = state
        self.paths=paths
        self.div_id = div_id
        self.image_size = image_size
        self.anim_interval =anim_interval
        self.anim_steps = anim_steps
        self.jquery_symbol = jquery_symbol
        

    @property
    def title(self):
        return _(u"Gallery Portlet")


class Renderer(base.Renderer):
    
    _template =  ViewPageTemplateFile('galleryportlet.pt')
    imageFirstId = 0
    
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.navigation_root_url = portal_state.navigation_root_url()
        self.portal = portal_state.portal()
        self.navigation_root_path = portal_state.navigation_root_path()

    
    #@ram.cache(render_cachekey)
    #def render(self):
    #    return xhtml_compress(self._template())
    
    render = _template
        
    @property
    def available(self):
        return len(self._data())
        
    def resize_function(self):
        if self.data.image_size:
            return '/image_'+self.data.image_size
        else:
            return ''
        
    def images(self):
        return self._data()
        
    def title(self):
        return self.data.name
        
    def width(self):
        return self.data.width
        
    def height(self):
        return self.data.height
        
    def gallery_css(self):
        if self.width() > 0:
            widthTag = "width: %dpx  !important;" % self.width()
        else:
            widthTag = ''
        id = self.data.div_id 
        images = self.images()
        if len(images) > 0:
            if self.data.shuffle:
                self.imageFirstId = random.randrange(0, (len(images)-1))
            firstImgTag = "background-image:url('%s');" % (images[self.imageFirstId].getURL()+self.resize_function())
        else:
            firstImgTag = ''
        return ("""
<style type="text/css">
#slideshow {
   %s
   background-repeat: no-repeat;
   background-attachment: related;
   background-position: center center;
   %s
   height:%spx;
}
#slideshow-desc {
   font-size: %s;
   color: %s;
   text-align:center;
   height:%s;
}
</style> """ % (firstImgTag, widthTag, self.height(), self.data.desc_font_size, self.data.desc_font_color,self.data.desc_height)).replace('slideshow', id)

    def div_id(self):
        return self.data.div_id

    def gallery_js(self):
        id = self.data.div_id
        images = self.images()
        if len(images) > 0:
            imagesList = 'var images'+id+' = ['
            imagesDescList = 'var imagesDesc'+id+' = ['
            for img in images:
                imagesList = imagesList + "'"+img.getURL() + self.resize_function() +"', "
                imagesDescList = imagesDescList + "'"+_decode(_encode(img.Description)).replace("'","\\'").replace("\n","<br/>").replace("\r","")+"', "
            imagesList = imagesList + ']'
            imagesDescList = imagesDescList + ']'
            firstImgDesc = _decode(_encode(images[self.imageFirstId].Description)).replace("'","\\'").replace("\n","<br/>").replace("\r","")
        else:
            imagesList = '[]'
            imagesDescList = '[]'
            firstImgDesc = '&nbsp;'
        jsInitCounter = "var galleryCounter = %d;\n" % (self.imageFirstId)
       	if self.data.shuffle:
       	    jsChooseNext = """
       	    	galleryCounterOld = galleryCounter;
       	    	while(galleryCounterOld == galleryCounter){
     	    		galleryCounter = Math.floor(Math.random() * images.length );
       	    	}
     	    """
       	else:
       	    jsChooseNext = """
     	    	galleryCounter++;
  				galleryCounter %= images.length;
     	    """

        return ("""
<script type="text/javascript">
%s;
%s;
""" % (imagesList, imagesDescList)) + (""" 
%s

function slideSwitch() {
    var $slideshow = $('#slideshow');
    var $slideshow_desc = $('#slideshow-desc');

    %s
    
    $slideshow.animate({opacity : 0.0}, %d, function() {
    	$slideshow_desc.html('&nbsp;');
        $slideshow.css('background-image' , 'url('+images[galleryCounter]+')');
          $slideshow.animate({opacity : 1.0}, %d);
          $slideshow_desc.html('&nbsp;'+descs[galleryCounter]);
        });
}

$('#slideshow-desc').html('&nbsp;'+'%s');
setInterval( "slideSwitch()", %d );
</script> """ % (jsInitCounter,jsChooseNext,self.data.anim_steps, self.data.anim_steps,firstImgDesc, self.data.anim_interval)).replace('$', self.data.jquery_symbol).replace('slideshow', id).replace('slideSwitch', id).replace('galleryCounter', 'counter'+id).replace('images', 'images'+id).replace('descs', 'imagesDesc'+id)
        
#    @memoize
    def _data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        limit = self.data.count
        state = self.data.state
        query= {'portal_type':self.data.image_types,} 
        if len(state)>0:
            query['review_state'] = state
        query['path']=self.data.paths.split("\n")
        query['sort_on'] = 'Date'
        query['sort_order'] = 'reverse'
        if limit:
            result = catalog(query)[:limit]
        else:
            result = catalog(query)
        return result


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IGalleryPortlet)
    
    label = _(u"Add Gallery Portlet")
    description = _(u"This portlet presents dynamic gallery based on query.")

    def create(self, data):
        return Assignment(
                name=data.get('name',u''),
                width=data.get('width',0),
                height=data.get('height',128),
                omit_border=data.get('omit_border', False),
                display_desc=data.get('display_desc', True),
                desc_font_size=data.get('desc_font_size', u'7px'),
                desc_font_color=data.get('desc_font_color', u'#CCCCCC'),
                desc_height=data.get('desc_height', u'15px'),
                count=data.get('count', 5),
                shuffle=data.get('shuffle', True), 
                image_types=data.get('image_types', ('Image',)),
                state=data.get('state', ()),
                paths=data.get('paths', u'/'),
                div_id=u'slideshow'+str(random.randrange(0, 10001)),
                image_size=data.get('image_size', u'thumb'),
                anim_interval=data.get('anim_interval', 5000),
                anim_steps=data.get('anim_steps', 500),
                jquery_symbol=data.get('jquery_symbol', u'jq'))

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IGalleryPortlet)
    
    label = _(u"Edit Gallery Portlet")
    description = _(u"This portlet presents dynamic gallery.")
