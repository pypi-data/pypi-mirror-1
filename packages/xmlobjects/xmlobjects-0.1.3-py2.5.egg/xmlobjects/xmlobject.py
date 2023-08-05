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
    _member_inherit_members_ = False
    
    def __init__(self, name=_name_, namespace=_namespace_, members=None, etree=None, parent_etree=None, attributes=None):
        """Initialization, handles creation of etree object if none exists"""
        if name.find('}') is not -1:
            namespace, name = get_namespace_and_name(name)
        
        if etree is not None:
            object.__setattr__(self, '_etree_', etree)
        elif parent_etree is not None:
            object.__setattr__(self, '_etree_', ElementTree.SubElement(parent_etree, make_tag(name, namespace)))
        else:
            object.__setattr__(self, '_etree_', ElementTree.Element(make_tag(name, namespace)))
        
        if members is not None:
            getattr(self, '_etree_').attrib = copy.copy(members)
        
        object.__setattr__(self, '_name_', name)
        object.__setattr__(self, '_namespace_',  namespace)
        
        if attributes is not None:
            for key, value in attributes.items():
                self[key] = value
        
    def _set_namespace_(self, namespace):
        object.__setattr__(self, '_namespace_', namespace)
        self._etree_.tag = make_tag(self._name_, self._namespace_)
    
    def _set_tag_(self, tag):
        object.__setattr__(self, '_name_', tag)
        self._etree_.tag = make_tag(self._name_, self._namespace_)
        
    def _create_new_member_(self, key, value, members=None):
        # Create new member and handle adding xml sub elements
        if value.__class__.__name__ in self._text_value_conversions_:
            if self._member_inherit_namespace_ is True and self._namespace_ is not None:
                element = ElementTree.SubElement(self._etree_, '{'+self._namespace_+'}'+key)
            else:
                element = ElementTree.SubElement(self._etree_, key)
            
            if self._member_inherit_members_ is True and len(self._etree_.items()) is not 0:
                element.attrib = copy.copy(self._etree_.attrib)
            
            if members is not None:
                element.attrib.update(members)
        
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
            
            inherit_members = None    
                
            if self._member_inherit_members_ is True and len(self._etree_.attrib) is not 0:
                inherit_members = copy.copy(self._etree_.attrib)
            
            if members is not None:
                members = inherit_members.update(members)
            elif inherit_members:
                members = inherit_members
                
            object.__setattr__(self, key, XMLObject(name=key, namespace=namespace, members=members, parent_etree=self._etree_))
        else:
            raise TypeError, "Unsupported object type"
            
    def __getattr__(self, key):
        """Get attribute by name. Supports '{namespace}key' regardless of attribute type."""
        if key.find('}') is not -1:
            real_key = key.split('}')
            real_key[0] = real_key[0].replace('{', '')
            
            try:
                attribute_by_name = object.__getattribute__(self, real_key[1])
            except KeyError, e:
                raise AttributeError, e
                
            if type(attribute_by_name) is element_list:
                for element in attribute_by_name:
                    if element._namespace_ == real_key[0]:
                        return element
                raise AttributeError, 'no element with namespace %s exists in %s' % (real_key[0], attribute_by_name)
            else:
                if attribute_by_name._namespace_ == real_key[0]:
                    return attribute_by_name
                else:
                    raise AttributeError, '%s does not match namespace %s' % (attribute_by_name, real_key[1])
        else:
            raise AttributeError, 'object does not have attributes %s' % key
            
        
    def __setattr__(self, key, value):
        """Attribute assignment method that handles xml manipulation. Values are assumed to be xml child nodes"""
        if key.startswith('_') is False:
            if hasattr(self, key):
                # if that member exists modify the value properly and then create a new xobject type and assign it to he object
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
        """Item assignment method that handles xml manipulation. Values are assumed to be xml members"""
        self._etree_.attrib.__setitem__(key, self._text_value_conversions_[value.__class__.__name__](value))
        
    def __getitem__(self, key):
        """Item get method that interfaces with etree"""
        return self._etree_.attrib.__getitem__(key)
        
    
    ### Object comparisons ###    
    def _comparison_(self, other):
        """xmlobject comparison method"""
        
        def compare_members(object_one, object_two, member_name):
            """method for comparing a single member on two objects by name"""
            if hasattr(object_one, member_name):
                if not hasattr(object_two, member_name):
                    return False
                elif getattr(object_one, member_name) != getattr(object_two, member_name):
                    return False
                elif not getattr(object_one, member_name) == getattr(object_two, member_name):
                    return False
            return True
        
        # Comparisons for members
        for member in [member for member in dir(self) if not member.startswith('_')]:
            if not compare_members(self, other, member):
                return False
                
                    
            # Attribute comparison for members
            if hasattr(getattr(self, member), '_etree_'):
                if not hasattr(getattr(other, member), '_etree_'):
                    return False
                else:
                    if getattr(self, member)._etree_.attrib != getattr(other, member)._etree_.attrib:
                        return False
            
            # Name comparison for members (this is a corner case since name should always be the member name)
            if not compare_members(getattr(self, member), getattr(other, member), '_name_'):
                return False
            
            # Namespace comparison for members
            if not compare_members(getattr(self, member), getattr(other, member), '_namespace_'):
                return False
            
        # Attribute comparison for root
        if not hasattr(other, '_etree_'):
            return False
        else:
            if self._etree_.attrib != other._etree_.attrib:
                return False
        
        # Name comparison for root
        if not compare_members(self, other, '_name_'):
            return False
        
        # Namespace comparison for root
        if not compare_members(self, other, '_namespace_'):
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
                

def test():
    f = open('/Users/mikeal/Documents/feed.text')
    atom_feed = f.read()
    atom_tree = ElementTree.fromstring(atom_feed)                
    parser = Parser()
    return parser.parse_etree(atom_tree), atom_tree
                

                
    
    
    
    
    
    