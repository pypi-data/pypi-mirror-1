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

from datetime import datetime
from dateutil.parser import parse as dateutil_parse
from xml.etree import ElementTree
import os, sys

def setup_module(module):
    sys.path.append(os.path.abspath(os.path.dirname(sys.modules[__name__].__file__)+'/'+os.path.pardir))
    import xmlobjects
    module.xmlobjects = xmlobjects
    
def test_create_root():
    xobj = xmlobjects.XMLObject(name='test_name')
    xobj.sub = 'asdf'
    assert xmlobjects.tostring(xobj) == '<test_name><sub>asdf</sub></test_name>'

def test_create_all_types():
    xobj = xmlobjects.XMLObject(name='test_name')
    xobj.sub = 'asdf'
    xobj.sub2 = 4
    xobj.sub3 = 4.5
    xobj.sub4 = datetime(1994, 12, 24, 12, 12, 4)
    xobj.sub5 = None
    assert xmlobjects.tostring(xobj) == '<test_name><sub>asdf</sub><sub2>4</sub2><sub3>4.5</sub3><sub4>1994-12-24T12:12:04</sub4><sub5 /></test_name>'

def test_create_attributes():
    xobj = xmlobjects.XMLObject(name='test_name')
    xobj.sub = 'asdf'
    xobj['test-attribute'] = 'testing'
    xobj.sub['test-attribute'] = 'testing sub'
    assert xmlobjects.tostring(xobj) == '<test_name test-attribute="testing"><sub test-attribute="testing sub">asdf</sub></test_name>'
    
def test_namespace_inheritance():
    xobj = xmlobjects.XMLObject(name='test_name', namespace='http://example.com/xml')
    xobj.sub = 5
    assert xmlobjects.tostring(xobj) == '<ns0:test_name xmlns:ns0="http://example.com/xml"><ns0:sub>5</ns0:sub></ns0:test_name>'
    xobj._member_inherit_namespace_ = False
    xobj.sub2 = 'asdf'
    assert xmlobjects.tostring(xobj) == '<ns0:test_name xmlns:ns0="http://example.com/xml"><ns0:sub>5</ns0:sub><sub2>asdf</sub2></ns0:test_name>'
    xobj.sub = 'test'
    assert xmlobjects.tostring(xobj) == '<ns0:test_name xmlns:ns0="http://example.com/xml"><ns0:sub>test</ns0:sub><sub2>asdf</sub2></ns0:test_name>'
    
def test_attribute_inheritance():
    xobj = xmlobjects.XMLObject(name='test_name')
    xobj['type'] = 'text'
    xobj._member_inherit_attributes_ = True
    xobj.sub = 'test'
    xobj.sub1 = None
    assert xmlobjects.tostring(xobj) ==  '<test_name type="text"><sub type="text">test</sub><sub1 type="text" /></test_name>'
    
def test_list_creation():
    xobj = xmlobjects.XMLObject(name='list_test_name')
    xobj.sub = 'test'
    assert xmlobjects.tostring(xobj) == '<list_test_name><sub>test</sub></list_test_name>'
    
    xobj.sub2 = []
    assert xmlobjects.tostring(xobj) == '<list_test_name><sub>test</sub></list_test_name>'
    
    xobj.sub = []
    assert len(xobj.sub) is 1
    assert xmlobjects.tostring(xobj) == '<list_test_name><sub>test</sub></list_test_name>'
    
    xobj.sub2.append(1)
    assert xmlobjects.tostring(xobj) == '<list_test_name><sub>test</sub><sub2>1</sub2></list_test_name>'
    
    test_dt = datetime.now()
    xobj.sub2.append(test_dt)
    assert xmlobjects.tostring(xobj) == '<list_test_name><sub>test</sub><sub2>1</sub2><sub2>%s</sub2></list_test_name>' % test_dt.isoformat()
    
    xobj.sub2.append('asdf')
    assert xmlobjects.tostring(xobj) == '<list_test_name><sub>test</sub><sub2>1</sub2><sub2>%s</sub2><sub2>asdf</sub2></list_test_name>' % test_dt.isoformat()
    
    xobj.sub2.append(1.6)
    assert xmlobjects.tostring(xobj) == '<list_test_name><sub>test</sub><sub2>1</sub2><sub2>%s</sub2><sub2>asdf</sub2><sub2>1.6</sub2></list_test_name>' % test_dt.isoformat()
    
    xobj.sub2.append(None)
    assert xmlobjects.tostring(xobj) == '<list_test_name><sub>test</sub><sub2>1</sub2><sub2>%s</sub2><sub2>asdf</sub2><sub2>1.6</sub2><sub2 /></list_test_name>' % test_dt.isoformat()
    
    xobj.sub2[3]['new_attribute'] = 'asdfasdfasdf'
    assert xmlobjects.tostring(xobj) == '<list_test_name><sub>test</sub><sub2>1</sub2><sub2>%s</sub2><sub2>asdf</sub2><sub2 new_attribute="asdfasdfasdf">1.6</sub2><sub2 /></list_test_name>' % test_dt.isoformat()
    
