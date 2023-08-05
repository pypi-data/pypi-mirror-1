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

##############################
## You can't use list types for assignment of a new tree of elements because you need a different list type to handle semantics for multiple elements of the same name
## Instead just create a new XMLObject()
##############################

import copy
from xml.etree import cElementTree as ElementTree
from dateutil.parser import parse as dateutil_parse
from datetime import datetime


def get_namespace_and_name(tag):
    "Find namespace and tag in element.tag"
    if tag.find('{') is not -1:
        split_vals = tag.split('}')
        tag = split_vals[-1]
        namespace = split_vals[0].replace('{', '', 1)
    else:
        tag = tag
        namespace = None
    
    return namespace, tag

def make_tag(tag, ns=None):
    if ns is None:
        return tag
    else:
        return '{'+ns+'}'+tag

from elements_lib import element_type, element_str, element_list, element_int, element_float, element_datetime
from elements_lib import xobject_str, xobject_int, xobject_datetime, xobject_float, xobject_none, xobject_list
import elements_lib
    
class XMLObject(object):
    
    _conversions_ = elements_lib.conversion_chart
    _text_value_conversions_ = elements_lib.text_value_conversions
    _name_ = 'root'
    _namespace_ = None
    _member_inherit_namespace_ = True
    _member_inherit_attributes_ = False
    
    def __init__(self, name=_name_, namespace=_namespace_, attributes=None, etree=None, parent_etree=None):
        """Initialization, handles creation of etree object if none exists"""
        if name.find('}') is not -1:
            namespace, name = get_namespace_and_name(name)
        
        if etree is not None:
            object.__setattr__(self, '_etree_', etree)
        elif parent_etree is not None:
            object.__setattr__(self, '_etree_', ElementTree.SubElement(parent_etree, make_tag(name, namespace)))
        else:
            object.__setattr__(self, '_etree_', ElementTree.Element(make_tag(name, namespace)))
        
        if attributes is not None:
            getattr(self, '_etree_').attrib = copy.copy(attributes)
        
        object.__setattr__(self, '_name_', name)
        object.__setattr__(self, '_namespace_',  namespace)
        
    def _set_namespace_(self, namespace):
        object.__setattr__(self, '_namespace_', namespace)
        self._etree_.tag = make_tag(self._name_, self._namespace_)
    
    def _set_tag_(self, tag):
        object.__setattr__(self, '_name_', tag)
        self._etree_.tag = make_tag(self._name_, self._namespace_)
        
    def _create_new_member_(self, key, value, attributes=None):
        # Create new member and handle adding xml sub elements
        if value.__class__.__name__ in self._text_value_conversions_:
            if self._member_inherit_namespace_ is True and self._namespace_ is not None:
                element = ElementTree.SubElement(self._etree_, '{'+self._namespace_+'}'+key)
            else:
                element = ElementTree.SubElement(self._etree_, key)
            
            if self._member_inherit_attributes_ is True and len(self._etree_.items()) is not 0:
                element.attrib = copy.copy(self._etree_.attrib)
            
            if attributes is not None:
                element.attrib.update(attributes)
        
            # if type(value) is list:
            #     new_member = self._add_xobject_member_(key, XMLObject())
            #     for item in value:
            #         new_member.setattr()
        
        
            element.text = self._text_value_conversions_[value.__class__.__name__](value)
            object.__setattr__(self, key, self._conversions_[value.__class__.__name__](element))
            
        elif type(value) is list:
            object.__setattr__(self, key, xobject_list(self._etree_, key))
        elif type(value) is XMLObject:
            if self._member_inherit_namespace_ is True and self._namespace_ is not None:
                namespace = self._namespace_
            else:
                namespace = None
            
            inherit_attributes = None    
                
            if self._member_inherit_attributes_ is True and len(self._etree_.attrib) is not 0:
                inherit_attributes = copy.copy(self._etree_.attrib)
            
            if attributes is not None:
                attributes = inherit_attributes.update(attributes)
            elif inherit_attributes:
                attributes = inherit_attributes
                
            object.__setattr__(self, key, XMLObject(name=key, namespace=namespace, attributes=attributes, parent_etree=self._etree_))
        else:
            raise TypeError, "Unsupported object type"
            
        
        
    def __setattr__(self, key, value):
        """Attribute assignment method that handles xml manipulation. Values are assumed to be xml child nodes"""
        if key.startswith('_') is False:
            if hasattr(self, key):
                # if that attribute exists modify the value properly and then create a new xobject type and assign it to he object
                # Note: this doesn't handle the case of when the type is XMLObject yet.
                if value.__class__.__name__ in self._text_value_conversions_:
                    current_value = getattr(self, key)
                    current_value._etree_.text = self._text_value_conversions_[value.__class__.__name__](value)
                    object.__setattr__(self, key, self._conversions_[value.__class__.__name__](current_value._etree_))
                elif type(value) is XMLObject:
                    # If we get another xmlobject and we have one of the same name, remove the current object and start an xmlobject.
                    self._etree_.remove(getattr(self, key)._etree_)
                    self._create_new_member_(key, value)
                elif type(value) is list:
                    current_value = getattr(self, key)
                    self._create_new_member_(key, [])
                    new_element_list = getattr(self, key)
                    list.append(new_element_list, current_value)
                else:
                    raise TypeError, 'Unsupporting object type'    
            else:
                self._create_new_member_(key, value)
        else:
            if key == '_name_':
                self._set_tag_(value)
            elif key == '_namespace_':
                self._set_namespace_(value)
            else:    
                object.__setattr__(self, key, value)
                
    def __delattr__(self, key):
        
        self._etree_.remove(getattr(self, key)._etree_)
        object.__delattr__(self, key)
            
    def __setitem__(self, key, value):
        """Item assignment method that handles xml manipulation. Values are assumed to be xml attributes"""
        self._etree_.attrib.__setitem__(key, self._text_value_conversions_[value.__class__.__name__](value))
        
    def __getitem__(self, key):
        """Item get method that interfaces with etree"""
        return self._etree_.attrib.__getitem__(key)
                

def test():
    f = open('/Users/mikeal/Documents/feed.text')
    atom_feed = f.read()
    atom_tree = ElementTree.fromstring(atom_feed)                
    parser = Parser()
    return parser.parse_etree(atom_tree), atom_tree
                

                
    
    
    
    
    
    