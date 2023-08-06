"""cubicweb-ctl plugin providing the fsimport command

:organization: Logilab
:copyright: 2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.clcommands import register_commands, pop_arg

from cubicweb.toolsutils import Command


class FSImportCommand(Command):
    """Import content of a directory on the file system as File/Image entities.
    The instance must use the `file` cube.

    <instance id>
      identifier of the instance where directory's content has to be imported.

    <fs directory>
      directory to import (recursivly)
    """
    name = 'fsimport'
    arguments = '<instance id> <fs directory>'
    options = (
        ("map-folders",
         {'short': 'F', 'action' : 'store_true',
          'default': False,
          'help': 'map file-system directories as Folder entities (requires the `folder` cube).',
          }),
        )

    def run(self, args):
        """run the command with its specific arguments"""
        from cubicweb.server.serverconfig import ServerConfiguration
        from cubicweb.server.serverctl import repo_cnx
        from cubicweb.server.sources.storages import ETYPE_ATTR_STORAGE
        from cubes.file.fsimport import import_directory
        appid = pop_arg(args, expected_size_after=1)
        directory = pop_arg(args)
        config = ServerConfiguration.config_for(appid)
        repo, cnx = repo_cnx(config)
        session = repo._get_session(cnx.sessionid, setpool=True)
        import_directory(session, directory,
                         mapfolders=self.config.map_folders,
                         bfss='data' in ETYPE_ATTR_STORAGE.get('File', ()),
                         )
        session.commit()

register_commands((FSImportCommand,))
