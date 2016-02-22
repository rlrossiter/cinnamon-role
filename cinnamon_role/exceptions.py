from tempest import exceptions


class CinnamonRoleException(exceptions.TempestException):
    pass


class RoleSetMixinMissingException(CinnamonRoleException):
    message = 'Missing RoleSetMixin class'
