"""
Based on this cry for help:
http://mail.python.org/pipermail/python-list/2006-January/323506.html
This is atrocious XML, but we've all had to deal with a mess of generated
records elements, so let's use pushbind to turn it into a nice dict
"""

XML = """\
<?xml version='1.0' ?>
<Services>
  <Service>
    <Name>name</Name>
    <Label>label</Label>
    <Icon>/opt/OV/www/htdocs/ito_op/images/service.32.gif</Icon>
    <Status>
      <Normal/>
    </Status>
    <Depth>1</Depth>
    <Attribute>
     <Name>Attrib1</Name>
     <Value>Val1</Value>
    </Attribute>
    <Attribute>
     <Name>Attrib1.1</Name>
     <Value>Val1.1</Value>
    </Attribute>
  </Service>
  <Service>
    <Name>name1</Name>
    <Label>label1</Label>
    <Icon>/opt/OV/www/htdocs/ito_op/images/service.32.gif</Icon>
    <Status>
      <Normal/>
    </Status>
    <Depth>1</Depth>
    <Attribute>
     <Name>Attrib2</Name>
     <Value>val 2</Value>
    </Attribute>
  </Service>
  <Service>
    <Name>name2</Name>
    <Label>label2</Label>
    <Icon>/opt/OV/www/htdocs/ito_op/images/service.32.gif</Icon>
    <Status>
      <Normal/>
    </Status>
    <Depth>1</Depth>
  </Service>
</Services>
"""

import amara
services = {}
for service in amara.pushbind(XML, u'Service'):
    service_attribs = {}
    if hasattr(service, 'Attribute'):
        #Using look-before-you-leap.  Could also try/except AttributeError
        #Or even XPath: for attr in service.xml_xpath(u'Attribute'):
        for attr in service.Attribute:
            service_attribs[unicode(attr.Name)] = unicode(attr.Value)
    services[unicode(service.Name)] = service_attribs

print services
