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

from xmlobject import *
from parser import *
from elements_lib import *

def tostring(xmlobject):
    from xml.etree import cElementTree as ElementTree
    return ElementTree.tostring(xmlobject._etree_)
    
def fromstring(xml_string):
    from xml.etree import cElementTree as ElementTree
    parser = Parser()
    return parser.parse_etree(ElementTree.fromstring(xml_string))
    
def set_namespace(xmlobject, namespace):
    """Set the namespace for a given"""
    if issubclass(xmlobject.__class__, element_type) or type(xmlobject) is XMLObject:
        xmlobject._set_namespace_(namespace)
    else:
        raise TypeError, 'Not xmlobjects.element_type'
        
def hasattrib(xmlobject, key):
    if key in xmlobject._etree_.attrib.keys():
        return True
    else:
        return False
    