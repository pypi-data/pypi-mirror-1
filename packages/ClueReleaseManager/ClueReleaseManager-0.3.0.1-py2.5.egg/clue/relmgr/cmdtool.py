import logging
import optparse
import sys

from clue.relmgr import utils
from clue.relmgr.pypi import PyPi


class InsecurePyPi(PyPi):

    def has_role(self, distro_id, *roles):
        return True

    def get_active_user(self):
        return 'admin'


class Runner(object):
    """Cmdtool runner.

      >>> runner = Runner()
      >>> class Mock(object):
      ...     def __init__(self, **kw):
      ...         self.__dict__.update(kw)
      >>> class MockSecurity(object):
      ...     def update_user(self, *args, **kwargs): pass
      ...     def update_roles(self, *args, **kwargs): pass
      >>> runner.pypi_factory = lambda x, y: Mock(security_manager=MockSecurity())

      >>> runner.main([], [])
      Usage: setup.py <cmd> [<arg1>, <arg2>...]
      <BLANKLINE>
          Where <cmd> can be:
              updateuser <username> <password> <email> [<role1> <role2> ...]
              updategroup <groupname> [<role1> <role2> ...]
              updateusersgroups <username> <group1> [<group2> ...]
              addfile <distro_id> <filename>
              addindexentry <distro_id> <indexname> <target_distro_id> <target_distro_version>
              delindexentry <distro_id> <indexname> <target_distro_id>
      <BLANKLINE>

      >>> runner.main(['updateuser', 'foo', 'bar', 'abc', 'role1'])
    """

    pypi_factory = staticmethod(InsecurePyPi)

    def split_roles(self, *args):
        roles = {}
        for arg in args:
            s = arg.split(':')
            distro_id = ''
            if len(s) == 2:
                distro_id = s[0]
                role = s[1]
            else:
                role = s[0]
            l = roles.get(distro_id, None)
            if l is None:
                l = set()
                roles[distro_id] = l
            l.add(role)
        return roles

    def main(self, args=None, extraargs=None):
        logging.basicConfig()

        usage = """%prog <cmd> [<arg1>, <arg2>...]

    Where <cmd> can be:
        updateuser <username> <password> <email> [<role1> <role2> ...]
        updategroup <groupname> [<role1> <role2> ...]
        updateusersgroups <username> <group1> [<group2> ...]
        addfile <distro_id> <filename>
        addindexentry <distro_id> <indexname> <target_distro_id> <target_distro_version>
        delindexentry <distro_id> <indexname> <target_distro_id>"""

        parser = optparse.OptionParser(usage=usage)

        if args is None:
            args = []
        if extraargs is None:
            extraargs = sys.argv[1:]
        options, args = parser.parse_args(args + extraargs)

        if len(args) < 1:
            parser.print_usage()
            return

        cmd = args[0]
        params = args[1:]

        pypi = self.pypi_factory('files', 'sqlite:///cluerelmgr.db')

        if cmd == 'updateuser':
            roledict = self.split_roles(*params[3:])
            pypi.security_manager.update_user(params[0],
                                              params[1],
                                              params[2],
                                              roledict.get('', []))
            for distro_id, roles in roledict.items():
                pypi.security_manager.update_roles(distro_id=distro_id,
                                                   username=params[0],
                                                   roles=roles)
        elif cmd == 'updategroup':
            roledict = self.split_roles(*params[1:])
            pypi.security_manager.update_group(params[0],
                                               roledict.get('', []))
            for distro_id, roles in roledict.items():
                pypi.security_manager.update_roles(distro_id=distro_id,
                                                   groupname=params[0],
                                                   roles=roles)
        elif cmd == 'updateusersgroups':
            username = params[0]
            pypi.security_manager.update_users_groups(params[0],
                                                      params[1:])
        elif cmd == 'addfile':

            def content(v):
                if v.startswith('http:') or v.startswith('https:'):
                    return utils.UrlContent(v)
                return utils.FileContent(v)

            distro_id = params[0]
            files = [content(x) for x in params[1:]]
            pypi.upload_files(distro_id, files)
        elif cmd == 'addindexentry':
            distro_id = params[0]
            indexname = params[1]
            target_distro_id = params[2]
            target_version = params[3]

            pypi.index_manager.add_index_item(distro_id, indexname,
                                              target_distro_id, target_version)
        elif cmd == 'delindexentry':
            distro_id = params[0]
            indexname = params[1]
            target_distro_id = params[2]

            pypi.index_manager.del_index_item(distro_id, indexname,
                                              target_distro_id)


main = Runner().main

if __name__ == '__main__':
    main()
