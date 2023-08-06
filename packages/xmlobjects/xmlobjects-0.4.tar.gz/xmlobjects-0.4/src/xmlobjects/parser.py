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
from xmlobject import *
from elements_lib import *

class Parser(object):
    _xmlobject_class_ = XMLObject
    
    def parse_etree(self, etree):
        """Default etree parser"""
        
        # Add logic to verify tree has only one root
        
        def recursive_child_parser(parent=None, etree=None):
            """Simple recursive function that begins the parsing path for all elements, attributes and values"""
            if parent is None:
                parent = self._xmlobject_class_(etree.tag)
                
                if len(etree.attrib) is not 0:
                    for key, value in etree.attrib.items():
                        parent[key] = value
                        
                for child in etree.getchildren():
                    recursive_child_parser(parent, child)
                
                return parent
            
            if len(etree.getchildren()) is not 0:
                namespace, name = get_namespace_and_name(etree.tag)
                
                if hasattr(parent, name):
                    # Handle multiple children of the same name
                    if type(getattr(parent, name)) is not element_list:
                        setattr(parent, name, [])
                    getattr(parent, name).append(self._xmlobject_class_(name, namespace))
                    # -- Handle namespaces -- #
                    if namespace is not None:
                        getattr(parent, name)[-1]._namespace_ = namespace
                    if namespace is None and parent._member_inherit_namespace_ is True:
                        getattr(parent, name)[-1]._namespace_ = None
                    parent = getattr(parent, name)[-1]
                
                    if len(etree.attrib) is not 0:
                        for key, value in etree.attrib.items():
                            parent[key] = value
                
                else:
                    setattr(parent, name, self._xmlobject_class_(name, namespace))
                    # -- Handle namespaces -- #
                    if namespace is not None:
                        getattr(parent, name)._namespace_ = namespace
                    if namespace is None and parent._member_inherit_namespace_ is True:
                        getattr(parent, name)._namespace_ = None
                    parent = getattr(parent, name)
                    
                    if len(etree.attrib) is not 0:
                        for key, value in etree.attrib.items():
                            parent[key] = value
                
                
                for child in etree.getchildren():
                     recursive_child_parser(parent, child)
                        
                     
            else:
                namespace, name = get_namespace_and_name(etree.tag)
                
                if hasattr(parent, name):
                    # Handle multiple children of the same name
                    if type(getattr(parent, name)) is not element_list:
                        setattr(parent, name, [])
                    getattr(parent, name).append(self.fallback(etree.text))
                    # -- Handle namespaces -- #
                    if namespace is not None:
                        getattr(parent, name)[-1]._namespace_ = namespace
                    if namespace is None and parent._member_inherit_namespace_ is True:
                        getattr(parent, name)[-1]._namespace_ = None

                    if len(etree.attrib) is not 0:
                        for key, value in etree.attrib.items():
                            getattr(parent, name)[-1][key] = value

                    
                else:
                    setattr(parent, name, self.fallback(etree.text))
                    # -- Handle namespaces -- #
                    if namespace is not None:
                        getattr(parent, name)._namespace_ = namespace
                    if namespace is None and parent._member_inherit_namespace_ is True:
                        getattr(parent, name)._namespace_ = None

                    if len(etree.attrib) is not 0:
                        for key, value in etree.attrib.items():
                            getattr(parent, name)[key] = value
                
                    
        xobj = recursive_child_parser(etree=etree, parent=None)
        return xobj
                
            
    def fallback(self, value):
        """Fallback method to return best type converter for a given value"""
        # Cascading logic that tries it's best to return the proper type converter for a given value
        if value is None or value == '':
            return None
        
        if value.find('.') is not -1:
            try:
                return float(value)
            except:
                pass
        if value.find('T') is not -1:
            try:
                return dateutil_parse(value)
            except:
                pass
        try:
            return int(value)
        except:
            return str(value)