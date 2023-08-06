from amara import bindery
from amara.bindery.model import generate_metadata
from amara.bindery.model.examplotron import examplotron_model

DSRL_EG_MODEL_XML = '''\
<?xml version="1.0" encoding="UTF-8"?>
<dsrl:maps xmlns:dsrl="http://purl.oclc.org/dsdl/dsrl">
<!--Mapping of element and attribute names and attribute values-->
<dsrl:element-name-map target="adresse">address</dsrl:element-name-map>
<dsrl:attribute-name-map target="adresse[@sorte]">type</dsrl:attribute-name-map>
<dsrl:attribute-values-map target="adresse[@sorte]">maison home bureau office</dsrl:attribute-values-map>
<dsrl:attribute-name-map target="adresse[@torte]">type2</dsrl:attribute-name-map>
<dsrl:attribute-values-map target="adresse[@torte]">maison home bureau office</dsrl:attribute-values-map>
<dsrl:element-name-map target="numero">building-identifier</dsrl:element-name-map>
<dsrl:element-name-map target="rue">road</dsrl:element-name-map>
<dsrl:element-name-map target="ville">locality</dsrl:element-name-map>
<dsrl:element-name-map target="cité">postal-town</dsrl:element-name-map>
<dsrl:element-name-map target="département">county</dsrl:element-name-map>
<dsrl:element-name-map target="code-postal">postcode</dsrl:element-name-map>
<dsrl:element-name-map target="pays">country</dsrl:element-name-map>
<!--Assigning default values-->
<dsrl:entity-name-map>
 eacute e
 amp et
 amp and
 lt	open-tag
 gt	close-tag
</dsrl:entity-name-map>
<dsrl:map-pi-target target-name="PIname" alternative-names="PInameAsInput AlternativePIname"/> <dsrl:map-pi-target target-name="ProcessThis" alternative-names="MyPI"/> <dsrl:default-content target="cité" parent="adresse"
map-to-element-name="postal-town" force-default="true">Bordeaux</dsrl:default-content>
<dsrl:default-content target="ville" parent="adresse" map-to-element-name="locality">
<dsrl:default-attribute-values force-default="false">required false</dsrl:default-attribute-values> Downtown
</dsrl:default-content>
<dsrl:default-attribute-values target="pays" force-default="true">
 code-system iso3166
</dsrl:default-attribute-values>
</dsrl:maps>
'''

DSRL_EG_MODEL = examplotron_model(DSRL_EG_MODEL_XML)

class smart_entity(bindery.nodes.entity_base):
    def __init__(self, document_uri=None):
        bindery.nodes.entity_base.__init__(self, document_uri)
        return

    def xml_pyname(self, ns, local, parent=None, iselement=True):
        pyname = bindery.nodes.entity_base.xml_pyname(self, ns, local, parent, iselement)
        return self.NAME_MAPPING.get(pyname, pyname)

doc = bindery.parse(XML, entity_factory=smart_entity)

print unicode(doc.spam.someNiceName) # outputs 'this is a test'


