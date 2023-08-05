"""Route and Mapper core classes"""

import re
import sys
import urllib
from util import _url_quote as url_quote
from util import controller_scan, RouteException
from routes import request_config

if sys.version < '2.4':
    from sets import ImmutableSet as frozenset

import threadinglocal

def strip_slashes(name):
    if name.startswith('/'):
        name = name[1:]
    if name.endswith('/'):
        name = name[:-1]
    return name

class Route(object):
    """The Route object holds a route recognition and generation routine.
    
    See Route.__init__ docs for usage.
    
    """
    
    def __init__(self, routepath, **kargs):
        """Initialize a route, with a given routepath for matching/generation
        
        The set of keyword args will be used as defaults.
        
        Usage::
        
            >>> from routes.base import Route
            >>> newroute = Route(':controller/:action/:id')
            >>> newroute.defaults
            {'action': 'index', 'id': None}
            >>> newroute = Route('date/:year/:month/:day', controller="blog", action="view")
            >>> newroute = Route('archives/:page', controller="blog", action="by_page", requirements = { 'page':'\d{1,2}' })
            >>> newroute.reqs
            {'page': '\\\d{1,2}'}
        
        .. Note:: 
            Route is generally not called directly, a Mapper instance connect method should
            be used to add routes.
        
        """
        
        self.routepath = routepath
        self.sub_domains = False
        
        # Don't bother forming stuff we don't need if its a static route
        self.static = kargs.get('_static', False)
        self.filter = kargs.pop('_filter', None)
        
        # Pull out route conditions
        self.conditions = kargs.pop('conditions', None)
        
        # reserved keys that don't count
        reserved_keys = ['requirements']
        
        # Strip preceding '/' if present
        if routepath.startswith('/'):
            routepath = routepath[1:]
        
        # Build our routelist, and the keys used in the route
        self.routelist = routelist = self._pathkeys(routepath)
        routekeys = frozenset([key['name'] for key in routelist if isinstance(key, dict)])
        
        # Build a req list with all the regexp requirements for our args
        self.reqs = kargs.get('requirements', {})
        self.req_regs = {}
        for key,val in self.reqs.iteritems():
            self.req_regs[key] = re.compile('^' + val + '$')
        # Update our defaults and set new default keys if needed. defaults needs to be saved
        (self.defaults, defaultkeys) = self._defaults(routekeys, reserved_keys, kargs)
        # Save the maximum keys we could utilize
        self.maxkeys = defaultkeys | routekeys
        # Populate our minimum keys, and save a copy of our backward keys for quicker generation later
        (self.minkeys, self.routebackwards) = self._minkeys(routelist[:])
        # Populate our hardcoded keys, these are ones that are set and don't exist in the route
        self.hardcoded = frozenset([key for key in self.maxkeys \
            if key not in routekeys and self.defaults[key] is not None])
    
    def _pathkeys(self, routepath):
        """Utility function to walk the route, and pull out the valid dynamic/wildcard keys"""
        collecting = False
        current = ''
        done_on = ''
        var_type = ''
        just_started = False
        routelist = []
        for char in routepath:
            if char in [':', '*'] and not collecting:
                just_started = True
                collecting = True
                var_type = char
                if len(current) > 0:
                    routelist.append(current)
                    current = ''
            elif collecting and just_started:
                just_started = False
                if char == '(':
                    done_on = ')'
                else:
                    current = char
                    done_on = '/'
            elif collecting and char != done_on:
                current += char
            elif collecting:
                collecting = False
                routelist.append(dict(type=var_type, name=current))
                if done_on == '/':
                    routelist.append(done_on)
                done_on = var_type = current = ''
            else:
                current += char
        if collecting:
            routelist.append(dict(type=var_type, name=current))
        elif current:
            routelist.append(current)
        return routelist
                
        
    def _minkeys(self, routelist):
        """Utility function to walk the route backwards
        
        Will also determine the minimum keys we can handle to generate a working route.
        
        routelist is a list of the '/' split route path
        defaults is a dict of all the defaults provided for the route
        
        """
        minkeys = []
        backcheck = routelist[:]
        gaps = False
        backcheck.reverse()
        for part in backcheck:
            if not isinstance(part, dict) and part != '/':
                gaps = True
                continue
            elif not isinstance(part, dict):
                continue
            key = part['name']
            if self.defaults.has_key(key) and not gaps:
                continue
            minkeys.append(key)
            gaps = True
        return  (frozenset(minkeys), backcheck)
    
    def _defaults(self, routekeys, reserved_keys, kargs):
        """Creates default set with values stringified
        
        Put together our list of defaults, stringify non-None values
        and add in our action/id default if they use it and didn't specify it
        
        defaultkeys is a list of the currently assumed default keys
        routekeys is a list of the keys found in the route path
        reserved_keys is a list of keys that are not
        
        """
        defaults = {}
        # Add in a controller/action default if they don't exist
        if 'controller' not in routekeys and 'controller' not in kargs:
            kargs['controller'] = 'content'
        if 'action' not in routekeys and 'action' not in kargs:
            kargs['action'] = 'index'
        defaultkeys = frozenset([key for key in kargs.keys() if key not in reserved_keys])
        for key in defaultkeys:
            if kargs[key] != None:
                defaults[key] = str(kargs[key])
            else:
                defaults[key] = None
        if 'action' in routekeys and not defaults.has_key('action'):
            defaults['action'] = 'index'
        if 'id' in routekeys and not defaults.has_key('id'):
            defaults['id'] = None
        newdefaultkeys = frozenset([key for key in defaults.keys() if key not in reserved_keys])
        return (defaults, newdefaultkeys)
        
    def makeregexp(self, clist):
        """Create a regular expression for matching purposes
        
        Note: This MUST be called before match can function properly.
        
        clist should be a list of valid controller strings that can be matched, for this reason
        makeregexp should be called by the web framework after it knows all available controllers
        that can be utilized
        
        """        
        (reg, noreqs, allblank) = self.buildnextreg(self.routelist, clist)
        
        if not reg: reg = '/'
        reg = reg + '(/)?' + '$'
        if not reg.startswith('/'):
            reg = '/' + reg
        reg = '^' + reg
        
        self.regexp = reg
        self.regmatch = re.compile(reg)
    
    def buildnextreg(self, path, clist):
        """Recursively build our regexp given a path, and a controller list.
        
        Returns the regular expression string, and two booleans that can be ignored as
        they're only used internally by buildnextreg
        
        """
        if path:
            part = path[0]
        else:
            part = ''
        reg = ''
        
        # noreqs will remember whether the remainder has either a string match, or a non-defaulted
        # regexp match on a key, allblank remembers if the rest could possible be completely empty
        (rest, noreqs, allblank) = ('', True, True)
        if len(path[1:]) > 0:
            (rest, noreqs, allblank) = self.buildnextreg(path[1:], clist)
        
        if isinstance(part, dict) and part['type'] == ':':
            var = part['name']
            partreg = ''
            
            # First we plug in the proper part matcher
            if self.reqs.has_key(var):
                partreg = '(?P<' + var + '>' + self.reqs[var] + ')'
            elif var == 'controller':
                partreg = '(?P<' + var + '>' + '|'.join(map(re.escape, clist)) + ')'
            else:
                if len(path) > 1:
                    partreg = '(?P<' + var + '>[^' + path[1][0] +']+)'
                else:
                    partreg = '(?P<' + var + '>[^/]+)'
            
            if self.reqs.has_key(var): noreqs = False
            if not self.defaults.has_key(var): 
                allblank = False
                noreqs = False
            
            # Now we determine if its optional, or required. This changes depending on what is in
            # the rest of the match. If noreqs is true, then its possible the entire thing is optional
            # as there's no reqs or string matches.
            if noreqs:
                # The rest is optional, but now we have an optional with a regexp. Wrap to ensure that if we match
                # anything, we match our regexp first. It's still possible we could be completely blank as we have
                # a default
                if self.reqs.has_key(var) and self.defaults.has_key(var):
                    reg = '(' + partreg + rest + ')?'
                
                # Or we have a regexp match with no default, so now being completely blank form here on out isn't
                # possible
                elif self.reqs.has_key(var):
                    allblank = False
                    reg = partreg + rest
                
                # Or we have a default with no regexp, don't touch the allblank
                elif self.defaults.has_key(var):
                    reg = partreg + '?' + rest
                
                # Or we have a key with no default, and no reqs. Not possible to be all blank from here
                else:
                    allblank = False
                    reg = partreg + rest
            # In this case, we have something dangling that might need to be matched
            else:
                # If they can all be blank, and we have a default here, we know its
                # safe to make everything from here optional. Since something else in
                # the chain does have req's though, we have to make the partreg here
                # required to continue matching
                if allblank and self.defaults.has_key(var):
                    reg = '(' + partreg + rest + ')?'
                    
                # Same as before, but they can't all be blank, so we have to require it all to ensure
                # our matches line up right
                else:
                    reg = partreg + rest
        elif isinstance(part, dict) and part['type'] == '*':
            var = part['name']
            if noreqs:
                if self.defaults.has_key(var):
                    reg = '(?P<' + var + '>.*)' + rest
                else:
                    reg = '(?P<' + var + '>.*)' + rest
                    allblank = False
                    noreqs = False
            else:
                if allblank and self.defaults.has_key(var):
                    reg = '(?P<' + var + '>.*)' + rest
                elif self.defaults.has_key(var):
                    reg = '(?P<' + var + '>.*)' + rest
                else:
                    allblank = False
                    noreqs = False
                    reg = '(?P<' + var + '>.*)' + rest
        elif part.endswith('/'):
            if allblank:
                reg = re.escape(part[:-1]) + '(/' + rest + ')?'
            else:
                allblank = False
                reg = re.escape(part) + rest
        
        # We have a normal string here, this is a req, and it prevents us from being all blank
        else:
            noreqs = False
            allblank = False
            reg = re.escape(part) + rest
        
        return (reg, noreqs, allblank)
    
    def match(self, url, environ=None, sub_domains=False, sub_domains_ignore=None, domain_match=''):
        """Match a url to our regexp. 
        
        While the regexp might match, this operation isn't
        guaranteed as there's other factors that can cause a match to fail even though
        the regexp succeeds (Default that was relied on wasn't given, requirement regexp
        doesn't pass, etc.).
        
        Therefore the calling function shouldn't assume this will return a valid dict, the
        other possible return is False if a match doesn't work out.
        
        """
        # Static routes don't match, they generate only
        if self.static:
            return False
        
        if url.endswith('/') and len(url) > 1:
            url = url[:-1]
        m = self.regmatch.match(url)
        
        if not m: return False
            
        if not environ: environ = {}
        
        sub_domain = None
        
        if environ.get('HTTP_HOST') and sub_domains:
            host = environ['HTTP_HOST'].split(':')[0]
            sub_match = re.compile('^(.+?)\.%s$' % domain_match)
            subdomain = re.sub(sub_match, r'\1', host)
            if subdomain not in sub_domains_ignore and host != subdomain:
                sub_domain = subdomain
        
        if self.conditions:
            if self.conditions.has_key('method') and \
                environ.get('REQUEST_METHOD') not in self.conditions['method']:
                return False
            
            # Check sub-domains?
            use_sd = self.conditions.get('sub_domain')
            if use_sd and not sub_domain:
                return False
            if isinstance(use_sd, list) and sub_domain not in use_sd:
                return False
        
        matchdict = m.groupdict()
        result = {}
        extras = frozenset(self.defaults.keys()) - frozenset(matchdict.keys())
        for key,val in matchdict.iteritems():
            if not val and self.defaults.has_key(key) and self.defaults[key]:
                result[key] = self.defaults[key]
            else:
                result[key] = val
        for key in extras:
            result[key] = self.defaults[key]
        
        # Add the sub-domain if there is one
        if sub_domains: result['sub_domain'] = sub_domain
        
        # If there's a function, call it with environ and expire if it
        # returns False
        if self.conditions and self.conditions.has_key('function') and \
            not self.conditions['function'](environ, result):
            return False
        
        return result
    
    def generate(self, _ignore_req_list=False, **kargs):
        """Generate a URL from ourself given a set of keyword arguments
        
        Toss an exception if this
        set of keywords would cause a gap in the url.
        
        """
        # Verify that our args pass any regexp requirements
        if not _ignore_req_list:
            for key in self.reqs.keys():
                val = kargs.get(key)
                if val and not self.req_regs[key].match(str(val)):
                    return False
        
        # Verify that if we have a method arg, its in the method accept list. Also, method
        # will be changed to _method for route generation
        meth = kargs.get('method')
        if meth:
            if self.conditions and 'method' in self.conditions \
                and meth.upper() not in self.conditions['method']:
                return False
            kargs.pop('method')
        
        routelist = self.routebackwards
        urllist = []
        gaps = False
        for part in routelist:
            if isinstance(part, dict) and part['type'] == ':':
                arg = part['name']
                
                # For efficiency, check these just once
                has_arg = kargs.has_key(arg)
                has_default = self.defaults.has_key(arg)
                
                # Determine if we can leave this part off
                # First check if the default exists and wasn't provided in the call (also no gaps)
                if has_default and not has_arg and not gaps:
                    continue
                    
                # Now check to see if there's a default and it matches the incoming call arg
                if (has_default and has_arg) and str(kargs[arg]) == str(self.defaults[arg]) and not gaps: 
                    continue
                
                # We need to pull the value to append, if the arg is None and we have a default, use that
                if has_arg and kargs[arg] is None and has_default and not gaps:
                    continue
                
                # Otherwise if we do have an arg, use that
                elif has_arg:
                    val = kargs[arg]
                
                elif has_default and self.defaults[arg] is not None:
                    val = self.defaults[arg]
                
                # No arg at all? This won't work
                else:
                    return False
                
                urllist.append(url_quote(val))
                if has_arg: del kargs[arg]
                gaps = True
            elif isinstance(part, dict) and part['type'] == '*':
                arg = part['name']
                kar = kargs.get(arg)
                if kar is not None:
                    urllist.append(url_quote(kar))
                    gaps = True
            elif part.endswith('/'):
                if not gaps and part == '/':
                    continue
                elif not gaps:
                    urllist.append(part[:-1])
                    gaps = True
                else:
                    gaps = True
                    urllist.append(part)
            else:
                gaps = True
                urllist.append(part)
        urllist.reverse()
        url = ''.join(urllist)
        if not url.startswith('/'):
            url = '/' + url
        extras = frozenset(kargs.keys()) - self.maxkeys
        if extras:
            url += '?'
            url += urllib.urlencode([(key, kargs[key]) for key in kargs if key in extras and \
                                     (key != 'action' or key != 'controller')])
        return url
    

