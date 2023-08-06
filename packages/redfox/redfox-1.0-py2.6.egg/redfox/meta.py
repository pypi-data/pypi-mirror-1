"""The bowels of redfox. This is where the metaclass that makes Redfox
app class instances into WSGI applications lives.
"""

from itertools import chain
from werkzeug.routing import Map, Rule, RuleFactory
from werkzeug import Request, ClosingIterator
from werkzeug.exceptions import HTTPException
from redfox.routing import routes

# Define a real, honest-to-Zod function named __call__ so that
# webapp-derived types look as normal as possible. This function
# gets reused for every single WebApplication-derived class's
# __call__ method.
def __call__(self, environ, start_response):
    """WSGI entry point. Routes requests to methods decorated by ``@route``
    and friends, then chains to the WSGI application (normally a
    ``werkzeug.Response``) returned by the endpoint method.
    
    The WSGI request environment is encapsulated in a ``werkzeug.Request``
    object, for convenience.
    """
    request = Request(environ)
    adapter = self.__rule_map__.bind_to_environ(environ)
    try:
        endpoint, values = adapter.match()
        handler = getattr(self, endpoint)
        response = handler(request, **values)
    except HTTPException, e:
        response = e
    return ClosingIterator(response(environ, start_response))

class WebApplication(type):
    """Instances of this metaclass are given the following attributes:
    
    ``__rule_defs__``
        A ``list`` of rule definitions suitable for constructing Rule objects.
    
    ``__rule_map__``
        A ``werkzeug.routing.Map`` object for identifying the appropriate
        method for each request. The ``Map`` is populated using rules from
        both the class's own routable methods and from any parents that look
        like they might have rule definitions.
    
    ``__call__``
        A WSGI entry point method that uses ``__rule_map__`` to route requests.
    """
    def __new__(meta, name, bases, dict):
        dict['__rule_defs__'] = rule_defs = list(meta.extract_rule_defs(dict))
        rules = [Rule(*args, **kwargs) for args, kwargs in rule_defs]
        
        inherited_rule_defs = chain(*[
            base.__rule_defs__ for base in bases if hasattr(base, '__rule_defs__')
        ])
        inherited_rules = [Rule(*args, **kwargs) for args, kwargs in inherited_rule_defs]
        dict['__rule_map__'] = Map(rules + inherited_rules)
        dict['__call__'] = __call__
        
        return type.__new__(meta, name, bases, dict)

    @classmethod
    def extract_rule_defs(meta, attributes):
        """Extracts rule definitions from all routable objects in the
        ``attributes`` dictionary and returns them in a flat sequence.
        """
        for name, method in attributes.iteritems():
            for rule in meta.to_rules(name, method):
                yield rule
    
    @classmethod
    def to_rules(meta, name, method):
        """Extracts the route definitions from a method, adding some
        metadata necessary to route requests to methods.
        """
        # We use the name here so that requests routed to a child class
        # prefer the child class's version of an overridden method, rather
        # than the parent's. See __call__ for the other half of the
        # equation.
        return routes(method, endpoint=name)
