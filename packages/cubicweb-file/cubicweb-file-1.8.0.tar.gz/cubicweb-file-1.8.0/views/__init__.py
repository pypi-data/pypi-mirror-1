from cubicweb.view import EntityView
from cubicweb.selectors import implements
from cubicweb.web import uicfg
from cubicweb.web.views import baseviews

_pvs = uicfg.primaryview_section
_pvs.tag_attribute(('File', 'title'), 'hidden')
_pvs.tag_attribute(('Image', 'title'), 'hidden')
_pvs.tag_attribute(('File', 'data_name'), 'hidden')
_pvs.tag_attribute(('Image', 'data_name'), 'hidden')

_pvdc = uicfg.primaryview_display_ctrl
_pvdc.tag_attribute(('File', 'description'), {'showlabel': False})
_pvdc.tag_attribute(('Image', 'description'), {'showlabel': False})


class FileOneLine(baseviews.OneLineView):
    __select__ = implements('File')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<img src="%s" alt="%s"/>' % (
            entity.icon_url(), self._cw._('icon for %s') % entity.data_format))
        super(FileOneLine, self).cell_call(row, col)


class FileInContext(baseviews.InContextView):
    __select__ = implements('File')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<img src="%s" alt="%s"/>' % (
            entity.icon_url(), self._cw._('icon for %s') % entity.data_format))
        super(FileInContext, self).cell_call(row, col)


class FileOutOfContext(baseviews.OutOfContextView):
    __select__ = implements('File')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<img src="%s" alt="%s"/>' % (
            entity.icon_url(), self._cw._('icon for %s') % entity.data_format))
        super(FileOutOfContext, self).cell_call(row, col)



class FileIcon(EntityView):
    __select__ = implements('File')
    __regid__ = 'icon'
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w('<a href="%s"><img src="%s" alt="%s"/></a>' % (
            entity.absolute_url(), entity.icon_url(),
            self._cw._('file type icon')))
