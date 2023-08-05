# License: PSF
# see: LICENSE
# for full text of the license
# 
# OO oriented Sugar Interface
# above the pysugar transport interface
#
# Original Idea: Florent Aide, <florent.aide@gmail.com>
# Design: Christophe de Vienne, <cdevienne@alphacent.com>
# Co-design : Florent Aide, <florent.aide@gmail.com>

import types
import datetime
from pysugar import SugarDataError, SugarOperationnalError

class SugarModuleCollection:
    def __init__(self, backend):
        self.backend = backend
        self.modules = {}

    def add(self, module_name, module_class):
        self.modules[module_name] = SugarModule(
                self, module_name, module_class)
        setattr(self, module_name, self.modules[module_name])

class SugarModule(object):
    def __init__(self, collection, name, object_class):
        self.collection = collection
        self.name = name
        self.object_class = object_class
        self.elements = {}
        self.new_elements = []

    def add(self):
        o = self.object_class(self)
        self.new_elements.append( o )
        return o

    def get(self, id):
        if not id in self.elements.keys():
            e = self.object_class(self, id)
            self.elements[id] = e
        else:
            e = self.elements[id]
        return e

class SugarObject(object):
    def __init__(self, module, id = None):
        self.__id = id
        self.module = module

    def get_id(self):
        return self.__id

    def isnew(self):
        return self.__id is None

    def post(self):
        post_dict = {}
        if self.__id is not None:
            post_dict['id'] = self.__id

        for prop in self.sugar_properties:
            if prop._get_modified(self):
                post_dict[prop.name] = prop._to_sugar_value(
                        prop._get_raw_value(self))
                
        new_id = self.module.collection.backend.set_entry(
                self.module.name,
                post_dict
                ) 

        if self.__id is None:
            self.__id = new_id
            self.module.new_elements.pop(
                    self.module.new_elements.index(self))
            self.module.elements[new_id] = self
            self.invalidate()
        else:
            if self.__id != new_id:
                raise SugarOperationnalError(
                        'Posted object %s and received a new id: %s' % (
                                self.__id, new_id))

    def load(self):
        d = self.module.collection.backend.get_entry(
                self.module.name, self.id, '')

        for prop in self.sugar_properties:
            # respect flags for the property
            if not prop.send_only:
                prop._load_value(self, d[prop.field_name])

    def invalidate(self):
        for prop in self.sugar_properties:
            prop._cleanup(self)
        
    id = property(fget = get_id)
    
class SugarField(object):
    def __init__(self, name, field_name, module=None, read_only=False,
            receive_only=False, send_only=False, mandatory=True):
        self.name = name
        self.field_name = field_name
        self.module = module
        self.read_only = read_only
        self.receive_only = receive_only
        self.send_only = send_only
        self.mandatory = mandatory

        self.value_attr = '__sp_v_%s' % self.name
        self.modified_attr = '__sp_m_%s' % self.name

    def is_loaded(self, sugar_o):
        return hasattr(sugar_o, self.value_attr)

    def _get_raw_value(self, sugar_o):
        return getattr(sugar_o, self.value_attr)

    def __set_raw_value(self, sugar_o, value):
        setattr(sugar_o, self.value_attr, value)

    def _get_modified(self, sugar_o):
        return self.is_loaded(sugar_o) and \
            getattr(sugar_o, self.modified_attr)

    def __set_modified(self, sugar_o, value):
        setattr(sugar_o, self.modified_attr, value)

    def _cleanup(self, sugar_o):
        if hasattr(sugar_o, self.value_attr):
            delattr(sugar_o, self.value_attr)
        if hasattr(sugar_o, self.modified_attr):
            delattr(sugar_o, self.modified_attr)

    def _from_sugar_value(self, value):
        return value
    
    def _to_sugar_value(self, value):
        return value

    def _load_value(self, sugar_o, value):
        self.__set_raw_value(
                sugar_o, self._from_sugar_value(value))
        self.__set_modified(sugar_o, False)

    def _set_value(self, sugar_o, value):
        if not sugar_o.isnew() and \
                not self.is_loaded(sugar_o):
            sugar_o.load()
        self.__set_raw_value(sugar_o, value)
        self.__set_modified(sugar_o, True)

    def _get_value(self, sugar_o):
        if not sugar_o.isnew() \
                and not hasattr(sugar_o, self.value_attr):
            sugar_o.load()

        return self._get_raw_value(sugar_o)

class SugarSimpleField(SugarField):
    get_value = SugarField._get_value
    set_value = SugarField._set_value

class SugarRelationField(SugarField):
    def get_value(self, sugar_o):
        id = self._get_value(sugar_o)
        return sugar_o.module.collection.modules[
                self.module].get(id)

    def set_value(self, sugar_o, value):
        self._set_value(sugar_o, value.id)

class SugarDatetimeField(SugarField):
    '''
    sugar datetimes are represented as '2006-10-17 12:33:25'
    '''
    get_value = SugarField._get_value
    set_value = SugarField._set_value

    def _from_sugar_value(self, value):
        if not isinstance(value, types.StringType):
            raise ValueError('value should be a string')

        # TODO we should link this datetime object creation
        # with the TimeZone info from the server so we could
        # generate datetime objects with timezone set which would
        # prove really more accurate on many cases :)
        (my_date, my_time) = value.split(' ')
        (year, month, day) = my_date.split('-')
        (hour, minute, second) = my_time.split(':')
        return datetime.datetime(
                int(year), int(month), int(day),
                int(hour), int(minute), int(second))

    def _to_sugar_value(self, value):
        if not isinstance(value, datetime.datetime):
            raise ValueError('value should be a datetime.datetime')

        return value.isoformat(' ')

