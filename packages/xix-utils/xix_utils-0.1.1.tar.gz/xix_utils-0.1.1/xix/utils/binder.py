"""Bind names to object instances.
"""

from xix.utils.comp.interface import implements
from xix.utils.interfaces import IBindingRequest, IBindingFactory

_global_binding_registry = {}
_binding_context_regsitry = {}
_request_list = []

class BindingRequest:
    """A binding request consists of a name to bind to corresponding instance(s).

    BindingRequest provides the IBindingRequest interface.

    >>> br = BindingRequest('object1', object, bundlect=23) 
    >>> from xix.utils.comp.interface import providedBy
    >>> from xix.utils.interfaces import IBindingRequest
    >>> int(IBindingRequest.providedBy(br))
    1
    """

    implements(IBindingRequest)

    def __init__(self, name, creator, shared=False, bundlect=1, maxcount=0,
            initargs=None, initkwargs=None):
        """
        @param name: the name to bind to
        @param creator: Class object or callable that returns instance of object
        @param shared: One instance or bundles of instances shared by threads.
        @param bundlect: bundle count for bundled sharing
        @param maxct: max number of instances to create, or 0 for no limit
        @param initargs: initialization positional args for creator
        @param initkwargs: initialization keyword args for creator
        """
        self.name = name
        self.creator = creator
        self.shared = shared
        self.bundlect = bundlect
        self.maxcount = maxcount
        self.initargs = initargs or []
        self.initkwargs = initkwargs or {}
        self.stack = []
        self.createdct = 0

class BindingException:
    pass

class BindingOverflowException:
    pass


class BindingFactory:
    """Contains list
    """

    implements(IBindingFactory)

    def bind(self, bindingRequest):
        """Given a binding request, return binding.

        Example usage:

        >>> br = BindingRequest('a', object)
        >>> factory = BindingFactory()
        >>> o1 = factory.bind(br)
        >>> o2 = factory.bind(br)
        >>> int(isinstance(o1, object))
        1
        >>> int(isinstance(o2, object))
        1
        >>> int(o1 != o2)
        1

        Singleton pattern:

        >>> br = BindingRequest('b', object, shared=True)
        >>> o1, o2 = factory.bind(br), factory.bind(br)
        >>> int(o1 == o2)
        1
        >>> int(isinstance(o1, object))
        1

        @param bindingRequest: IBindingRequest provider
        """
        br = bindingRequest
        if not br.stack:
            binding = self.__prepbind(br)
            if binding:
                return binding
        try:
            binding = br.stack[0]
            if len(br.stack) > 1: #rotate to next in bundle
                br.stack = br.stack[1:] + [br.stack[0]]
            return binding
        except IndexError, ie:
            raise BindingException, \
                'No bindings could be created for %s :reason: %s' \
                    % (br.name, ie)


    def __prepbind(self, bindingRequest):
        br = bindingRequest
        if br.shared:
            instances = [ br.creator(*br.initargs, **br.initkwargs) \
                for _ in range(br.bundlect) ]
            br.stack = instances
        else:
            if br.createdct == br.maxcount - 1:
                raise BindingOverflowException, \
                    "Bindings exceeded max count: %d" % br.maxcount
            return br. creator(*br.initargs, **br.initkwargs)
            


def bootstrap(registry=None, request_list=None, context_registry=None):
    """bootstrap this module with optional IRegisty provider and
    IList provider.

    Example usage:


    >>> from xix.utils import binder
    >>> from UserDict import UserDict
    >>> from UserList import UserList
    >>> ud, ul = UserDict(), UserList()
    >>> binder.bootstrap(registry=ud, request_list=ul, context_registry=ud)
    >>> int(binder._global_binding_registry == ud)
    1
    >>> int(binder._request_list == ul)
    1
    >>> int(binder._binding_context_regsitry == ud)
    1

    @param registry: IRegistry provider - registry holds bindings to instances
    @param request_list: IList provider - list of binding request used in
        startup phase to bind names to objects.
    """
    global _global_binding_registry, _request_list, _binding_context_regsitry
    _global_binding_registry = registry or _global_binding_registry
    _request_list = request_list or _request_list
    _binding_context_regsitry = context_registry or _binding_context_regsitry

# alias for bootstrap
init = bootstrap
    
