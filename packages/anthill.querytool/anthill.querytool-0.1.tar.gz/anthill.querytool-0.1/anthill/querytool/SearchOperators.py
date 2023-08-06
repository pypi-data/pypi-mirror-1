from BTrees.OOBTree import OOBTree, OOTreeSet 
from BTrees.OOBTree import intersection as OOBTreeIntersection

from BTrees.IIBTree import IITreeSet, intersection

from Products.ZCatalog.Lazy import LazyCat, LazyMap
from Interface import Interface

from Products.AdvancedQuery.sorting import _sort, normSortSpecs as _normSortSpecs
from Products.AdvancedQuery.AdvancedQuery import _BaseQuery, _ElementaryQuery

class IIntResult(Interface):
    pass

class Count(_BaseQuery):
    __implements__ = (IIntResult,)
    def __init__(self, query):
        self._query = query
        
    def _eval(self,context):
        result = self._query._eval(context)
        return len(result)
    
class Sum(_BaseQuery):
    __implements__ = (IIntResult,)
    def __init__(self, query, field):
        self._query = query
        self.field = field
                
    def _eval(self,context):
        result = self._query._eval(context)
        brain = getBrain(result, context._catalog)
        return sum(brain, self.field)

class Avg(_BaseQuery):
    __implements__ = (IIntResult,)
    def __init__(self, query, field):
        self._query = query
        self.field = field
                
    def _eval(self,context):
        result = self._query._eval(context)
        brain = getBrain(result, context._catalog)
        (resultsum,missing,invalid) = sum(brain, self.field)
        count = len(brain) - missing - invalid
        return (resultsum/count, missing, invalid)

class Around(_ElementaryQuery):
    
    def __init__(self, idx, term, distance, constraint):
        self._idx = idx
        self._term = term

        try:
            self._distance = int(distance)
        except:
            if type(distance)==type('') or type(distance)==type(u'') and distance[0]=='$':
                # is probably a parameter
                self._distance=5 # take default value
            else:
                raise Exception, "SearchOperators: distance is not a convertable integer"

        self._constraint = constraint

    def __str__(self):
        return '%s ~ (%s)' % (self._idx, self._term)

    def _eval(self,context):
        before = self._subquery(context,'min')
        after  = self._subquery(context,'max')
        return IITreeSet(before+after)
    
    def _subquery(self,context,type):
        cat = context._catalog

        term = {'query':self._term, 'range':type}
        rs = context._applyIndex(self._idx, term)
        rs = intersection(rs, self._constraint._eval(context))
        rs = _sort(rs, _normSortSpecs((self._idx,), cat))

        if hasattr(rs, 'keys'): rs= rs.keys() # a TreeSet does not have '__getitem__'
        rs = LazyMap(cat.__getitem__, rs)

        if type=='min' and len(rs)>self._distance:
            rs = rs[:self._distance+1]
        elif type=='max' and len(rs)>self._distance:
            rs = rs[-1-self._distance:]
        
        return map(lambda n:n.getRID(),rs)

class Linked(_BaseQuery):
    """ linked query for integration in AdvancedQuery statements

     example script:
     from Products.AdvancedQuery import Eq, Between, Le, MatchGlob, And, Or, Indexed
     from Products.LinkableObjects import Linked
     pmpcatalog = context.pmpcatalog
     linkmanager = context.CMFLinkManager
     query = Linked(Eq('title','Abr*'), Eq('title','1?'), "Responsible", "target", linkmanager)
     query = Linked(Eq('title','1?'), Eq('title','Abr*'), "Responsible", "source", linkmanager)
     brain = pmpcatalog.evalAdvancedQuery(query,  ('sort_code',))
     for x in brain: print x.title

     explanation:
     Linked(['Abraham I', 'Abraham II', 'Abraham III']], ['1 Geschichte'])
        Link from 'Abraham II' to 'Geschichte' exists
     -> Linked() returns 'Abraham II'

    """     

    def __init__(self, source_query, linktype, target_query,direction,linkmanager):
        self._source_query = source_query
        self._target_query = target_query
        self._linktype     = linktype

        if direction not in ('source','target'): 
            raise Exception, "Invalid value %s for direction, expected (source|target)" % direction

        self._direction    = direction
        self._linkmanager  = linkmanager

    def __str__(self):
        return '((%s) -> (%s) [by linktype %s])' % (self._source_query, self._target_query, self._linktype)

    def _eval(self,context):
        sset=self.getBrains(self._source_query, context) # [brI,brII,brIII]
        tset=self.getBrains(self._target_query, context) # [br1]

        pathresultset=self.linkedDifference(sset, tset) # [/II]
        return self.mapToRID(pathresultset,sset) #[ridII]

    def mapToRID(self, pathresultset,sset):
        ssetmap = OOBTree()

        for i in sset:
            ssetmap[i.getPath()]=i.getRID() # mapping: PATH -> RID

        resultset = IITreeSet()
        for i in pathresultset:
            resultset.insert(ssetmap[i])

        return resultset

    def getBrains(self, query, context):
        set=query._eval(context)
        catalog=context._catalog
        if hasattr(set, 'keys'): set=set.keys() # set can be Set or TreeSet; a TreeSet does not have '__getitem__' 

        set=LazyMap(catalog.__getitem__, set) # map to brain
        return set

    def linkedDifference(self, set1, set2):
        """  e.g. set1: [ridI,ridII,ridIII]
              set2: [rid1] """

        pathset1 = OOTreeSet() # [/I, /II, /III]
        for i in set1:
            pathset1.insert(i.getPath()) # set of paths

        linkset = OOTreeSet() # set of link targets|anchors

        for i in set2:
            # links returned by the link manager need
            # to be paths
            if self._direction=='target':
                links = self._linkmanager.getSourcesFor(i.getPath(),self._linktype) # link [/II -> /1] : return [/II]
            else:
                links = self._linkmanager.getTargetsFor(i.getPath(),self._linktype)
     
            for s in links:

                # compat with CMFLinkManager
                if hasattr(self._linkmanager, 'getBrainFor'):

                    # we want to have the physical path
                    linkset.insert(self._linkmanager.getBrainFor(s).getPath())

                else:
                    linkset.insert(s) # /II

        pathresultset = OOBTreeIntersection(linkset,pathset1) # -> [/II]
        return pathresultset
    
# *** UTILITY FUNCTIONS ***

def getBrain(result, catalog):
    if hasattr(result, 'keys'): result=result.keys() # set can be Set or TreeSet; a TreeSet does not have '__getitem__' 
    return LazyMap(catalog.__getitem__, result) # map to brain

def sum(result, field):
    """
    returns (sum,unindexed,invalid)
    sum: sum of all entries in result;
    unindexed: number of entries which are not indexed
    invalid: number of entries for which the type conversion failed
    """
    sum = 0
    typeerrors=0
    valueerrors=0
    
    for i in result:
        try:
            sum += int(getattr(i,field))
        except TypeError:
            typeerrors+=1
        except ValueError:
            valueerrors+=1
    return (sum,typeerrors,valueerrors)


