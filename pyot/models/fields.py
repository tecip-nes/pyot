'''
Created on Jul 15, 2013

@author: http://djangosnippets.org/snippets/1961/
'''
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import fields, widgets
from ipaddr import _IPAddrBase, IPAddress, IPNetwork


# from django.forms import ValidationError as FormValidationError
class IPNetworkWidget(widgets.TextInput):
    def render(self, name, value, attrs=None):
        if isinstance(value, _IPAddrBase):
            value = u'%s' % value
        return super(IPNetworkWidget, self).render(name, value, attrs)

class IPNetworkManager(models.Manager):
    use_for_related_fields = True

    def __init__(self, qs_class=models.query.QuerySet):
        self.queryset_class = qs_class
        super(IPNetworkManager, self).__init__()

    def get_query_set(self):
        return self.queryset_class(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

class IPNetworkQuerySet(models.query.QuerySet):

    net = None

    def network(self, key, value):
        if not isinstance(value, _IPAddrBase):
            value = IPNetwork(value)
        self.net = (key, value)
        return self

    def iterator(self):
        for obj in super(IPNetworkQuerySet, self).iterator():
            try:
                net = IPNetwork(getattr(obj, self.net[0]))
            except (ValueError, TypeError):
                pass
            else:
                if not self.net[1] in net:
                    continue
            yield obj

    @classmethod
    def as_manager(cls, ManagerClass=IPNetworkManager):
        return ManagerClass(cls)

class IPNetworkField(models.Field):
    __metaclass__ = models.SubfieldBase
    description = "IP Network Field with CIDR support"
    empty_strings_allowed = False

    def db_type(self, connection):
        return 'varchar(45)'

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _IPAddrBase):
            return value

        try:
            return IPNetwork(value.encode('latin-1'))
        except Exception, e:
            raise ValidationError(e)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' \
                % lookup_type)

    def get_prep_value(self, value):
        if isinstance(value, _IPAddrBase):
            value = '%s' % value
        return unicode(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class' : fields.CharField,
            'widget': IPNetworkWidget,
        }
        defaults.update(kwargs)
        return super(IPNetworkField, self).formfield(**defaults)

class IPAddressField(models.Field):
    __metaclass__ = models.SubfieldBase
    description = "IP Address Field with IPv6 support"

    def db_type(self, connection):
        return 'varchar(42)'

    def to_python(self, value):
        if not value:
            return None

        if isinstance(value, _IPAddrBase):
            return value

        try:
            return IPAddress(value.encode('latin-1'))
        except Exception, e:
            raise ValidationError(e)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' \
                % lookup_type)

    def get_prep_value(self, value):
        if isinstance(value, _IPAddrBase):
            value = '%s' % value
        return unicode(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class' : fields.CharField,
            'widget': IPNetworkWidget,
        }
        defaults.update(kwargs)
        return super(IPAddressField, self).formfield(**defaults)
