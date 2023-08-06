
import re
import logging

from five import grok
from zope.schema import getFieldsInOrder

from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.libtransforms.utils import MissingBinary
from Products import ARFilePreview

from plone.dexterity.utils import iterSchemata
from plone.rfc822.interfaces import IPrimaryField

from collective.filepreviewbehavior import interfaces

LOG = logging.getLogger('collective.filepreviewbehavior')

class ToPreviewableObject( ARFilePreview.adapters.ToPreviewableObject,
                           grok.Adapter ):
    grok.implements( ARFilePreview.interfaces.IPreviewable )
    grok.context( interfaces.IPreviewable )


    class _replacer(object):
        
        def __init__( self, sublist, instance ):
            self.sublist = sublist
            self.instance = instance
        
        def __call__( self, match ):
            prefix = match.group( 1 )
            inside = match.group( 2 )
            postfix = match.group( 3 )
            # patch inside
            if inside.startswith( './' ):
                # some .swt are converted with this prefix
                inside = inside[2:]
            if inside in self.sublist:
                # convert elems that are known images 
                inside = '%s/@@preview_provider?image=%s' % (
                        self.instance.getId(),
                        inside
                )
            result = '<img%s src="%s"%s>' % ( prefix, inside, postfix )
            return result


    def getPrimaryField( self ):
        for schema in iterSchemata( self.context ):
            for name, field in getFieldsInOrder( schema ):
                if IPrimaryField.providedBy( field ):
                    return field
        return None


    def getPreview( self, mimetype='text/html' ):
        data = self.annotations[self.key]['html']
        if mimetype != 'text/html' and data:
            transforms = getToolByName( self.context, 'portal_transforms' )
            primary = self.getPreview()
            filename = primary.get( self.context ).filename + '.html'
            return str( transforms.convertTo( mimetype, data.encode('utf8'),
                                              mimetype = 'text/html',
                                              filename = filename )
                      ).decode('utf8')
        return data

    
    def buildAndStorePreview(self):
        self.clearSubObjects()
        transforms = getToolByName(self.context, 'portal_transforms')
        # -- get the primary field the dexterity way
        file = self.getPrimaryField().get( self.context )
        data = None
        if file:
            try:
                data = transforms.convertTo('text/html', file.data, filename=file.filename)
            except MissingBinary, e:
                LOG.error(str(e))
        # --
        
        if data is None:
            self.setPreview(u"")
            return
        
        #get the html code
        html_converted = data.getData()
        #update internal links
        #remove bad character '\xef\x81\xac' from HTMLPreview
        html_converted = re.sub('\xef\x81\xac', "", html_converted)
        # patch image sources since html base is that of our parent
        subobjs = data.getSubObjects()
        if len(subobjs)>0:
            for id, data in subobjs.items():
                self.setSubObject(id, data)
            html_converted = self._re_imgsrc.sub(self._replacer(subobjs.keys(), self.context), html_converted)
        #store the html in the HTMLPreview field for preview
        self.setPreview(html_converted.decode('utf-8', "replace"))
        self.context.reindexObject()