def test_xmlobject_subelement():
    xobj = xmlobjects.XMLObject(name='xmlobject_name')
    xobj.test_sub = xmlobjects.XMLObject()
    xobj.test_sub.int_test = 1
    assert xmlobjects.tostring(xobj) == '<xmlobject_name><test_sub><int_test>1</int_test></test_sub></xmlobject_name>'
    
    xobj.test_sub.float_test = 1.2
    assert xmlobjects.tostring(xobj) == '<xmlobject_name><test_sub><int_test>1</int_test><float_test>1.2</float_test></test_sub></xmlobject_name>'
    
    xobj.test_sub.str_test = 'asdfasdfasdfsadf'
    assert xmlobjects.tostring(xobj) == '<xmlobject_name><test_sub><int_test>1</int_test><float_test>1.2</float_test><str_test>asdfasdfasdfsadf</str_test></test_sub></xmlobject_name>'
    
    xobj.test_sub.none_test = None
    assert xmlobjects.tostring(xobj) == '<xmlobject_name><test_sub><int_test>1</int_test><float_test>1.2</float_test><str_test>asdfasdfasdfsadf</str_test><none_test /></test_sub></xmlobject_name>'
    
    test_dt = datetime.now()
    xobj.test_sub.dt_test = test_dt
    assert xmlobjects.tostring(xobj) == '<xmlobject_name><test_sub><int_test>1</int_test><float_test>1.2</float_test><str_test>asdfasdfasdfsadf</str_test><none_test /><dt_test>%s</dt_test></test_sub></xmlobject_name>' % test_dt.isoformat()
    
    xobj.test_sub['test_attribute'] = 'a nice little test'
    assert xmlobjects.tostring(xobj) == '<xmlobject_name><test_sub test_attribute="a nice little test"><int_test>1</int_test><float_test>1.2</float_test><str_test>asdfasdfasdfsadf</str_test><none_test /><dt_test>%s</dt_test></test_sub></xmlobject_name>' % test_dt.isoformat()
    
    