class SugarDateField(SugarField):
    '''
    sugar dates are stored as '2006-10-17'
    '''
    get_value = SugarField._get_value
    set_value = SugarField._set_value

    def _from_sugar_value(self, value):
        if not isinstance(value, types.StringType):
            raise ValueError('value should be a string')

        (year, month, day) = value.split('-')
        return datetime.date(int(year), int(month), int(day))

    def _to_sugar_value(self, value):
        if not isinstance(value, datetime.date):
            raise ValueError('value should be a datetime.date')

        return value.isoformat()

class SugarTimeField(SugarField):
    '''
    sugar times are stored as '12:33:25'
    '''
    get_value = SugarField._get_value
    set_value = SugarField._set_value

    def _from_sugar_value(self, value):
        if not isinstance(value, types.StringType):
            raise ValueError('value should be a string')

        (hour, minute, second) = value.split(':')
        return datetime.time(int(hour), int(minute), int(second))

    def _to_sugar_value(self, value):
        if not isinstance(value, datetime.time):
            raise ValueError('value should be a datetime.time')

        return value.isoformat()

class SugarIntegerField(SugarField):
    '''
    This field will give an integer instead of the Sugar string
    representation of an integer
    '''
    get_value = SugarField._get_value
    set_value = SugarField._set_value

    def _from_sugar_value(self, value):
        if not isinstance(value, types.StringType):
            raise ValueError('value should be a string')

        return int(value)

    def _to_sugar_value(self, value):
        if not isinstance(value, types.IntType):
            raise ValueError('value should be an integer')

        return str(int)

class SugarBooleanField(SugarField):
    '''
    when sugar stores '0/1
    we will manipulate Booleans
    '''
    get_value = SugarField._get_value
    set_value = SugarField._set_value

    def _from_sugar_value(self, value):
        if not isinstance(value, types.StringType):
            raise ValueError('value should be a string')

        v = int(value)
        if v > 0:
            return True
        else:
            return False

    def _to_sugar_value(self, value):
        if not isinstance(value, types.BooleanType):
            raise ValueError('value should be a boolean')

        if value is True:
            return '1'
        else:
            return '0'

class SugarPropertyGetter:
    def __init__(self, sugar_field):
        self.sugar_field = sugar_field

    def __call__(self, sugar_o):
        return self.sugar_field.get_value(sugar_o)

class SugarPropertySetter:
    def __init__(self, sugar_field):
        self.sugar_field = sugar_field

    def __call__(self, sugar_o, value):
        self.sugar_field.set_value(sugar_o, value)


def create_property(sugar_field):
    return property(
            fget = SugarPropertyGetter(sugar_field),
            fset = SugarPropertySetter(sugar_field));

def init_SugarObject(sugar_object_class, fields):
    sugar_object_class.sugar_properties = []
    for f, p in fields:
        sugar_object_class.sugar_properties.append(f)
        setattr(sugar_object_class, f.name, p)

def sugar_field(name, read_only=False, receive_only=False,
        send_only=False, mandatory=True):

    field = SugarSimpleField( name, name,
            read_only=read_only,
            receive_only=receive_only, send_only=send_only,
            mandatory=mandatory,
            )

    return (field, create_property(field))

# TODO: These definitions should be specific instead of just being
# mappings to the same sugar_field
#sugar_date_field = sugar_field
#sugar_time_field = sugar_field
#sugar_datetime_field = sugar_field
sugar_str_field = sugar_field
#sugar_integer_field = sugar_field
#sugar_bool_field = sugar_field

def sugar_relation_field(property_name, field_name, module,
        read_only=False, receive_only=False,
        send_only=False, mandatory=True):

    field = SugarRelationField(property_name, field_name,
            module=module, read_only=read_only,
            receive_only=receive_only, send_only=send_only,
            mandatory=mandatory,
            )

    return (field, create_property(field))

def sugar_datetime_field(name, read_only=False, receive_only=False,
        send_only=False, mandatory=True):

    field = SugarDatetimeField( name, name,
            read_only=read_only,
            receive_only=receive_only, send_only=send_only,
            mandatory=mandatory,
            )

    return (field, create_property(field))

def sugar_date_field(name, read_only=False, receive_only=False,
        send_only=False, mandatory=True):

    field = SugarDateField( name, name,
            read_only=read_only,
            receive_only=receive_only, send_only=send_only,
            mandatory=mandatory,
            )

    return (field, create_property(field))

def sugar_time_field(name, read_only=False, receive_only=False,
        send_only=False, mandatory=True):

    field = SugarTimeField( name, name,
            read_only=read_only,
            receive_only=receive_only, send_only=send_only,
            mandatory=mandatory,
            )

    return (field, create_property(field))

def sugar_integer_field(name, read_only=False, receive_only=False,
        send_only=False, mandatory=True):

    field = SugarIntegerField( name, name,
            read_only=read_only,
            receive_only=receive_only, send_only=send_only,
            mandatory=mandatory,
            )

    return (field, create_property(field))

def sugar_bool_field(name, read_only=False, receive_only=False,
        send_only=False, mandatory=True):

    field = SugarBooleanField( name, name,
            read_only=read_only,
            receive_only=receive_only, send_only=send_only,
            mandatory=mandatory,
            )

    return (field, create_property(field))

# vim: expandtab tabstop=4 shiftwidth=4:
