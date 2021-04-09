# import all of radicale's internal rights modules
from radicale.rights import BaseRights, INTERNAL_TYPES

from radicale.log import logger

from functools import reduce
from importlib import import_module
from os import path as p

name = "radicale-rights-combine"
builtin_rights = {intype:
                  import_module("radicale.rights.{}".format(intype)).Rights
                  for intype in INTERNAL_TYPES}


def rights_union(a, b):
    return "".join(set(a).union(set(b)))


class Rights(BaseRights):
    def __init__(self, configuration):
        super().__init__(configuration)
        types = map(str.strip,
                    self.configuration.get("rights", "types").split(","))
        self.rights = {
            s: self.init_right(s, configuration)
            for s in types
        }
        if "resolve_symlinks" not in self.configuration.options("rights"):
            self.resolve_symlinks = True
        else:
            self.resolve_symlinks = self.configuration.get("rights",
                                                           "resolve_symlinks")
        if self.resolve_symlinks:
            filesystem_folder = self.configuration.get("storage",
                                                       "filesystem_folder")
            self.storepath = p.join(filesystem_folder, "collection-root")
            self.authorization = self.__authorized_resolve_symlinks
        else:
            self.authorization = self.__authorized

    @staticmethod
    def init_right(right_name, configuration):
        if right_name in builtin_rights.keys():
            return builtin_rights[right_name](configuration)
        else:
            return import_module(right_name).Rights(configuration)

    def __authorized_resolve_symlinks(self, user, path):
        fullpath = p.join(self.storepath, path.strip("/"))
        if p.islink(fullpath):
            target = p.realpath(fullpath)
            path = target.replace(self.storepath, "")
        return self.__authorized(user, path)

    def __authorized(self, user, path):
        logger.debug(
            """Using plugins %r to determine rights for request:
                User %r access path %r.""",
            self.rights.keys(), user, path)
        rights = reduce(rights_union,
                        (right.authorization(user, path)
                         for right in self.rights.values()),
                        "")
        logger.debug("The union of returned rights was: %r",
                     rights)
        return rights
