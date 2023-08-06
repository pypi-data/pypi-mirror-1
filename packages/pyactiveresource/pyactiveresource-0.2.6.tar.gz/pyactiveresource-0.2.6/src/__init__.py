from urlparse import urlparse
import httplib
import urllib
import base64
from sys import version_info

if version_info >= (2, 5):
    from xml.etree import cElementTree as ElementTree
else:
    try:
        import cElementTree as ElementTree
    except ImportError:
        try:
            from elementtree import ElementTree
        except ImportError:
            raise Exception('ElementTree must be installed')
            
class Object(object):
    'A blank object'
    pass
                
class ActiveResourceException(Exception):
    pass

class ActiveResourceMeta(type):
    
    def __new__(cls, name, bases, attrs):
        if name == 'ActiveResource':
            return super(ActiveResourceMeta, cls).__new__(cls, name, bases, attrs)
        
        klass = type.__new__(cls, name, bases, attrs)
        
        if not klass.Meta.site:
            raise ActiveResourceException('Site attribute must be set for %s' % name)
        
        klass.Meta.parsed_site = urlparse(klass.Meta.site)
        
        if klass.Meta.parsed_site[0] not in ('http', 'https'):
            raise ActiveResourceException('Only http and https protocols are allowed')
        
        klass.Meta.conntype = getattr(httplib, '%sConnection' % klass.Meta.parsed_site[0].upper())
        klass.Meta.host = klass.Meta.parsed_site[1]
        
        if '@' in klass.Meta.parsed_site[1]:
            auth, path = klass.Meta.parsed_site[1].split('@')
            klass.Meta.auth = base64.b64encode(auth)
            # httplib doesn't like the auth string inside the host
            klass.Meta.host = path
        
        klass.Meta.name = name.lower()
        if not getattr(klass.Meta, 'name_plural', None):
            klass.Meta.name_plural = '%ss' % klass.Meta.name
        klass.Meta.path_root = '%s%s' % (klass.Meta.parsed_site[2], klass.Meta.name_plural)
        klass.Meta.base_path = '%s.xml' % klass.Meta.path_root
        
        return klass

class ActiveResource(object):
    __metaclass__ = ActiveResourceMeta
    
    class Meta:
        site = None
        auth = None
    
    def __init__(self, **kwargs):
        self.Meta.changed = []
        
        [setattr(self, k, v) for k, v in kwargs.iteritems()]
        if kwargs.get('_record_exists'):
            # Clearing the changed state of attrs set above
            self.Meta.changed = []
            
    def __setattr__(self, name, value):
        self.Meta.changed.append(name)
        self.__dict__[name] = value
        
    def destroy(self):
        status, xml = self.__class__._make_request(obj=self, method='DELETE')
        return str(status[0]).startswith('2')
            
    def find(cls, _object_id=None, **kwargs):
        if _object_id:
            return cls.find(id=_object_id)[0]
        status, xml = cls._make_request(params=kwargs)
        # Allow any 2xx code
        if not str(status[0]).startswith('2'):
            raise ActiveResourceException('%s: %s' % (status, xml))
        return cls._parse_xml(xml)
    find = classmethod(find)
    
    def perform_action(self, action, method='GET', **params):
        status, xml = self.__class__._make_request(self, method, params, action=action, skip_param_build=True)
        if not str(status[0]).startswith('2'):
            raise ActiveResourceException('%s: %s' % (status, xml))
            
        if '<' in xml:
            return self.__class__._parse_xml(xml)
        else:
            return True
    
    def save(self):
        if getattr(self, 'id', None):
            method = 'PUT'
        else:
            method = 'POST'
        
        dict([(k, getattr(self, k)) for k in self.Meta.changed])
        status, xml = self.__class__._make_request(obj=self, method=method)
        
        if not str(status[0]).startswith('2'):
            return False
        
        # Not a blank HEAD response
        if '<' in xml:
            e = ElementTree.fromstring(xml)
            attrs = self.__class__._extract_attrs(e)
            self._update(**attrs)
        
        return True
        
    def _get_path(self, action=None):
        if getattr(self, 'id', None):
            obj_path = '%s/%s' % (self.Meta.path_root, self.id)
            if action:
                obj_path = '%s/%s' % (obj_path, action)
            return '%s.xml' % (obj_path)
        else:
            return self.Meta.base_path
                
    def _extract_attrs(cls, el):
        attrs = {'_record_exists':True}
        for attr in el.getchildren():
            value = attr.text
            t = dict(attr.items()).get('type')
            if t and t == 'integer':
                value = int(value)
            attrs[attr.tag.replace('-', '_')] = value
        return attrs
    _extract_attrs = classmethod(_extract_attrs)
        
    def _parse_xml(cls, el):
        if isinstance(el, basestring):
            el = ElementTree.fromstring(el)

        is_list = len(set([e.tag for e in el.getchildren()])) == 1

        if el.attrib.get('type') == 'array' or is_list:
            obj = [cls._parse_xml(e) for e in el.getchildren()]
        elif el.getchildren():
            if el.tag == cls.Meta.name:
                obj = cls()
            else:
                obj = Object()
            [setattr(obj, e.tag.replace('-', '_'), cls._parse_xml(e)) for e in el.getchildren()]
            
            if isinstance(obj, cls):
                obj.Meta.changed = []
                
        elif el.text:
            obj = el.text
            if el.attrib.get('type') == 'integer':
                val = int(obj)
        elif el.attrib.get('nil') == 'true':
            obj = None
        return obj
    _parse_xml = classmethod(_parse_xml)
    
    def _make_request(cls, obj=None, method='GET', params={}, headers={}, action=None, skip_param_build=False):
        if cls.Meta.auth and not headers.has_key('Authorization'):
            headers['Authorization'] = cls.Meta.auth
            
        headers["Content-type"] = "application/x-www-form-urlencoded"
        
        if method != 'GET' and not skip_param_build:
            np = {}
            for key, val in params.iteritems():
                k = '%s[%s]' % (cls.Meta.name, key)
                np[k] = val
            params = np
        params = urllib.urlencode(params)
        
        if obj:
            path = obj._get_path(action)
        else:
            path = cls.Meta.base_path
            
        if method == 'GET':
            path += '?%s' % params
            
        conn = cls.Meta.conntype(cls.Meta.host)
        conn.request(method, path, params, headers)
        r = conn.getresponse()
        
        return (r.status, r.reason), r.read()
    _make_request = classmethod(_make_request)
    
    def _update(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.iteritems()]
        [self.Meta.changed.remove(k) for k in kwargs.keys()]
