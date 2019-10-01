from radicale.rights import (
    BaseRights,
    AuthenticatedRights,
    OwnerWriteRights,
    OwnerOnlyRights,
    Rights,
)
from importlib import import_module

name = "radicale-rights-combine"
builtin_rights = {
    "authenticated": AuthenticatedRights,
    "owner_write": OwnerWriteRights,
    "owner_only": OwnerOnlyRights,
    "from_file": Rights
}


class Rights(BaseRights):
    def __init__(self, configuration, logger):
        super().__init__(configuration, logger)
        types = map(str.strip,
                    self.configuration.get("rights", "types").split(","))
        self.rights = {
            s: self.init_right(s, configuration, logger)
            for s in types
        }

    @staticmethod
    def init_right(right_name, configuration, logger):
        if right_name in builtin_rights.keys():
            return builtin_rights[right_name](configuration, logger)
        else:
            return import_module(right_name).Rights(configuration, logger)

    def authorized(self, user, path, permissions):
        self.logger.debug(
            """Using plugins %r to determine rights for request:
                User %r access path %r with permissions %r.""",
            self.rights.keys(), user, path, permissions)
        results = (
            right.authorized(user, path, permissions)
            for right in self.rights.values()
        )
        if any(results):
            self.logger.debug("One of the plugins authorized access.")
            return True
        else:
            self.logger.debug(
                "No pluging authorized the request. Denying access.")
            return False
