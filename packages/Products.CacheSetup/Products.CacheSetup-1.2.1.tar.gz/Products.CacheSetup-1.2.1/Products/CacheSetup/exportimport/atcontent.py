from zope.component import queryMultiAdapter
from Products.GenericSetup.interfaces import INode
from Products.GenericSetup import utils as gsutils
from ZPublisher.HTTPRequest import default_encoding

import logging
logger = logging.getLogger('GS adapter')


class ATContentAdapterBase(gsutils.XMLAdapterBase,
                           gsutils.ObjectManagerHelpers):

    _LOGGER_ID = "CacheSetup"
    _encoding = default_encoding
    _fields = None


    def _getObjectNode(self, name, i18n=True):
        """Override NodeAdapterBase._getObjectNode to use portal_type."""
        node = self._doc.createElement(name)
        node.setAttribute("name", self.context.getId())
        node.setAttribute("portal_type", self.context.portal_type)
        i18n_domain = getattr(self.context, "i18n_domain", None)
        if i18n and i18n_domain:
            node.setAttributeNS(gsutils.I18NURI, "i18n:domain", i18n_domain)
            self._i18n_props = ("title", "description")
        return node


    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode("object")
        node.appendChild(self._extractFields())
        node.appendChild(self._extractObjects())
        return node


    def _convertValueToString(self, value):
        if isinstance(value, bool):
            value = unicode(bool(value))
        elif isinstance(value, str):
            value = value.decode(self._encoding)
        elif not isinstance(value, basestring) and value is not None:
            value = unicode(value)
        return value


    def _extractFields(self):
        fragment = self._doc.createDocumentFragment()
        schema = self.context.Schema()
        for fieldname in self._fields:
            field = schema[fieldname]
            accessor = field.getEditAccessor(self.context)
            if accessor is not None:
                value = accessor()
            else:
                value = field.get(self.context)

            node = self._doc.createElement("property")
            node.setAttribute("name", fieldname)

            if isinstance(value, (tuple,list)):
                for v in value:
                    if isinstance(v, str):
                        v = v.decode(self._encoding)
                    child = self._doc.createElement("element")
                    child.setAttribute("value", v)
                    node.appendChild(child)
            else:
                value = self._convertValueToString(value)
                if value is None:
                    continue
                child = self._doc.createTextNode(value)
                node.appendChild(child)

            if fieldname in getattr(self, "_i18n_props", []):
                node.setAttribute("i18n:translate", "")

            fragment.appendChild(node)

        return fragment


    def _purgeFields(self):
        schema = self.context.Schema()
        for fieldname in self._fields:
            field = schema[fieldname]
            field.getMutator(self.context)(field.getDefault(self.context))


    def _initFields(self, node):
        schema = self.context.Schema()

        for child in node.childNodes:
            if child.nodeName != "property":
                continue

            fieldname = str(child.getAttribute("name"))
            if fieldname not in schema.keys():
                continue

            field = schema[fieldname]
            accessor = field.getEditAccessor(self.context)
            if accessor is not None:
                current_value = accessor()
            else:
                current_value = field.get(self.context)

            if isinstance(current_value, (list,tuple)):
                if not self._convertToBoolean(child.getAttribute("purge") or "True"):
                    value = current_value
                else:
                    value = []
                for sub in child.childNodes:
                    if sub.nodeName != "element":
                        continue
                    value.append(sub.getAttribute("value").encode(self._encoding))

                if isinstance(current_value, tuple):
                    value = tuple(value)
            else:
                value = self._getNodeText(child)
                if value == "None":
                    value = None
                elif isinstance(current_value, bool):
                    value = self._convertToBoolean(value)
                elif isinstance(current_value, int):
                    if "Boolean" in field.getType():
                        # Archetypes releases before 1.5.8 had BooleanFields
                        # which could return integers.
                        value = self._convertToBoolean(value)
                    else:
                        value = int(value)

            field.getMutator(self.context)(value)


    def _initObjects(self, node):
        """Import objects. This is a much simpler version of
        ObjectManagerHelpers._init_objects which does not support ordering
        and uses portal_types.
        """

        for child in node.childNodes:
            if child.nodeName != "object":
                continue

            parent = self.context
            obj_id = str(child.getAttribute("name"))
            if child.hasAttribute("remove"):
                if obj_id in parent.objectIds():
                    parent.manage_delObjects([obj_id])
                continue

            if obj_id not in parent.objectIds():
                portal_type = str(child.getAttribute("portal_type"))
                self.context.invokeFactory(portal_type, obj_id)

            obj = getattr(self.context, obj_id)

            importer = queryMultiAdapter((obj, self.environ), INode)
            if importer:
                importer.node = child


    def _importNode(self, node):
        """Import the object from the DOM node.
        """

        if self.environ.shouldPurge():
            self._purgeFields()
            self._purgeObjects()
                    
        self._initObjects(node)
        self._initFields(node)
        self.context.indexObject()

    node = property(_exportNode, _importNode)

