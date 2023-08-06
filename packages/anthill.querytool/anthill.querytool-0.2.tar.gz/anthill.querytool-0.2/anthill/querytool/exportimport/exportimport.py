from zope.component import queryMultiAdapter

from Products.GenericSetup.interfaces import INode
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import PropertyManagerHelpers
from Products.GenericSetup.utils import XMLAdapterBase

from anthill.querytool.QueryTool import Query
from anthill.querytool.QueryTool import IQueryTool

class _extra:
    pass


class QueryToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers,
                         PropertyManagerHelpers):
    """XML im- and exporter for QueryTool
    """

    __used_for__ = IQueryTool

    _LOGGER_ID = 'querytool'

    name = 'querytool'

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractQueries())

        self._logger.info('QueryTool exported.')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeQueries()

        self._initQueries(node)
        self._logger.info('QueryTool imported.')

    def _extractQueries(self):
        fragment = self._doc.createDocumentFragment()
        queries = self.context.getAllPredefinedQueries()
        queries.sort(lambda x,y:cmp(x.getName(), y.getName()))
        for query in queries:
            element = self._doc.createElement('query')
            element.setAttribute('name', query.getName())
            element.setAttribute('catalog', query.getCatalog())
            element.setAttribute('wrapsecurity', query.getWrapSecurity())
            tnode = self._doc.createTextNode(str(query).strip())
            element.appendChild(tnode)
            fragment.appendChild(element)

        return fragment

    def _purgeQueries(self):
        self.context._predefined_queries = {}
        self.context._p_changed = 1

    def _getText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def _initQueries(self, node):
        for child in node.childNodes:
            if child.nodeName != 'query': continue
            queryname = str(child.getAttribute('name'))
            querycatalog = str(child.getAttribute('catalog'))
            querywrap = str(child.getAttribute('wrapsecurity'))
            querytext = str(self._getText(child.childNodes)).strip()

            query = Query(queryname).createFromString(querytext, replacespecial=False)
            query.setCatalog(querycatalog)
            query.setWrapSecurity(eval(querywrap))
            self.context.setPredefinedQuery(queryname, query)

