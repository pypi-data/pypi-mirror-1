from zope.interface import implements
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.instance import memoize
from datetime import datetime,timedelta
import time

fmt = '%Y/%m/%d %H:%M:%S'
try:
    import deliciousapi
    dapi = deliciousapi.DeliciousAPI()
    val =True
except:
    val =False
                    
        

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from Products.ATContentTypes.interface import IATFolder


from my315ok.portlet.bookmark import BookmarkPortletMessageFactory as _
from plone.portlet.collection import PloneMessageFactory as _a





class IBookmarkPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    header = schema.TextLine(title=_a(u"Portlet header"),
                             description=_a(u"Title of the rendered portlet"),
                             required=True)

    limit = schema.Int(title=_a(u"Limit"),
                       description=_a(u"Specify the maximum number of items to show in the portlet."
                                       "Leave this blank to show all items."),
                       required=False)
    isprivate = schema.Bool(title=_a(u"display private bookmark"),
                         description=_a(u"If enabled, items will be selected  from a private bookmark ,"
                                         "this need provide username and passwd,else items be selected "
                                         "from a public bookmark,this need provide a tag."),
                         required=True,
                         default=True)
    interval = schema.Int(title=_(u"interval"),
                       description=_(u"Specify the duration for using fresh page,in hours."),
                       required=True) 
    tag = schema.TextLine(title=_(u"your tag"),
                       description=_(u"Specify you  focusing tag ."),                                      
                       required=True)
    innerid = schema.TextLine(title=_(u"inner css id"),
                       description=_(u"the css id that you need load html to here."),
                        required=False
                      )
    tmpdocid = schema.TextLine(title=_(u"doc id"),
                       description=_(u"the generated doc id that using for cache out html source."),
                        required=False
                      )
  
    target_folder = schema.Choice(title=_a(u"Target folder"),
                                  description=_a(u"Find the folder which provides the items to list"),
                                  required=True,
                                  source=SearchableTextSourceBinder({'object_provides' : IATFolder.__identifier__},
                                                                    default_query='path:'))
    username = schema.TextLine(title=_(u"Delicious username"),
                       description=_(u"Specify your username  in Delicious bookmark site."),
                       required=True)
    passwd = schema.TextLine(title=_(u"passwd"),
                       description=_(u"Specify your password in Delicious bookmark site."),
                       required=True)    


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IBookmarkPortlet)

    # TODO: Set default values for the configurable parameters here

    header = u""
    limit = 5
    isprivate = True
    tag = u""
    interval = 5
    innerid = u""
    tmpdocid = u""
    target_folder = None
    username = u""
    passwd = u""
       

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u""):
    #    self.some_field = some_field

    def __init__(self,header=u"",limit=None,isprivate=True,tag=None,interval=5,innerid=None,tmpdocid=u"",target_folder=None,username=None,passwd=None):
        self.header = header
        self.limit = limit
        self.isprivate = isprivate
        self.interval = interval
        self.innerid = innerid
        self.target_folder = target_folder
        self.tag = tag
        self.username = username
        self.passwd = passwd
        

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """                   
        return _(u"Bookmark portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('bookmarkportlet.pt')
    def available(self):
        return val and len(self.result())
    
    def portlet_header(self):
        head = self.data.header        
        return head
    
    @memoize
    def result(self):
#        import pdb
#        pdb.set_trace()
        try:
            return self.outer(self.data.tmpdocid)
        except:
            return u''
        
    def isfetch(self,id):
#        import pdb
#        pdb.set_trace()
        from time import mktime
        container = self.target_folder()
        if id == None:
            return 1
        obj = getattr(container,id,None)
        if obj == None: 
            return 1       
        #imevalue = self.folder.doc.modified()
        timevalue = obj.modified()        
        
        di = time.strptime(timevalue.strftime(fmt),fmt)
        dt = datetime.fromtimestamp(mktime(di))

        now =   datetime.now()
        if (now - dt) > timedelta(hours = self.data.interval):
            return 1        
        return 0         
   
        
    def outer(self,id):
#        import pdb
#        pdb.set_trace()
        if self.isfetch(id):
            try:
                content = self.get_htmlsrc()                          
                length = len(content['title'])
                outs =""
                if length == 0:
                    return outs                
                for i in range(length):                    
                    outs = outs + """<dd class="portletItem">
                    <a href="%s" class="tile" title="%s">            
                    <span>%s</span>
                    <span class="portletItemDetails">%s</span>
        </a></dd>""" % (content["url"][i],content["title"][i],content["title"][i],content["time"][i])                                                  

                self.store_tmp_content(id, outs)
                return outs                
            except:
                return self.fetch_tmp_content(id)
        else:
                
            return self.fetch_tmp_content(id)
            
    
    def fetch_tmp_content(self,id):
#        import pdb
#        pdb.set_trace()
        container = self.target_folder()
        try:
            obj = container[id]
        except:
            return u""
        cached = obj.getText()
        return cached       
            
    @memoize   
    def store_tmp_content(self,id,content):
#        import pdb
#        pdb.set_trace()
        container = self.target_folder()
        if id == None:
            return
        obj = getattr(container,id,None)
        if obj == None:           
            container.invokeFactory(type_name="Document", id=id)
            obj = container[id]
      
        obj.setText(content)
        obj.setModificationDate(datetime.now().strftime(fmt))
        
    def target_folder(self):
        path = self.data.target_folder
        if not path:
            return None
        if path.startswith('/'):
            path = path[1:]        
        if not path:
            return None
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(path, default=None)
    
    @memoize
    def get_htmlsrc(self):
#        import pdb
#        pdb.set_trace()
        data = self.data
        if data.isprivate:
            content = self._standard_results()            
        else:
            content = self._standard_resultspub()
        return content                   

    @memoize
    def _standard_results(self):
#        import pdb
#        pdb.set_trace()    
        data = self.data
        results = {}       
        dbookmark = dapi.get_user(username=data.username, max_bookmarks=data.limit, sleep_seconds=1)
        results["title"] = []
        results["url"] = []
        results["time"] = [] 
        for bookmark in dbookmark.bookmarks:
            title = bookmark[2]
            url = bookmark[0]
            tm = bookmark[-1]
            ts = time.strftime('%Y-%m-%d',tm)
            results["title"].append(title)
            results["url"].append(url)
            results["time"].append(ts)                                     
        return results   


    @memoize
    def _standard_resultspub(self):    
##        import pdb
##        pdb.set_trace()
        data = self.data
        results = {}                                  
        urls = dapi.get_urls(tag=data.tag, popular=False, max_urls=data.limit)
#        from BeautifulSoup import BeautifulSoup 
        results["title"] = []
        results["url"] = []
        results["time"] = []              
        for u in urls:
            meta = dapi.get_url(u)            
            title = meta.title
            url = meta.url
            tm = meta.bookmarks[0][-1]
            ts = time.strftime('%Y-%m-%d',tm)
            results["title"].append(title)
            results["url"].append(url)
            results["time"].append(ts)
                                                                                       
        return results 

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IBookmarkPortlet)
    form_fields['target_folder'].custom_widget = UberSelectionWidget
    
    label = _a(u"Add Collection Portlet")
    description = _a(u"This portlet display a listing of items from a Collection.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IBookmarkPortlet)
    form_fields['target_folder'].custom_widget = UberSelectionWidget
    
    label = _a(u"Add Collection Portlet")
    description = _a(u"This portlet display a listing of items from a Collection.")