def test_building_eimml():
    example = """<?xml version='1.0' encoding='UTF-8'?>
<eim:collection xmlns:eim="http://osafoundation.org/eim"
                uuid="f230dcd4-7c32-4c3f-908b-d92081cc9a89"
                name="Cosmo">
  <eim:recordset uuid="e55b5f1c-a20d-4d47-acda-c43049967281">
    <item:record xmlns:item="http://osafoundation.org/eim/item">
      <item:uuid eim:type="text" eim:key="true">e55b5f1c-a20d-4d47-acda-c43049967281</item:uuid>
      <item:title eim:type="text">Welcome to Cosmo!</item:title>
      <item:triageStatus eim:type="text" />
      <item:triageStatusChanged eim:type="decimal" />
      <item:lastModifiedBy eim:type="text" />
      <item:createdOn eim:type="timestamp">2006-12-19T11:09:44Z</item:createdOn>
    </item:record>
    <note:record xmlns:note="http://osafoundation.org/eim/note">
      <note:uuid eim:type="text" eim:key="true">e55b5f1c-a20d-4d47-acda-c43049967281</note:uuid>
      <note:body eim:type="clob">Welcome to Cosmo!</note:body>
      <note:icalUid eim:type="text">bc54d532-ad87-4c47-b37c-44d23e4f8850</note:icalUid>
    </note:record>
    <event:record xmlns:event="http://osafoundation.org/eim/event">
      <event:uuid eim:type="text" eim:key="true">e55b5f1c-a20d-4d47-acda-c43049967281</event:uuid>
      <event:dtstart eim:type="text">20061220T090000</event:dtstart>
      <event:dtend eim:type="text">20061220T100000</event:dtend>
      <event:location eim:type="text" />
      <event:rrule eim:type="text" />
      <event:exrule eim:type="text" />
      <event:rdate eim:type="text" />
      <event:exdate eim:type="text" />
      <event:recurrenceId eim:type="text" />
      <event:status eim:type="text" />
    </event:record>
  </eim:recordset>
</eim:collection>""" # From the eimml spec, modified to remove CDATA

    eimmlobj = xmlobjects.XMLObject(name='collection', namespace='http://osafoundation.org/eim')
    eimmlobj['uuid'] = "f230dcd4-7c32-4c3f-908b-d92081cc9a89"
    eimmlobj['name'] = 'Cosmo'
    eimmlobj.recordset = xmlobjects.XMLObject()
    eimmlobj.recordset['uuid'] = "e55b5f1c-a20d-4d47-acda-c43049967281"
    eimmlobj.recordset.record = xmlobjects.XMLObject()
    xmlobjects.set_namespace(eimmlobj.recordset.record, 'http://osafoundation.org/eim/item')
    eimmlobj.recordset.record.uuid = 'e55b5f1c-a20d-4d47-acda-c43049967281'
    eimmlobj.recordset.record.uuid['{http://osafoundation.org/eim}type'] = 'text'
    eimmlobj.recordset.record.uuid['{http://osafoundation.org/eim}key'] = 'true'
    eimmlobj.recordset.record.title = 'Welcome to Cosmo!'
    eimmlobj.recordset.record.title['{http://osafoundation.org/eim}type'] = 'text'
    eimmlobj.recordset.record.triageStatus = None
    eimmlobj.recordset.record.triageStatus['{http://osafoundation.org/eim}type'] = 'text'
    eimmlobj.recordset.record.triageStatusChanged = None
    eimmlobj.recordset.record.triageStatusChanged['{http://osafoundation.org/eim}type'] = 'decimal'
    eimmlobj.recordset.record.lastModifiedBy = None
    eimmlobj.recordset.record.lastModifiedBy['{http://osafoundation.org/eim}type'] = 'text'
    eimmlobj.recordset.record.createdOn = '2006-12-19T11:09:44Z'
    eimmlobj.recordset.record.createdOn['{http://osafoundation.org/eim}type'] = 'timestamp'
    eimmlobj.recordset.record = []
    eimmlobj.recordset.record.append(xmlobjects.XMLObject())
    xmlobjects.set_namespace(eimmlobj.recordset.record[1], "http://osafoundation.org/eim/note")
    eimmlobj.recordset.record[1].uuid = 'e55b5f1c-a20d-4d47-acda-c43049967281'
    eimmlobj.recordset.record[1].uuid['{http://osafoundation.org/eim}type'] = 'text'
    eimmlobj.recordset.record[1].uuid['{http://osafoundation.org/eim}key'] = 'true'
    eimmlobj.recordset.record[1].body = 'Welcome to Cosmo!'
    eimmlobj.recordset.record[1].body['{http://osafoundation.org/eim}type'] = 'clob'
    eimmlobj.recordset.record[1].icalUid = 'bc54d532-ad87-4c47-b37c-44d23e4f8850'
    eimmlobj.recordset.record[1].icalUid['{http://osafoundation.org/eim}type'] = 'text'
    eimmlobj.recordset.record.append(xmlobjects.XMLObject())
    xmlobjects.set_namespace(eimmlobj.recordset.record[2], "http://osafoundation.org/eim/event")
    eimmlobj.recordset.record[2].uuid = 'e55b5f1c-a20d-4d47-acda-c43049967281'
    eimmlobj.recordset.record[2].uuid['{http://osafoundation.org/eim}type'] = 'text'
    eimmlobj.recordset.record[2].uuid['{http://osafoundation.org/eim}key'] = 'true'
    eimmlobj.recordset.record[2].dtstart = '20061220T090000'
    eimmlobj.recordset.record[2].dtstart['{http://osafoundation.org/eim}type'] = 'text'
    eimmlobj.recordset.record[2].dtend = '20061220T100000'
    eimmlobj.recordset.record[2].dtend['{http://osafoundation.org/eim}type'] = 'text'
    for i in ['location', 'rrule', 'exrule', 'rdate', 'exdate', 'recurrenceId', 'status']:
        setattr(eimmlobj.recordset.record[2], i, None)
        getattr(eimmlobj.recordset.record[2], i)['{http://osafoundation.org/eim}type'] = 'text'
    example_etree = ElementTree.fromstring(example)
    assert ElementTree.tostring(example_etree).replace('\n      ', '').replace('\n    ', '').replace('\n  ', '').replace('\n', '') == xmlobjects.tostring(eimmlobj)
 

