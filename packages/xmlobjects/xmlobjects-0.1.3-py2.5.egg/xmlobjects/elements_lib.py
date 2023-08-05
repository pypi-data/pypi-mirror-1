#   Copyright (c) 2007 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import copy
from xml.etree import cElementTree as ElementTree
from dateutil.parser import parse as dateutil_parse
from datetime import datetime
from xmlobject import make_tag, get_namespace_and_name

class ElementComparison(object):
    
    def __init__(self, instance, base_type, false_code):
        self.base_type = base_type
        self.false_code = false_code
        self.instance = instance
        
        
    def __call__(self, other):
        if not hasattr(other, '_name_'):
            return self.false_code
        elif self.instance._name_ != other._name_:
            return self.false_code
        
        if not hasattr(other, '_namespace_'):
            return self.false_code
        elif self.instance._namespace_ != other._namespace_:
            return self.false_code
        
        if not hastattr(other, '_etree_'):
            return self.false_code
        elif self.instance._etree_.attrib != other._etree_attrib:
            return self.false_code
            
        if false_code is False:
            if hasattr(base_type, '__eq__'):
                if not base_type.__eq__(self.instance, other):
                    return False
            elif hasattr(base_type, '__cmp__'):
                if not base_type.__cmp__(self.instance, other):
                    return False
            elif hasattr(base_type, '__hash__'):
                if not hasattr(other, '__hash__'):
                    return False
                elif self.instance.__hash__() != other.__hash__():
                    return False
                    
        if false_code is True:
            if hasattr(base_type, '__ne__'):
                if base_type.__ne__(self.instance, other):
                    return True
            elif hasattr(base_type, '__cmp__'):
                if base_type.__cmp__(self.instance, other):
                    return True
            elif hasattr(base_type, '__hash__'):
                if hasattr(other, '__hash__'):
                    return True
                elif self.instance.__hash__() == other.__hash__():
                    return True
                    

class element_type(object):    
    def __getitem__(self, key):
        return self._etree_.attrib.__getitem__(key)
    def __setitem__(self, key, value):
        self._etree_.attrib.__setitem__(key, value)
    def __delitem__(self, key):
        self._etree_.attrib.__delitem__(key)
        
    def has_key(self, key):
        return self._etree_.attrib.has_key(key)
        
    def __setattr__(self, key, value):
        if key == '_namespace_':
            self._set_namespace_(value)
        elif key == '_name_':
            self._set_tag_(value)
        else:
            object.__setattr__(self, key, value)
            
    def _set_namespace_(self, namespace):
        object.__setattr__(self, '_namespace_', namespace)
        self._etree_.tag = make_tag(self._name_, self._namespace_)

    def _set_tag_(self, tag):
        object.__setattr__(self, '_name_', tag)
        self._etree_.tag = make_tag(self._name_, self._namespace_)

class element_str(element_type, unicode):
    """str object that supports __setattr__ and parses string from element"""
    def __init__(self, *args, **kwargs):
        unicode.__init__(self, *args, **kwargs)
        self.__eq__ = ElementComparison(self, unicode, False)
        self.__ne__ = ElementComparison(self, unicode, True)
                
class element_int(element_type, int):
    """int object that supports __setattr__"""
    def __init__(self, *args, **kwargs):
        int.__init__(self, *args, **kwargs)
        self.__eq__ = ElementComparison(self, int, False)
        self.__ne__ = ElementComparison(self, int, True)
            
class element_float(element_type, float):
    """float object that supports __setattr__"""
    def __init__(self, *args, **kwargs):
        float.__init__(self, *args, **kwargs)
        self.__eq__ = ElementComparison(self, float, False)
        self.__ne__ = ElementComparison(self, float, True)
            
class element_datetime(element_type, datetime):
    """datetime object that supports __setattr__"""
    def __init__(self, *args, **kwargs):
        datetime.__init__(self, *args, **kwargs)
        self.__eq__ = ElementComparison(self, datetime, False)
        self.__ne__ = ElementComparison(self, datetime, True)
        
class element_none(element_type):
    """none object that supports __setattr__"""
    def __eq__(self, other):
        if type(other) is not element_none:
            return False
        elif self._etree_.attrib != other._etree_.attrib:
            return False
        return True

    def __ne__(self, other):
        if not self.__eq__(other):
            return True
        else:
            return False

     
# This needs to be rewritten with new semantics for hold multiple element_types and manipulating them
            
