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


class Rights(rights.BaseRights):
    def __init__(self, configuration, logger):
        super().__init__(configuration, logger)
        types = list(
            map(str.split,
                self.configuration.get("rights", "ldap_url").split(",")))
        self.rights = {
            s: init_right(s, configuration, logger)
            for s in self.types
        }

    @staticmethod
    def init_right(right_name, configuration, logger):
        if right_name in builtin_rights.keys():
            return builtin_rights[right_name]
        else:
            return import_module(right_name).Rights(configuration, logger)

    def authorized(self, user, path, permissions):
        self.logger.debug(
            """Using plugins %r to determine rights for request:
                User %r access path %r with permissions %r.""",
            self.rights.keys(), user, path, permissions)
        results = {
            name: right.authorized(user, path, permissions)
            for name, right in self.rights
        }
        if any(results.values()):
            auth_plugs = [plug for plug, auth in results.values() if auth]
            self.logger.debug("Plugins %r authorized access.", auth_plugs)
            return true
        else:
            self.logger.debug(
                "No pluging authorized the request. Denying access.")
            return false