class Mapper(object):
    """Mapper handles URL generation and URL recognition in a web application.
    
    Mapper is built handling dictionary's. It is assumed that the web application will handle
    the dictionary returned by URL recognition to dispatch appropriately.
    
    URL generation is done by passing keyword parameters into the generate function, a URL is then
    returned.
        
    """
    def __init__(self, controller_scan=controller_scan, directory=None, 
                 always_scan=False, register=True):
        """Create a new Mapper instance
        
        All keyword arguments are optional.

        ``controller_scan``
            Function reference that will be used to return a list of valid controllers used
            during URL matching. If ``directory`` keyword arg is present, it will be passed
            into the function during its call. This option defaults to a function that will
            scan a directory for controllers.

        ``directory``
            Passed into controller_scan for the directory to scan. It should be an absolute
            path if using the default ``controller_scan`` function.

        ``always_scan``
            Whether or not the ``controller_scan`` function should be run during every URL
            match. This is typically a good idea during development so the server won't need
            to be restarted anytime a controller is added.
        
        ``register``
            Boolean used to determine if the Mapper should use ``request_config`` to register
            itself as the mapper. Since it's done on a thread-local basis, this is typically
            best used during testing though it won't hurt in other cases.
        
        """
        self.matchlist = []
        self.maxkeys = {}
        self.minkeys = {}
        self.urlcache = {}
        self._created_regs = False
        self._created_gens = False
        self.prefix = None
        self.environ = None
        self.req_data = threadinglocal.local()
        self.directory = directory
        self.always_scan = always_scan
        self.controller_scan = controller_scan
        self._regprefix = None
        self._routenames = {}
        self.debug = False
        self.append_slash = False
        self.sub_domains = False
        self.sub_domains_ignore = []
        self.domain_match = '[^\.\/]+?\.[^\.\/]+'
        if register:
            config = request_config()
            config.mapper = self
    
    def connect(self, *args, **kargs):
        """Create and connect a new Route to the Mapper.
        
        Usage:
        
        .. code-block:: Python
        
            m = Mapper()
            m.connect(':controller/:action/:id')
            m.connect('date/:year/:month/:day', controller="blog", action="view")
            m.connect('archives/:page', controller="blog", action="by_page",
            requirements = { 'page':'\d{1,2}' })
            m.connect('category_list', 'archives/category/:section', controller='blog', action='category',
            section='home', type='list')
            m.connect('home', '', controller='blog', action='view', section='home')
        
        """
        routename = None
        if len(args) > 1:
            routename = args[0]
            args = args[1:]
        route = Route(*args, **kargs)
        self.matchlist.append(route)
        if routename:
            self._routenames[routename] = route
        if route.static:
            return
        exists = False
        for key in self.maxkeys:
            if key == route.maxkeys:
                self.maxkeys[key].append(route)
                exists = True
                break
        if not exists:
            self.maxkeys[route.maxkeys] = [route]
        self._created_gens = False
    
    def _create_gens(self):
        """Create the generation hashes for route lookups"""
        # Use keys temporailly to assemble the list to avoid excessive
        # list iteration testing with "in"
        controllerlist = {}
        actionlist = {}
        
        # Assemble all the hardcoded/defaulted actions/controllers used
        for route in self.matchlist:
            if route.static: continue
            if route.defaults.has_key('controller'):
                controllerlist[route.defaults['controller']] = True
            if route.defaults.has_key('action'):
                actionlist[route.defaults['action']] = True
        
        # Setup the lists of all controllers/actions we'll add each route
        # to. We include the '*' in the case that a generate contains a
        # controller/action that has no hardcodes
        controllerlist = controllerlist.keys() + ['*']
        actionlist = actionlist.keys() + ['*']
        
        # Go through our list again, assemble the controllers/actions we'll
        # add each route to. If its hardcoded, we only add it to that dict key.
        # Otherwise we add it to every hardcode since it can be changed.
        gendict = {} # Our generated two-deep hash
        for route in self.matchlist:
            if route.static: continue
            clist = controllerlist
            alist = actionlist
            if 'controller' in route.hardcoded:
                clist = [route.defaults['controller']]
            if 'action' in route.hardcoded:
                alist = [str(route.defaults['action'])]
            for controller in clist:
                for action in alist:
                    actiondict = gendict.setdefault(controller, {})
                    actiondict.setdefault(action, ([], {}))[0].append(route)
        self._gendict = gendict
        self._created_gens = True
    
    def create_regs(self, clist=None):
        """Creates regular expressions for all connected routes"""
        if clist is None:
            if self.directory:
                clist = self.controller_scan(self.directory)
            else:
                clist = self.controller_scan()
            
        for key,val in self.maxkeys.iteritems():
            for route in val:
                route.makeregexp(clist)
        
        
        # Create our regexp to strip the prefix
        if self.prefix:
            self._regprefix = re.compile(self.prefix + '(.*)')
        self._created_regs = True
    
    def _match(self, url):
        """Internal Route matcher
        
        Matches a URL against a route, and returns a tuple of the match dict
        and the route object if a match is successfull, otherwise it returns empty.
        
        For internal use only.
        
        """
        if not self._created_regs and self.controller_scan:
            self.create_regs()
        elif not self._created_regs:
            raise RouteException, "You must generate the regular expressions before matching."
        
        if self.always_scan:
            self.create_regs()
        
        matchlog = []
        if self.prefix:
            if re.match(self._regprefix, url):
                url = re.sub(self._regprefix, r'\1', url)
                if not url:
                    url = '/'
            else:
                return (None, None, matchlog)
        for route in self.matchlist:
            if route.static:
                if self.debug: matchlog.append(dict(route=route, static=True))
                continue
            match = route.match(url, self.environ, self.sub_domains, 
                self.sub_domains_ignore, self.domain_match)
            if self.debug: matchlog.append(dict(route=route, regexp=bool(match)))
            if match:
                return (match, route, matchlog)
        return (None, None, matchlog)
        
    def match(self, url):
        """Match a URL against against one of the routes contained.
        
        Will return None if no valid match is found.
        
        .. code-block:: Python
            
            resultdict = m.match('/joe/sixpack')
        
        """
        result = self._match(url)
        if self.debug:
            return result[0], result[1], result[2]
        if result[0]:
            return result[0]
        return None
        
    def routematch(self, url):
        """Match a URL against against one of the routes contained.
        
        Will return None if no valid match is found, otherwise a
        result dict and a route object is returned.
        
        .. code-block:: Python
        
            resultdict, route_obj = m.match('/joe/sixpack')
        
        """
        result = self._match(url)
        if self.debug:
            return result[0], result[1], result[2]
        if result[0]:
            return result[0], result[1]
        return None
        
    
    def generate(self, controller='content', action='index', **kargs):
        """Generate a route from a set of keywords
        
        Returns the url text, or None if no URL could be generated.
        
        .. code-block:: Python
            
            m.generate(controller='content',action='view',id=10)
        
        """
        # Generate ourself if we haven't already
        if not self._created_gens:
            self._create_gens()
        
        kargs['controller'] = controller
        kargs['action'] = action
        
        # Check the url cache to see if it exists, use it if it does
        if str(kargs) in self.urlcache:
            return self.urlcache[str(kargs)]
        
        actionlist = self._gendict.get(controller) or self._gendict.get('*')
        if not actionlist: return None
        (keylist, sortcache) = actionlist.get(action) or actionlist.get('*', (None, None))
        if not keylist: return None
        
        keys = frozenset(kargs.keys())
        cacheset = False
        cachekey = str(keys)
        cachelist = sortcache.get(cachekey)
        if cachelist:
            keylist = cachelist
        else:
            cacheset = True
            newlist = []
            for route in keylist:
                if len(route.minkeys-keys) == 0:
                    newlist.append(route)
            keylist = newlist
            
            def keysort(a, b):
                am = a.minkeys
                a = a.maxkeys
                b = b.maxkeys
                
                lendiffa = len(keys^a)
                lendiffb = len(keys^b)
                # If they both match, don't switch them
                if lendiffa == 0 and lendiffb == 0:
                    return 0
                
                # First, if a matches exactly, use it
                if lendiffa == 0:
                    return -1
                
                # Or b matches exactly, use it
                if lendiffb == 0:
                    return 1
                
                # Neither matches exactly, return the one with the most in common
                if cmp(lendiffa,lendiffb) != 0:
                    return cmp(lendiffa,lendiffb)
                
                # Neither matches exactly, but if they both have just as much in common
                if len(keys&b) == len(keys&a):
                    return cmp(len(a),len(b))     # Then we return the shortest of the two
                
                # Otherwise, we return the one that has the most in common
                else:
                    return cmp(len(keys&b), len(keys&a))
            
            keylist.sort(keysort)
            if cacheset:
                sortcache[cachekey] = keylist
        
        for route in keylist:
            fail = False
            for key in route.hardcoded:
                kval = kargs.get(key)
                if not kval: continue
                if kval != route.defaults[key]:
                    fail = True
                    break
            if fail: continue
            path = route.generate(**kargs)
            if path:
                if self.prefix:
                    path = self.prefix + path
                if self.environ and self.environ.get('SCRIPT_NAME', '') != '':
                    path = self.environ['SCRIPT_NAME'] + path
                if self.urlcache is not None:
                    self.urlcache[str(kargs)] = path
                return path
            else:
                continue
        return None
    
    def resource(self, controller_name, **kwargs):
        """Generate routes for a controller resource
        
        The controller should be the name of the controller for which a set
        of resource-based Routes should be generated. The concept of a web
        resource maps somewhat directly to 'CRUD' operations. The overlying
        things to keep in mind is that mapping a resource is about handling
        creating, viewing, and editing that resource.
        
        All keyword arguments are optional.
        
        ``controller``
            If specified in the keyword args, the controller will be the actual
            controller used, but the rest of the naming conventions used for
            the route names and URL paths are unchanged.
        
        ``collection``
            Additional action mappings used to manipulate/view the entire set of
            resources provided by the controller.
            
            Example::
                
                map.resource('message', collection={'rss':'GET'})
                # GET /message;rss (maps to the rss action)
                # also adds named route "rss_message"
        
        ``member``
            Additional action mappings used to access an individual 'member'
            of this controllers resources.
            
            Example::
                
                map.resource('message', member={'mark':'POST'})
                # POST /message/1;mark (maps to the mark action)
                # also adds named route "mark_message"
        
        ``new``
            Action mappings that involve dealing with a new member in the
            controller resources.
            
            Example::
                
                map.resource('message', new={'preview':'POST'})
                # POST /message/new;preview (maps to the preview action)
                # also adds a url named "preview_new_message"
        
        ``path_prefix``
            Prepends the URL path for the Route with the path_prefix given.
            This is most useful for cases where you want to mix resources
            or relations between resources.
        
        ``name_prefix``
            Perpends the route names that are generated with the name_prefix
            given. Combined with the path_prefix option, it's easy to
            generate route names and paths that represent resources that are
            in relations.
            
            Example::
                
                map.resource('message', controller='categories', 
                    path_prefix='/category/:category_id', name_prefix="category_")
                # GET /category/7/message/1
                # has named route "category_message"
        
        """
        controller = controller_name
        collection = kwargs.pop('collection', {})
        member = kwargs.pop('member', {})
        new = kwargs.pop('new', {})
        path_prefix = kwargs.pop('path_prefix', '')
        name_prefix = kwargs.pop('name_prefix', '')
        
        # Ensure the edit and new actions are in and GET
        member['edit'] = 'GET'
        new.update({'new': 'GET'})
        
        # Make new dict's based off the old, except the old values become keys,
        # and the old keys become items in a list as the value
        def swap(dct, newdct):
            for key, val in dct.iteritems():
                newdct.setdefault(val.upper(), []).append(key)
            return newdct
        collection_methods = swap(collection, {})
        member_methods = swap(member, {})
        new_methods = swap(new, {})
        
        # Insert create, update, and destroy methods
        collection_methods.setdefault('POST', []).insert(0, 'create')
        member_methods.setdefault('PUT', []).insert(0, 'update')
        member_methods.setdefault('DELETE', []).insert(0, 'delete')
        
        # If there's a path prefix option, use it with the controller
        controller = strip_slashes(controller)
        path_prefix = strip_slashes(path_prefix)
        if path_prefix:
            path = path_prefix + '/' + controller
        else:
            path = controller
        collection_path = path
        new_path = path + "/new"
        member_path = path + "/:(id)"
        
        options = {'controller':kwargs.get('controller', controller)}
        
        def requirements_for(meth):
            """Returns a new dict to be used for all route creation as the
            route options"""
            opts = options.copy()
            if method != 'any': 
                opts['conditions'] = {'method':[meth.upper()]}
            return opts
        
        # Add the routes for handling collection methods
        for method, lst in collection_methods.iteritems():
            primary = (method != 'GET' and lst.pop(0)) or None
            route_options = requirements_for(method)
            for action in lst:
                route_options['action'] = action
                route_name = "%s%s_%s" % (name_prefix, action, controller)
                self.connect(route_name, "%s;%s" % (collection_path, action), **route_options)
                self.connect("formatted_" + route_name, "%s.:(format);%s" % (collection_path, action))
            if primary:
                route_options['action'] = primary
                self.connect(collection_path, **route_options)
                self.connect("%s.:(format)" % collection_path, **route_options)
        
        # Specifically add in the built-in 'index' collection method and its formatted
        # version
        self.connect(name_prefix + controller, collection_path, action='index', 
            conditions={'method':['GET']}, **options)
        self.connect("formatted_" + name_prefix + controller, 
            collection_path + ".:(format)", action='index', 
            conditions={'method':['GET']}, **options)
        
        # Add the routes that deal with new resource methods
        for method, lst in new_methods.iteritems():
            route_options = requirements_for(method)
            for action in lst:
                path = (action == 'new' and new_path) or "%s;%s" % (new_path, action)
                name = "new_" + controller
                if action != 'new': name = action + "_" + name
                route_options['action'] = action
                self.connect(name_prefix + name, path, **route_options)
                path = (action == 'new' and new_path + '.:(format)') or \
                    "%s.:(format);%s" % (new_path, action)
                self.connect("formatted_" + name_prefix + name, path, **route_options)
        
        # Add the routes that deal with member methods of a resource
        for method, lst in member_methods.iteritems():
            route_options = requirements_for(method)
            route_options['requirements'] = {'id':'\w+'}
            if method not in ['POST', 'GET', 'any']:
                primary = lst.pop(0)
            else:
                primary = None
            for action in lst:
                route_options['action'] = action
                self.connect("%s%s_%s" % (name_prefix, action, controller),
                    "%s;%s" % (member_path, action), **route_options)
                self.connect("formatted_%s%s_%s" % (name_prefix, action, controller),
                    "%s.:(format);%s" % (member_path, action), **route_options)
            if primary:
                route_options['action'] = primary
                self.connect(member_path, **route_options)
        
        # Specifically add the member 'show' method
        route_options = requirements_for('GET')
        route_options['action'] = 'show'
        route_options['requirements'] = {'id':'\w+'}
        self.connect(name_prefix + controller, member_path, **route_options)
        self.connect("formatted_" + name_prefix + controller, member_path + ".:(format)",
            **route_options)
    