def test_parser():

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
                return str(value)
            except:
                pass
        try:
            return int(value)
        except:
            return str(value)
            
    xmlobjects.Parser.fallback = fallback
    parser = xmlobjects.Parser()
    
    example = """<?xml version='1.0' encoding='UTF-8'?>
<eim:collection xmlns:eim="http://osafoundation.org/eim"
                uuid="f230dcd4-7c32-4c3f-908b-d92081cc9a89"
                name="Cosmo">
  <eim:recordset uuid="e55b5f1c-a20d-4d47-acda-c43049967281">
    <item:record xmlns:item="http://osafoundation.org/eim/item">
      <item:uuid eim:type="text" eim:key="true">e55b5f1c-a20d-4d47-acda-c43049967281</item:uuid>
      <item:title eim:type="text">Welcome to Cosmo!</item:title>
      <item:triageStatus eim:type="text" />
      <item:triageStatusChanged eim:type="decimal" />
      <item:lastModifiedBy eim:type="text" />
      <item:createdOn eim:type="timestamp">2006-12-19T11:09:44Z</item:createdOn>
    </item:record>
    <note:record xmlns:note="http://osafoundation.org/eim/note">
      <note:uuid eim:type="text" eim:key="true">e55b5f1c-a20d-4d47-acda-c43049967281</note:uuid>
      <note:body eim:type="clob">Welcome to Cosmo!</note:body>
      <note:icalUid eim:type="text">bc54d532-ad87-4c47-b37c-44d23e4f8850</note:icalUid>
    </note:record>
    <event:record xmlns:event="http://osafoundation.org/eim/event">
      <event:uuid eim:type="text" eim:key="true">e55b5f1c-a20d-4d47-acda-c43049967281</event:uuid>
      <event:dtstart eim:type="text">20061220T090000</event:dtstart>
      <event:dtend eim:type="text">20061220T100000</event:dtend>
      <event:location eim:type="text" />
      <event:rrule eim:type="text" />
      <event:exrule eim:type="text" />
      <event:rdate eim:type="text" />
      <event:exdate eim:type="text" />
      <event:recurrenceId eim:type="text" />
      <event:status eim:type="text" />
    </event:record>
  </eim:recordset>
</eim:collection>"""
    
    xobj = xmlobjects.fromstring(example)
    tree = ElementTree.fromstring(example)
    assert ElementTree.tostring(tree).replace('\n      ', '').replace('\n    ', '').replace('\n  ', '').replace('\n', '').replace('\n    ', '') == xmlobjects.tostring(xobj)
    
    

    
    
    