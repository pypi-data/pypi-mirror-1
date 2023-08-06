"""File related hooks

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"


from cubicweb import ValidationError
from cubicweb.selectors import implements
from cubicweb.server import hook
from cubicweb.sobjects.notification import ContentAddedView
from cubicweb.selectors import implements


class UpdateFileHook(hook.Hook):
    """a file has been updated, check data_format/data_encoding consistency
    """
    __regid__ = 'updatefilehook'
    events = ('before_update_entity',)
    __select__ = hook.Hook.__select__ & implements('File')

    def __call__(self):
        if self.entity.get('data'):
            self.entity.set_format_and_encoding()


class AddUpdateImageHook(hook.Hook):
    """a file has been updated, check data_format/data_encoding consistency
    """
    __regid__ = 'addupdateimagehook'
    events = ('before_add_entity', 'before_update_entity',)
    __select__ = hook.Hook.__select__ & implements('Image')

    def __call__(self):
        format = self.entity.get('data_format')
        if not 'data_format' in self.entity.edited_attributes \
               and 'data' in self.entity.edited_attributes:
            self.entity.set_format_and_encoding()
            format = self.entity.get('data_format')
        else:
            format = self.entity.get('data_format')
        if format and not format.startswith('image/'):
            raise ValidationError(self.entity.eid,
                                  {'data': self._cw._('not an image file (%s)') % format})


class FileAddedView(ContentAddedView):
    """get notified from new files"""
    __regid__ = 'fileaddedview'
    __select__ = implements('File', 'Image')
    content_attr = 'description'
