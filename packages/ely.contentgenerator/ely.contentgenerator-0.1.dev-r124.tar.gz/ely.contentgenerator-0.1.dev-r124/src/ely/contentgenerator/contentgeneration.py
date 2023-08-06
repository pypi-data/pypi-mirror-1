from StringIO import StringIO
import re

from lxml import etree
from namespaces import ns

class PloneContentGenerator:

    zopeattribute_re = re.compile(r'{%s}' %(ns['zope']))
    variablesubs_re = re.compile(r'\${(?P<variable>.+?)}')

    def __init__(self, contentstructuredata, root):
        self._root = root
        if not hasattr(contentstructuredata, 'seek'):
            data = StringIO(contentstructuredata)
        else:
            data = contentstructuredata
        self._tree = etree.parse(data)
        # we set up a list of methods to call with the generated node
        self.postprocessnodemethods = []

    def _elementdepth(self, element):
        depth = 0
        parent = element.getparent()
        while parent:
            depth = depth+1
            parent = parent.getparent()
        return depth

    def _filterAttributesByNamespace(self, attributes, namespace):
        filteredattributes =  [x for x in attributes if x.find(
            namespace) >= 0]
        ns = "{%s} %(namespace)"
        cleanedattributes = [x.replace(ns,'') for x in filteredattributes]
        return cleanedattributes

    def _removeNamespaceFromAttribute(self, attribute, namespace):
        ns = "{%s}" %(namespace)
        return attribute.replace(ns,'')

    def _doVariableSubstitutions(self, value):
        def replacement(m):
            return getattr(self, m.group('variable'))
        return self.variablesubs_re.sub(replacement, value)

    def _processAttributeValue(self, value):
         value = self._doVariableSubstitutions(value)
         if value.startswith('python:'):
             exec('attributevalue=' + \
                  value.replace('python:','').strip())
         elif value.startswith('file:'):
             filename =  value.replace('file:','').strip()
             attributevalue = open(filename,'r').read()
         else:
             attributevalue = value
         return attributevalue

    def _prepareAttributeData(self, element, namespaceprefix):
        attributedata = {}
        attributes = self._filterAttributesByNamespace(
            element.attrib, ns[namespaceprefix])
        for attribute in attributes:
            name = self._removeNamespaceFromAttribute(attribute, ns[namespaceprefix])
            value = self._processAttributeValue(element.attrib[attribute])
            attributedata[name] = value
        return attributedata

    def printContentStructure(self):
        for element in self._tree.getiterator():
            indent = " " * (self._elementdepth(element) * 2)
            print indent, element.tag, element.attrib

    def _nodeDefinesPloneContent(self, element):
        if "{%s}portal_type" %(ns['zope']) in element.attrib.keys():
            return True
        else:
            return False

    def generate(self):
        zopeparent = self._root
        treeparent = self._tree.getroot()
        self._generate(zopeparent, treeparent)

    def _generate(self, zopeparent, treeparent):
        for element in treeparent.getchildren():
            csattributedata = self._prepareAttributeData(element,'cs')
            if csattributedata.has_key('repeat'):
                repeatnumber = int(csattributedata['repeat'])
            else:
                repeatnumber = 1
            for index in range(0, repeatnumber):
                zopeattributedata = self._prepareAttributeData(element,'zope')
                if zopeattributedata:
                    attributedata = zopeattributedata.copy()
                    portal_type = attributedata['portal_type']
                    if repeatnumber == 1:
                        object_id = attributedata['id']
                    else:
                        object_id = attributedata['id'] + \
                                    "_" + str(index)
                    del(attributedata['portal_type'])
                    del(attributedata['id'])
                    oid = zopeparent.invokeFactory(portal_type, object_id,
                                                   **attributedata)
                    zopenode = getattr(zopeparent, oid)
                    for method in self.postprocessnodemethods:
                        method(zopenode)
                self._generate(zopenode, element)

