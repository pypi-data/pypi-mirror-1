from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from sgmllib import SGMLParser
from urlparse import urlsplit, urlunsplit, urljoin

singleton_tags = ["img", "br", "hr", "input", "meta", "param", "col"]

class TinyMCEOutput(SGMLParser):
    """ Parser to convert UUID links and captioned images """
    from htmlentitydefs import entitydefs

    def __init__(self, context=None, captioned_images=0):
        SGMLParser.__init__(self)
        self.current_status = None
        self.context = context
        self.captioned_images = captioned_images
        self.pieces = []

    def _makeUrlRelative(self, url, base):
        """Make a link relative to base. This method assumes we have already checked that url and base have a common prefix. This is taken from Kupu"""
        scheme, netloc, path, query, fragment = urlsplit(url)
        _, _, basepath, _, _ = urlsplit(base)
    
        baseparts = basepath.split('/')
        pathparts = path.split('/')
    
        basetail = baseparts.pop(-1)
    
        # Remove common elements
        while pathparts and baseparts and baseparts[0]==pathparts[0]:
            baseparts.pop(0)
            pathparts.pop(0)
    
        for i in range(len(baseparts)):
            pathparts.insert(0, '..')
    
        if not pathparts:
            pathparts.insert(0, '.')
        elif pathparts==[basetail]:
            pathparts.pop(0)
        return '/'.join(pathparts)
        
    def append_data(self, data, add_eol=0):
        """Append data to self.datas, add_eol won't remove the newline characters""" 
        if not add_eol:
            data = data.replace("\n", "") 
            data = data.replace("\r", "")
        else:
            data += '\n'    
        self.pieces.append(data)

    def handle_charref(self, ref):
        """ Handle characters, just add them again """
        self.append_data("&#%(ref)s;" % locals())

    def handle_entityref(self, ref):
        """ Handle html entities, put them back as we get them """
        self.append_data("&%(ref)s;" % locals())

    def handle_data(self, text):
        """ Add data unmodified """
        self.append_data(text);

    def handle_comment(self, text):
        """ Handle comments unmodified """
        self.append_data("<!--%(text)s-->" % locals())

    def handle_pi(self, text):
        """ Handle processing instructions unmodified""" 
        self.append_data("<?%(text)s>" % locals())

    def handle_decl(self, text):
        """Handle declarations unmodified """
        self.append_data("<!%(text)s>" % locals())
        
    def unknown_starttag(self, tag, attrs):
        """Here we've got the actual conversion of links and images. Convert UUID's to relative paths, and process captioned images to HTML"""
        if tag in ['a', 'img']:
            # Only do something if tag is a link or images
            attributes = {}
            for (key, value) in attrs:
                attributes[key] = value
            
            if tag == 'a':
                if attributes.has_key('href'):
                    href = attributes['href']
                    if href.find('resolveuid') == 0:
                        # We should check if "Link using UIDs" is enabled in the TinyMCE tool, but then the kupu resolveuid is used, so let's always transform here
                        parts = href.split("/")
                        # Get the actual UUID
                        uid = parts[1]
                        appendix = ""
                        if len(parts) > 2:
                            # There is more than just the UUID, save it in appendix
                            appendix = "/".join(parts[2:])
                        reference_tool = getToolByName(self.context, 'reference_catalog')
                        ref_obj = reference_tool.lookupObject(uid)
                        if ref_obj:
                            href = self._makeUrlRelative(ref_obj.absolute_url(), self.context.absolute_url()) + appendix
                            attributes['href'] = href
                            attrs = attributes.iteritems()
            elif tag == 'img':
                # First collect some attributes
                src = ""
                description = ""
                if attributes.has_key("src"):
                    src = attributes["src"]
                if src.find('resolveuid') == 0:
                    # We need to convert the UUID to a relative path here
                    parts = src.split("/")
                    uid = parts[1]
                    appendix = ""
                    if len(parts) > 2:
                        # There is more than just the UUID, save it in appendix (query parameters for example)
                        appendix = "/" + "/".join(parts[2:])
                    reference_tool = getToolByName(self.context, 'reference_catalog')
                    image_obj = reference_tool.lookupObject(uid)
                    if image_obj:
                        # Only do something when the image is actually found in the reference_catalog
                        src = self._makeUrlRelative(image_obj.absolute_url(), self.context.absolute_url()) + appendix
                        if hasattr(image_obj, "Description"):
                            description = image_obj.Description()                    
                else:
                    # It's a relative path, let's see if we can get the description from the portal catalog
                    full_path = urljoin(self.context.absolute_url(), src)
                    scheme, netloc, path, query, fragment = urlsplit(full_path)
                    portal_catalog = getToolByName(self.context, "portal_catalog")
                    # Check if we can find this in the portal catalog
                    brains = portal_catalog({'path' : {'query':path}, 'type' : 'Image'})
                    if len(brains) == 0:
                        # Maybe omething like 'image_preview' is in the path, let's chop it
                        query= {'path' : {'query' : "/".join(path.split('/')[:-1])}, 'type' : 'Image'}
                        brains = portal_catalog(query)
                    if len(brains) > 0:
                        description = brains[0].Description
                # Check if the image is a captioned image
                classes = ""                       
                if attributes.has_key("class"):
                    classes = attributes["class"]
                if self.captioned_images and classes.find('captioned') != -1:
                    # We have captioned images, and we need to convert them, so let's do so
                    width_style = ""    
                    if attributes.has_key("width"):
                        width_style="style=\"width:%spx;\" " % attributes["width"]
                    image_attributes = ""
                    image_attributes = image_attributes.join(["%s %s=\"%s\"" % (image_attributes, key, value) for (key, value) in attributes.items() if not key in ["class", "src"]])
                    captioned_html = """<dl %sclass="%s"> 
                                        <dt %s>
                                            <img %s src="%s"/>
                                        </dt>
                                        <dd class="image-caption">%s</dd>
                                        </dl>""" % (width_style, classes, width_style, image_attributes, src ,description)
                    self.append_data(captioned_html)
                    return True
                else:
                    # Nothing happens with the image, so add it normally
                    attrs = attributes.iteritems()
                    
        # Add the tag to the result
        strattrs = "".join([' %s="%s"' % (key, value) for key, value in attrs])
        if tag in singleton_tags:
            self.append_data("<%(tag)s%(strattrs)s />" % locals(), add_eol=1)
        else:
            self.append_data("<%(tag)s%(strattrs)s>" % locals(), add_eol=1)
        
    def unknown_endtag(self, tag):
        """Add the endtag unmodified"""
        self.append_data("</%(tag)s>" % locals(), add_eol=1) 

    def getResult(self):
        """Return the parsed result and flush it"""
        result = "".join(self.pieces)
        self.pieces = None
        return result