class element_list(element_type, list):

    _name_ = 'root'
    _namespace_ = None
    _member_inherit_namespace_ = True
    _member_inherit_attributes_ = False

    def __setitem__(self, key, value):
        if type(key) is int:
            current_element = list.__getitem__(self, key)
            current_element._etree_.text = self._text_value_conversions_[value.__class__.__name__](value)
            list.__setitem__(self, key, self._conversions_[value.__class__.__name__](current_element._etree_))
        else:
            raise IndexError, 'element_list indexes must be type int'
            
    def __delitem__(self, key):
        if type(key) is int:
            current_element = list.__getitem__(self, key)
            self._parent_etree_.remove(current_element)
            list.__delitem__(self, key)
        else:
            raise IndexError, 'element_list indexes must be type int'
            
    __getitem__ = list.__getitem__
            
    def append(self, value, attributes=None):
        from xmlobject import XMLObject
        if value.__class__.__name__ in self._text_value_conversions_:
            if self._member_inherit_namespace_ is True and self._namespace_ is not None:
                element = ElementTree.SubElement(self._parent_etree_, '{'+self._namespace_+'}'+self._name_)
            else:
                element = ElementTree.SubElement(self._parent_etree_, self._name_)
            
            if self._member_inherit_attributes_ is True and len(self._parent_etree_.items()) is not 0:
                element.attrib = copy.copy(self._parent_etree_.attrib)
            
            if attributes is not None:
                element.attrib.update(attributes)        
        
            element.text = self._text_value_conversions_[value.__class__.__name__](value)
            list.append(self, self._conversions_[value.__class__.__name__](element))
            

        elif type(value) is XMLObject:
            if self._member_inherit_namespace_ is True and self._namespace_ is not None:
                namespace = self._namespace_
            else:
                namespace = None
            
            inherit_attributes = None    
                
            if self._member_inherit_attributes_ is True and len(self._parent_etree_.attrib) is not 0:
                inherit_attributes = copy.copy(self._parent_etree_.attrib)
            
            if attributes is not None:
                attributes = inherit_attributes.update(attributes)
            elif inherit_attributes:
                attributes = inherit_attributes
                
            list.append(self, XMLObject(name=self._name_, namespace=namespace, attributes=attributes, parent_etree=self._parent_etree_))
            
    def _comparison_(self, other):
        if other.__class__ is not self.__class__:
            return False
        for index in range(len(other)):
            if self[index] != other[index]:
                return False
            if not self[index] == other[index]:
                return False
        return True
    
    def __eq__(self, other):
        if self._comparison_(other):
            return True
        else:
            return False

    def __ne__(self, other):
        if not self._comparison_(other):
            return True
        else:
            return False    


class ValueManipulator(object):
    """Value manipulation object"""
    def __init__(self, etree):
        self._etree_ = etree
    def setval(self, value):
        self._etree_.text = value
    def getval(self):
        return self._etree_.text
    
        
def datetime_isoformat(value):
    return value.isoformat()        
    
def none_to_empty_string(value):
    return ''    
        
def xobject_str(etree):
    namespace, name = get_namespace_and_name(etree.tag)
    elem = element_str(etree.text)
    elem._etree_ = etree
    object.__setattr__(elem, '_namespace_', namespace)
    object.__setattr__(elem, '_name_', name)
    elem._value_manipulator_ = ValueManipulator(etree)
    return elem

def xobject_int(etree):
    namespace, name = get_namespace_and_name(etree.tag)
    elem = element_int(int(etree.text))
    elem._etree_ = etree
    object.__setattr__(elem, '_namespace_', namespace)
    object.__setattr__(elem, '_name_', name)
    elem._value_manipulator_ = ValueManipulator(etree)
    return elem
    
def xobject_float(etree):
    namespace, name = get_namespace_and_name(etree.tag)
    elem = element_float(etree.text)
    elem._etree_ = etree
    object.__setattr__(elem, '_namespace_', namespace)
    object.__setattr__(elem, '_name_', name)
    elem._value_manipulator_ = ValueManipulator(etree)
    return elem
    
def xobject_datetime(etree):
    namespace, name = get_namespace_and_name(etree.tag)
    dt = dateutil_parse(etree.text)
    elem = element_datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)
    elem._etree_ = etree
    object.__setattr__(elem, '_namespace_', namespace)
    object.__setattr__(elem, '_name_', name)
    elem._value_manipulator_ = ValueManipulator(etree)
    return elem
    
def xobject_none(etree):
    namespace, name = get_namespace_and_name(etree.tag)
    elem = element_none()
    object.__setattr__(elem, '_namespace_', namespace)
    object.__setattr__(elem, '_name_', name)
    elem._etree_ = etree
    elem._value_manipulator_ = ValueManipulator(etree)
    return elem
    
# Element lists differ from previous types as they represent an element with subelements

def xobject_list(parent_etree, name):
    namespace, tag_name = get_namespace_and_name(parent_etree.tag)
    elem = element_list()
    object.__setattr__(elem, '_parent_etree_', parent_etree)
    object.__setattr__(elem, '_namespace_', namespace)
    object.__setattr__(elem, '_name_', name)
    
    if not hasattr(elem, '_conversions_'):
        object.__setattr__(elem, '_conversions_', conversion_chart)
    if not hasattr(elem, '_text_value_conversions_'):
        object.__setattr__(elem, '_text_value_conversions_', text_value_conversions)

    return elem
    
    
text_value_conversions = {'str':str, 'int':str, 'float':str, 'datetime':datetime_isoformat, 'NoneType':none_to_empty_string}

conversion_chart = {'str':xobject_str, 'int':xobject_int, 'float':xobject_float, 'datetime':xobject_datetime, 'NoneType':xobject_none, 'list':xobject_list}    
