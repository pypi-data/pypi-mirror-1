from xix.utils.python import ModuleWrapper

class ModuleWrapperTest:
    def importAll(self):
        '''Example Usage:

        >>> "uppercase" not in locals()
        True
        >>> wrapper = ModuleWrapper("string")
        >>> wrapper.importAll()
        >>> print uppercase
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        '''
    def importModule(self):
        '''Example Usage:

        >>> "sre" not in locals()
        True
        >>> wrapper = ModuleWrapper("sre")
        >>> wrapper.importModule()
        >>> type(sre)
        <type 'module'>
        '''
    def importNames(self, *names):
        '''Example Usage:

        >>> "uppercase" not in locals() and "upper" not in locals()
        True
        >>> wrapper = ModuleWrapper("string")
        >>> wrapper.importNames("uppercase", "upper")
        >>> print uppercase
        ABCDEFGHIJKLMNOPQRSTUVWXYZ
        >>> print upper("lower")
        LOWER
        '''
