"""entity classes for File entities

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from os.path import join

from logilab.mtconverter import guess_mimetype_and_encoding
from logilab.common.deprecation import deprecated

from cubicweb import Binary
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.interfaces import IDownloadable

class File(AnyEntity):
    """customized class for File entities"""
    __regid__ = 'File'
    fetch_attrs, fetch_order = fetch_config(['data_name', 'title'])
    __implements__ = AnyEntity.__implements__ + (IDownloadable,)

    def set_format_and_encoding(self):
        """try to set format and encoding according to known values (filename,
        file content, format, encoding).

        This method must be called in a before_[add|update]_entity hook else it
        won't have any effect.
        """
        assert 'data' in self, "missing mandatory attribute data"
        if self.get('data'):
            if hasattr(self.data, 'filename'):
                self['data_name'] = self.data.filename
        else:
            self['data_format'] = None
            self['data_encoding'] = None
            self['data_name'] = None
            return
        if 'data_format' in self.edited_attributes:
            format = self.get('data_format')
        else:
            format = None
        if 'data_encoding' in self.edited_attributes:
            encoding = self.get('data_encoding')
        else:
            encoding = None
        if not (format and encoding):
            format, encoding = guess_mimetype_and_encoding(
                data=self.get('data'),
                # use get and not get_value since data has changed, we only want
                # to consider explicitly specified values, not old ones
                filename=self.get('data_name'),
                format=format, encoding=encoding,
                fallbackencoding=self._cw.encoding)
            if format:
                self['data_format'] = unicode(format)
            if encoding:
                self['data_encoding'] = unicode(encoding)

    def pre_add_hook(self):
        """hook called by the repository before doing anything to add the entity
        (before_add entity hooks have not been called yet). Autocast File to
        Image if data_format is an image mime type.
        """
        self.set_format_and_encoding()
        if self.get('data_format') and self['data_format'].startswith('image/'):
            imagecls = self._cw.vreg['etypes'].etype_class('Image')
            image = imagecls(self._cw, None)
            image.update(self)
            image._is_saved = False
            image.edited_attributes = self.edited_attributes
            max_size = self._cw.vreg.config['image-max-size']
            if max_size:
                image['data'] = image._thumbnail(max_size)
            return image
        return self

    def dc_title(self):
        if self.title:
            return '%s (%s)' % (self.title, self.data_name)
        return self.data_name

    # IDownloadable
    def download_url(self):
        return self.absolute_url(vid='download')
    def download_content_type(self):
        return self.data_format
    def download_encoding(self):
        return self.data_encoding
    def download_file_name(self):
        return self.data_name
    def download_data(self):
        return self.data.getvalue()

    def size(self):
        rql = "Any LENGTH(D) WHERE X eid %(eid)s, X data D"
        return self.cursor.execute(rql, {'eid': self.eid})[0][0]

    @property
    @deprecated('use data_name instead')
    def name(self):
        return self.data_name

    def icon_url(self):
        config = self._cw.vreg.config
        for rid in (self.data_format.replace('/', '_', 1),
                    self.data_format.split('/', 1)[0],
                    'default'):
            iconfile = rid + '.ico'
            rpath = config.locate_resource(join('icons', iconfile))
            if rpath is not None:
                return self._cw.build_url('data/icons/' + iconfile)


from PIL.Image import open as pilopen
from PIL.Image import ANTIALIAS
from StringIO import StringIO

from uilib import dropShadow


class Image(File):
    __regid__ = 'Image'

    def pre_add_hook(self):
        """hook called by the repository before doing anything to add the entity
        (before_add entity hooks have not been called yet). Autocast File to
        Image if data_format is an image mime type.
        """
        # XXX won't work when adding an image as file
        self.set_format_and_encoding()
        max_size = self._cw.vreg.config['image-max-size']
        if max_size:
            self['data'] = self._thumbnail(max_size)
        return self

    def download_data(self):
        if 'small' in self._cw.form:
            shadow = 'noshadow' not in self._cw.form
            return self.thumbnail(shadow)
        return self.data.getvalue()

    def _thumbnail(self, size, shadow=False):
        size = tuple(int(s) for s in size.split('x'))
        pilimg = pilopen(self.data)
        if shadow:
            pilimg.draft("RGB", pilimg.size)
            pilimg = pilimg.convert("RGB")
            pilimg.thumbnail(size, ANTIALIAS)
            pilimg = dropShadow(pilimg)
        else:
            pilimg.thumbnail(size, ANTIALIAS)
        stream = Binary()
        pilimg.save(stream, u'png')
        return stream

    def thumbnail(self, shadow=True):
        size = self._cw.vreg.config['image-thumb-size']
        return self._thumbnail(size, shadow).getvalue()
