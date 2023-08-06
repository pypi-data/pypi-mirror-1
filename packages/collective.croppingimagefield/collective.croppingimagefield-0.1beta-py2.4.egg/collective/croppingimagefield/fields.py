from cStringIO import StringIO

from Products.Archetypes.Field import ImageField, HAS_PIL
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from ZODB.POSException import ConflictError

if HAS_PIL:
    import PIL

_marker = []

RESIZE_SCALE = 0
RESIZE_ZOOM = 1
RESIZE_CROP = 2

class CroppingImageField(ImageField):
    """
    See README.txt for documentation and example
    """

    _properties = ImageField._properties.copy()
    _properties.update({
        'original_crop' : False,
        })

    __implements__ = ImageField.__implements__

    security = ClassSecurityInfo()

    security.declareProtected(permissions.ModifyPortalContent, 'rescaleOriginal')
    def rescaleOriginal(self, value, **kwargs):
        """rescales the original image and sets the data

        for self.original_size or self.max_size
        
        value must be an OFS.Image.Image instance
        """
        data = str(value.data)
        if not HAS_PIL:
            return data
        
        mimetype = kwargs.get('mimetype', self.default_content_type)
        
        if self.original_size or self.max_size:
            if not value:
                return self.default
            # ================= Begin mod ====================
            w=h=s=r=0
            # ================= End mod ====================
            if self.max_size:
                if value.width > self.max_size[0] or \
                       value.height > self.max_size[1]:
                    factor = min(float(self.max_size[0])/float(value.width),
                                 float(self.max_size[1])/float(value.height))
                    w = int(factor*value.width)
                    h = int(factor*value.height)
            elif self.original_size:
                # ================= Begin mod ====================
                w = self.original_size[0]
                h = self.original_size[1]
                if len(self.original_size) > 2:
                    r = self.original_size[2]
            if w and h:
                __traceback_info__ = (self, value, w, h, r)
                fvalue, format = self.resize(data, w, h, r)
                # ================= End mod ====================
                data = fvalue.read()
        else:
            data = str(value.data)
            
        return data

    security.declareProtected(permissions.ModifyPortalContent, 'createScales')
    def createScales(self, instance, value=_marker):
        """creates the scales and save them
        """
        sizes = self.getAvailableSizes(instance)
        if not HAS_PIL or not sizes:
            return
        # get data from the original size if value is None
        if value is _marker:
            img = self.getRaw(instance)
            if not img:
                return
            data = str(img.data)
        else:
            data = value

        # empty string - stop rescaling because PIL fails on an empty string
        if not data:
            return

        filename = self.getFilename(instance)

        for n, size in sizes.items():
            # ================= Begin mod ====================
            if size[:2] == (0,0):
                continue
            w = size[0]
            h = size[1]
            if len(size) > 2:
                r = size[2]
            else:
                r = 0
            id = self.getName() + "_" + n
            __traceback_info__ = (self, instance, id, w, h, r)
            try:
                imgdata, format = self.resize(data, w, h, r)
                # ================= End mod ====================
            except (ConflictError, KeyboardInterrupt):
                raise
            except:
                if not self.swallowResizeExceptions:
                    raise
                else:
                    log_exc()
                    # scaling failed, don't create a scaled version
                    continue

            mimetype = 'image/%s' % format.lower()
            image = self._make_image(id, title=self.getName(), file=imgdata,
                                     content_type=mimetype, instance=instance)
            # nice filename: filename_sizename.ext
            #fname = "%s_%s%s" % (filename, n, ext)
            #image.filename = fname
            image.filename = filename
            try:
                delattr(image, 'title')
            except (KeyError, AttributeError):
                pass
            # manually use storage
            self.getStorage(instance).set(id, instance, image,
                                          mimetype=mimetype, filename=filename)

    security.declarePrivate('resize')
    def resize(self, data, w, h, r, default_format = 'PNG'):
        """ resize image (with material from ImageTag_Hotfix)"""
        #make sure we have valid int's
        size = int(w), int(h)

        original_file=StringIO(data)
        image = PIL.Image.open(original_file)
        # consider image mode when scaling
        # source images can be mode '1','L,','P','RGB(A)'
        # convert to greyscale or RGBA before scaling
        # preserve palletted mode (but not pallette)
        # for palletted-only image formats, e.g. GIF
        # PNG compression is OK for RGBA thumbnails
        original_mode = image.mode
        if original_mode == '1':
            image = image.convert('L')
        elif original_mode == 'P':
            image = image.convert('RGBA')
        # ================= Begin mod ====================
        resize = int(r)
        iw, ih = image.size
        dw, dh = size
        ir = float(iw) / float(ih)
        dr = float(dw) / float(dh)
        wr = float(dw) / float(iw)
        hr = float(dh) / float(ih)
        if resize == RESIZE_ZOOM:
            if ir > dr: # image larger than the desired size                
                size = (int(iw*hr), dh)
            else:
                size = (dw, int(ih*wr))
            image=image.resize(size, self.pil_resize_algo)
        elif resize == RESIZE_CROP:
            l = t = 0
            if ir > dr: # image larger than the desired size                
                osize = (int(iw*hr), dh)
                l = int((iw*hr - dw) / 2)
            else:
                osize = (dw, int(ih*wr))
                t = int((ih*wr - dh) / 2)
            image=image.resize(osize, self.pil_resize_algo)
            image=image.crop((l, t, l+dw, t+dh))
        else: # if resize == RESIZE_SCALE
            if ir > dr: # image larger than the desired size                
                size = (dw, int(ih*wr))
            else:
                size = (int(iw*hr), dh)
            image=image.resize(size, self.pil_resize_algo)
            # ================= End mod ====================
        format = image.format and image.format or default_format
        # decided to only preserve palletted mode
        # for GIF, could also use image.format in ('GIF','PNG')
        if original_mode == 'P' and format == 'GIF':
            image = image.convert('P')
        thumbnail_file = StringIO()
        # quality parameter doesn't affect lossless formats
        image.save(thumbnail_file, format, quality=self.pil_quality)
        thumbnail_file.seek(0)
        return thumbnail_file, format.lower()

    security.declarePrivate('scale')
    scale = resize


