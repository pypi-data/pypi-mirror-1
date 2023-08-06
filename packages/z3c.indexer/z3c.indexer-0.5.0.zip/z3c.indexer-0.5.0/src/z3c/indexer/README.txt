======
README
======

Intro
-----

The existing catalog and index implementation get a little out of sync
because there are at leasst 3 different type of indexes. This are FieldIndex,
ValueIndex and SetIndex. Each of them uses a different API if it comes to the
search part. This implementation will make it easier to use all the relevant
catalog index concepts. It also makes the catalog itself obsolate because
the search query API interacts directly with indexes.

The explicit usage of this components will also allow you to index object
if you need them and not because a container likes to do it explicit because
of some default registered generic catalog index subscribers.

This packages tries to improve the different search query concept as well. This
is done in two different levels. The And,Or and Not query are implemented as 
a chainable query processor which allows to apply intersections and union etc. 
based on previous results form the query chain. Other query hooks are directly 
implemented at the index level. This allows us to improve the query concept
directly at the index implementation level for each query index combination.

The implementation of different query types at the index level allows us
to reuse the search query API which makes it easy to reuse for new indexes.
This means you don't have to learn a new search query API if somebody provides
the search query API defined in this package.


Note
----

This package does nothing out of the box, everything is explicit and you have
to decide what you like to do and how. The package offers you a ready to use
API and a nice set of adapters and utilities which you can register and use.
Especialy there is no subscriber which does something for you. You need to 
find your own pattern how and when you need to index your objects. Nothing will
index or unindex objects by default. This is probably not the right concept
for every project but it's needed for one of my project which started having 
performance issues during a search. So I started to review and rethink about
the existing patterns. As far as I can see, there is not much potential for 
improvments in the indexing implementation, but the search and indexing concept
offered by this package provide a hugh performance win. One of my page in a
project which uses a complex query for list some items is now 9 times faster 
because of the new chainable search query. Also note, indexing and build 
inteligent search query patterns are not a easy part and this package can
only help to improve your work if you know what you are doing ;-)

Let me say it again, you can get very quick into trouble if you chain the 
And, Or and Not parts in a bad order. But on the other hand this concept can
incredible speedup your search query because it compares combined queries
against each other and not against all available objects.

Performeance
------------

See also the performance test located in this package. Here is a sample output
from my 2 GHz Duo Core Laptop:

- 1000 x repeat tests

- 10000 objects

- 3 relevant indexes

- 50 other indexes

Note, the index update get only processed one time.

Result for 10000 objects with 3 relevant and 50 other indexes
 ------------------------------------------------------------------------
| type    | indexing |   query | not query |  update |  modify |  remove |
 ------------------------------------------------------------------------
| catalog |   37.39s |  17.83s |    17.83s |  31.14s |   0.05s |  28.53s |
 ------------------------------------------------------------------------
| indexer |    4.84s |  10.75s |    10.84s |   1.66s |   0.03s |   3.73s |
 ------------------------------------------------------------------------
| speedup |   32.55s |   7.08s |    70.03s |  29.48s |   0.02s |  24.80s |
 ------------------------------------------------------------------------
| speedup |     672% |     66% |      646% |   1780% |     47% |    664% |
 ------------------------------------------------------------------------

This speedup tests shows that the indexing and object remove time get improved
by more then 6 times. This is a very common usecase in many application. The
indexer update test is probably not really comparable since we do not update
all indexes. We only update the relevant objects in the index which makes
it very fast. But that's the goal of this package, it offers the concepts
for doing things which can prevent to run into performance problems. Which 
means we can compare the update speedup because the indexes get updated
with the relevant objects. I've you can agree on this, the speedup for 
index update is more then 17 times ;-)


Goals
-----

The goals of this package are:

indexing
~~~~~~~~

  - Allow to explicit define of what, where get indexed

  - Reduce index calls. The existing zope.app.catalog implementation forces to 
    index every object which raises a ObjectAddedEvent. This ends in trying to
    index each object on every existing index contained in a catalog.

  - The existing container add item concept forces to reindex every item
    in a container which is most the time not needed. This is because the 
    existing event dispatching to it's sublocation.  

  - Get rid of persistent catalog and it's index items.

  - Use indexes as utilities

searching
~~~~~~~~~

  - Offer a optimized query function for build search queries. Implement a 
    chainable search query builder


Concepts
--------

The concepts used in this package are:

- Each index is a utility

- The IIndexer can index objects in one or more index

- The default IIndexer adapter will lookup a IIndexValue multi adapter for each
  (object, index) tuple and get the right value from this adapter. You can 
  register custom IIndexer adapters for your objects if you like to avoid this
  additional adapter call.

- Each obj, index pair can have a IIndexValue multi adapter which knows how
  to get the value which get indexed. Only needed if no IIndexer adapter is
  available for your custom object.

- Everything is explicit. This means it does not base on IntIdAddedEvent by 
  default. But you can write your own subscriber if you need to use it.


This will allow you to
----------------------

- choose when you index

- choose how you index, e.g.

  - in AddForm
  
    - call index per object

  - in large data imports
  
    - call update on index after import all objects


And you can make custom speedup improvments like

- index per object or update the index after adding large data sets without
  indexing on each object added event

- write index with built in value getter


Start a simple test setup
-------------------------

Setup some helpers:

  >>> import zope.component
  >>> from zope.app import folder
  >>> from zope.app.component.site import LocalSiteManager
  >>> from z3c.indexer import interfaces
  >>> from z3c.indexer import testing

Setup a site

  >>> class SiteStub(folder.Folder):
  ...     """Sample site."""
  >>> site = SiteStub()

  >>> root['site'] = site
  >>> sm = LocalSiteManager(site)
  >>> site.setSiteManager(sm)

And set the site as the current site. This is normaly done by traversing to a 
site:

  >>> from zope.app.component import hooks
  >>> hooks.setSite(site)

Setup a IIntIds utility:

  >>> from zope.app.intid import IntIds
  >>> from zope.app.intid.interfaces import IIntIds
  >>> intids = IntIds()
  >>> sm['default']['intids'] = intids
  >>> sm.registerUtility(intids, IIntIds)


TextIndex
---------

Setup a text index:

  >>> from z3c.indexer.index import TextIndex
  >>> textIndex = TextIndex()
  >>> sm['default']['textIndex'] = textIndex
  >>> sm.registerUtility(textIndex, interfaces.IIndex, name='textIndex')


FieldIndex
----------

Setup a field index:

  >>> from z3c.indexer.index import FieldIndex
  >>> fieldIndex = FieldIndex()
  >>> sm['default']['fieldIndex'] = fieldIndex
  >>> sm.registerUtility(fieldIndex, interfaces.IIndex, name='fieldIndex')


ValueIndex
----------

Setup a value index:

  >>> from z3c.indexer.index import ValueIndex
  >>> valueIndex = ValueIndex()
  >>> sm['default']['valueIndex'] = valueIndex
  >>> sm.registerUtility(valueIndex, interfaces.IIndex, name='valueIndex')


SetIndex
--------

Setup a set index:

  >>> from z3c.indexer.index import SetIndex
  >>> setIndex = SetIndex()
  >>> sm['default']['setIndex'] = setIndex
  >>> sm.registerUtility(setIndex, interfaces.IIndex, name='setIndex')


DemoContent
-----------

Now we define a content object:

  >>> import persistent
  >>> import zope.interface
  >>> from zope.app.container import contained
  >>> from zope.schema.fieldproperty import FieldProperty

  >>> class IDemoContent(zope.interface.Interface):
  ...     """Demo content."""
  ...     title = zope.schema.TextLine(
  ...         title=u'Title',
  ...         default=u'')
  ... 
  ...     body = zope.schema.TextLine(
  ...         title=u'Body',
  ...         default=u'')
  ... 
  ...     field = zope.schema.TextLine(
  ...         title=u'a field',
  ...         default=u'')
  ... 
  ...     value = zope.schema.TextLine(
  ...         title=u'A value',
  ...         default=u'')
  ... 
  ...     iterable = zope.schema.Tuple(
  ...         title=u'A sequence of values',
  ...         default=())

  >>> class DemoContent(persistent.Persistent, contained.Contained):
  ...     """Demo content."""
  ...     zope.interface.implements(IDemoContent)
  ... 
  ...     title = FieldProperty(IDemoContent['title'])
  ...     body = FieldProperty(IDemoContent['body'])
  ...     field = FieldProperty(IDemoContent['field'])
  ...     value = FieldProperty(IDemoContent['value'])
  ...     iterable = FieldProperty(IDemoContent['iterable'])
  ... 
  ...     def __init__(self, title=u''):
  ...         self.title = title
  ... 
  ...     def __repr__(self):
  ...         return '<%s %r>' % (self.__class__.__name__, self.title)

And we create and add the content object to the site:

  >>> demo = DemoContent(u'Title')
  >>> demo.description = u'Description'
  >>> demo.field = u'Field'
  >>> demo.value = u'Value'
  >>> demo.iterable = (1, 2, 'Iterable')
  >>> site['demo'] = demo

The zope event subscriber for __setitem__ whould call the IIntIds register
method for our content object. But we didn't setup the relevant subscribers, so
we do this here:

  >>> uid = intids.register(demo)


Indexer
-------

Setup a indexer adapter for our content object. Let's define a IIndexer class
which knows how to index text given from body and description attribute:

  >>> from z3c.indexer.indexer import ValueIndexer
  >>> class DemoValueIndexer(ValueIndexer):
  ...     zope.component.adapts(IDemoContent)
  ... 
  ...     indexName = 'textIndex'
  ... 
  ...     @property
  ...     def value(self):
  ...         """Get the value form context."""
  ...         return '%s %s' % (self.context.title, self.context.body)

Register the adapter as a named adapter:

  >>> zope.component.provideAdapter(DemoValueIndexer, name='textIndex')

We can also use a indexer wich knows how to index the object in different 
indexes.

  >>> from z3c.indexer.indexer import MultiIndexer
  >>> class DemoMultiIndexer(MultiIndexer):
  ...     zope.component.adapts(IDemoContent)
  ... 
  ...     def doIndex(self):
  ... 
  ...         # index context in fieldIndex
  ...         fieldIndex = self.getIndex('fieldIndex')
  ...         fieldIndex.doIndex(self.oid, self.context.field)
  ... 
  ...         # index context in setIndex
  ...         setIndex = self.getIndex('setIndex')
  ...         setIndex.doIndex(self.oid, self.context.iterable)
  ... 
  ...         # index context in valueIndex
  ...         valueIndex = self.getIndex('valueIndex')
  ...         valueIndex.doIndex(self.oid, self.context.value)
  ... 
  ...     def doUnIndex(self):
  ... 
  ...         # index context in fieldIndex
  ...         fieldIndex = self.getIndex('fieldIndex')
  ...         fieldIndex.doUnIndex(self.oid)
  ... 
  ...         # index context in setIndex
  ...         setIndex = self.getIndex('setIndex')
  ...         setIndex.doUnIndex(self.oid)
  ... 
  ...         # index context in valueIndex
  ...         valueIndex = self.getIndex('valueIndex')
  ...         valueIndex.doUnIndex(self.oid)

Register the adapter as a named adapter:

  >>> zope.component.provideAdapter(DemoMultiIndexer, name='DemoMultiIndexer')


Indexing
--------

Before we start indexing, we check the index:

  >>> textIndex.documentCount()
  0

  >>> setIndex.documentCount()
  0

  >>> valueIndex.documentCount()
  0

Now we can index our demo object:

  >>> from z3c.indexer.indexer import index
  >>> index(demo)

And check our indexes:

  >>> textIndex.documentCount()
  1

  >>> setIndex.documentCount()
  1

  >>> valueIndex.documentCount()
  1


Auto indexing
-------------

Sometimes, you like to ensure that each object get indexed or updated in the 
index like we us to do in the default zope.app.catalog implementation. This 
means each object get index after adding or updated on object modification.
We offer a solution for this behavior with the IAutoIndexer adapter call.
On each object added event or object modified event, a subscriber tries to 
lookup an IAutoIndexer which could index or update the object values in the 
relevant indexes. Since the subscriber calls getAdapters, it's allowed to 
have more then one such indexer adapter. 

First register a new index:

  >>> from z3c.indexer.index import TextIndex
  >>> autoIndex = TextIndex()
  >>> sm['default']['autoIndex'] = textIndex
  >>> sm.registerUtility(autoIndex, interfaces.IIndex, name='autoIndex')

The new auto (text) index does not contain any indexed objects right now:

  >>> autoIndex.documentCount()
  0

Let's now define a IAutoIndexer adapter:

  >>> from z3c.indexer.indexer import ValueAutoIndexer
  >>> class MyDemoContentAutoIndexer(ValueAutoIndexer):
  ...     zope.component.adapts(IDemoContent)
  ... 
  ...     indexName = 'autoIndex'
  ... 
  ...     @property
  ...     def value(self):
  ...         """Get the value form context."""
  ...         return 'auto indexed value: %s %s' % (self.context.title,
  ...             self.context.body)

and register them:

  >>> zope.component.provideAdapter(MyDemoContentAutoIndexer, name='Auto')

Now we need to register our subscriber which calls the IAutoIndexer adapters:

  >>> from z3c.indexer import subscriber
  >>> zope.component.provideHandler(subscriber.autoIndexSubscriber)
  >>> zope.component.provideHandler(subscriber.autoUnindexSubscriber)

and we also need to register the intid subscribers:

  >>> from zope.app.intid import addIntIdSubscriber
  >>> from zope.app.intid import removeIntIdSubscriber
  >>> zope.component.provideHandler(addIntIdSubscriber)
  >>> zope.component.provideHandler(removeIntIdSubscriber)

If we now add a new object it get auomaticly indexed without to call the 
indexer method explicit:

  >>> autoIndex.documentCount()
  0

  >>> textIndex.documentCount()
  1

  >>> setIndex.documentCount()
  1

  >>> valueIndex.documentCount()
  1

Let's now add a new content object:

  >>> autoDemo = DemoContent(u'Auto')
  >>> autoDemo.description = u'Auto Demo'
  >>> autoDemo.field = u'Auto field'
  >>> autoDemo.value = u'auto value'
  >>> autoDemo.iterable = (1, 2, 'Iterable')
  >>> site['autoDemo'] = autoDemo

You can see that we've got a key reference for the new object:

  >>> intids.getId(autoDemo) is not None
  True

You can see that the new object get added without to call the index method
defined in indexer module:

  >>> autoIndex.documentCount()
  1

  >>> textIndex.documentCount()
  1

  >>> setIndex.documentCount()
  1

  >>> valueIndex.documentCount()
  1

As you can see only the ``autoIndex`` get used.

Of corse there is also a ``auto`` unindex implementation which get used if we
remove the object:

  >>> del site['autoDemo']

As you can see the object got removed from the ``autoIndex``:

  >>> autoIndex.documentCount()
  0

  >>> textIndex.documentCount()
  1

  >>> setIndex.documentCount()
  1

  >>> valueIndex.documentCount()
  1


SearchQuery
-----------

Text Index Query
~~~~~~~~~~~~~~~~

Build a simple text search query:

  >>> from z3c.indexer.search import SearchQuery
  >>> from z3c.indexer.query import TextQuery
  >>> textQuery = TextQuery('textIndex', 'Title')
  >>> query = SearchQuery(textQuery)

Now let's see if we get ``uid`` from the content object:

  >>> res = query.apply()
  >>> res[0] == uid
  True

A none existent value will return a emtpy result:

  >>> textQuery = TextQuery('textIndex', 'bad')
  >>> query = SearchQuery(textQuery)
  >>> query.apply()
  IFSet([])


Field Index Query
~~~~~~~~~~~~~~~~~

Search with a Eq query:

  >>> from z3c.indexer.query import Eq
  >>> eqQuery = Eq('fieldIndex', 'Field')
  >>> query = SearchQuery(eqQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A none existent value will return a emtpy result:

  >>> eqQuery = Eq('fieldIndex', 'bad')
  >>> query = SearchQuery(eqQuery)
  >>> query.apply()
  IFSet([])

Search with a NotEq query:

  >>> from z3c.indexer.query import NotEq
  >>> notEqQuery = NotEq('fieldIndex', 'bad')
  >>> query = SearchQuery(notEqQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A existent value will return a emtpy result:

  >>> notEqQuery = NotEq('fieldIndex', 'Field')
  >>> query = SearchQuery(notEqQuery)
  >>> query.apply()
  IFSet([])

Search with a Between query:

  >>> from z3c.indexer.query import Between
  >>> betweenQuery = Between('fieldIndex', 'Fiel', 'Fielder')
  >>> query = SearchQuery(betweenQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A wrong min and max value will return a emtpy result:

  >>> betweenQuery = Between('fieldIndex', 'Fielder', 'Fiel')
  >>> query = SearchQuery(betweenQuery)
  >>> query.apply()
  IFSet([])

Search with a Ge query:

  >>> from z3c.indexer.query import Ge
  >>> geQuery = Ge('fieldIndex', 'Fiel')
  >>> query = SearchQuery(geQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A wrong max value will return a emtpy result:

  >>> geQuery = Ge('fieldIndex', 'Fielder')
  >>> query = SearchQuery(geQuery)
  >>> query.apply()
  IFSet([])

Search with a Le query:

  >>> from z3c.indexer.query import Le
  >>> leQuery = Le('fieldIndex', 'Fielder')
  >>> query = SearchQuery(leQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A wrong min value will return a emtpy result:

  >>> leQuery = Le('fieldIndex', 'Fiel')
  >>> query = SearchQuery(leQuery)
  >>> query.apply()
  IFSet([])

Search with a In query:

  >>> from z3c.indexer.query import In
  >>> inQuery = In('fieldIndex', ['Field', 1, 2])
  >>> query = SearchQuery(inQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A list of none existent values will return a emtpy result:

  >>> inQuery = In('fieldIndex', ['Fielder', 1, 2])
  >>> query = SearchQuery(inQuery)
  >>> query.apply()
  IFSet([])


Value Index Query
~~~~~~~~~~~~~~~~~

Search with a Eq query:

  >>> eqQuery = Eq('valueIndex', 'Value')
  >>> query = SearchQuery(eqQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A none existent value will return a emtpy result:

  >>> eqQuery = Eq('valueIndex', 'bad')
  >>> query = SearchQuery(eqQuery)
  >>> query.apply()
  IFSet([])

Search with a NotEq query:

  >>> notEqQuery = NotEq('valueIndex', 'bad')
  >>> query = SearchQuery(notEqQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A existent value will return a emtpy result:

  >>> notEqQuery = NotEq('valueIndex', 'Value')
  >>> query = SearchQuery(notEqQuery)
  >>> query.apply()
  IFSet([])

Search with a Between query:

  >>> betweenQuery = Between('valueIndex', 'Val', 'Values')
  >>> query = SearchQuery(betweenQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A wrong min and max value will return a emtpy result:

  >>> betweenQuery = Between('valueIndex', 'Values', 'Val')
  >>> query = SearchQuery(betweenQuery)
  >>> query.apply()
  IFSet([])

Search with a Ge query:

  >>> geQuery = Ge('valueIndex', 'Val')
  >>> query = SearchQuery(geQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A wrong max value will return a emtpy result:

  >>> geQuery = Ge('valueIndex', 'Values')
  >>> query = SearchQuery(geQuery)
  >>> query.apply()
  IFSet([])

Search with a Le query:

  >>> leQuery = Le('valueIndex', 'Values')
  >>> query = SearchQuery(leQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A wrong min value will return a emtpy result:

  >>> leQuery = Le('valueIndex', 'Val')
  >>> query = SearchQuery(leQuery)
  >>> query.apply()
  IFSet([])

Search with a In query:

  >>> inQuery = In('valueIndex', ['Value', 1, 2])
  >>> query = SearchQuery(inQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A list of none existent values will return a emtpy result:

  >>> inQuery = In('valueIndex', ['Values', 1, 2])
  >>> query = SearchQuery(inQuery)
  >>> query.apply()
  IFSet([])

Search with a ExtentAny query:

  >>> from zc.catalog.extentcatalog import Extent
  >>> from z3c.indexer.query import ExtentAny
  >>> extent = Extent()
  >>> extent.add(uid, ['Values', 1, 2])

  >>> extentAnyQuery = ExtentAny('valueIndex', extent)
  >>> query = SearchQuery(extentAnyQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

Search with a ExtentNone query:

  >>> from z3c.indexer.query import ExtentNone
  >>> extentNoneQuery = ExtentNone('valueIndex', extent)
  >>> query = SearchQuery(extentNoneQuery)
  >>> res = query.apply()
  >>> len(res)
  0


Set Index Query
~~~~~~~~~~~~~~~

Search with a AnyOf query:

  >>> from z3c.indexer.query import AnyOf
  >>> anyOfQuery = AnyOf('setIndex', ['Iterable', 1])
  >>> query = SearchQuery(anyOfQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A list of none existent values will return a emtpy result:

  >>> anyOfQuery = AnyOf('setIndex', ['Iter', 3])
  >>> query = SearchQuery(anyOfQuery)
  >>> query.apply()
  IFSet([])

Search with a AllOf query:

  >>> from z3c.indexer.query import AllOf
  >>> allOfQuery = AllOf('setIndex', ['Iterable', 1, 2])
  >>> query = SearchQuery(allOfQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A list of to less values will return the same result:

  >>> from z3c.indexer.query import AllOf
  >>> allOfQuery = AllOf('setIndex', ['Iterable', 1])
  >>> query = SearchQuery(allOfQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A list of to much values will return a emtpy result:

  >>> allOfQuery = AllOf('setIndex', ['Iterable', 1, 2, 3])
  >>> query = SearchQuery(allOfQuery)
  >>> query.apply()
  IFSet([])

Search with a Between query:

  >>> betweenQuery = Between('setIndex', 'Iter', 'Iterables')
  >>> query = SearchQuery(betweenQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A wrong min and max value will return a emtpy result:

  >>> betweenQuery = Between('setIndex', 'Iterables', 'Iter')
  >>> query = SearchQuery(betweenQuery)
  >>> query.apply()
  IFSet([])

Search with a Ge query:

  >>> geQuery = Ge('valueIndex', 'Iter')
  >>> query = SearchQuery(geQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A wrong max value will return a emtpy result:

  >>> geQuery = Ge('setIndex', 'Iterables')
  >>> query = SearchQuery(geQuery)
  >>> query.apply()
  IFSet([])

Search with a Le query:

  >>> leQuery = Le('setIndex', 'Iterables')
  >>> query = SearchQuery(leQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

A wrong min value will return a emtpy result:

  >>> leQuery = Le('setIndex', 0)
  >>> query = SearchQuery(leQuery)
  >>> query.apply()
  IFSet([])

Search with a ExtentAny query:

  >>> extentAnyQuery = ExtentAny('setIndex', extent)
  >>> query = SearchQuery(extentAnyQuery)
  >>> res = query.apply()
  >>> res[0] == uid
  True

Search with a ExtentNone query:

  >>> extent = Extent()
  >>> extent.add(uid, ['Iterables'])
  >>> extentNoneQuery = ExtentNone('setIndex', extent)
  >>> query = SearchQuery(extentNoneQuery)
  >>> query.apply()
  IFSet([])


Chainable Search Query
----------------------

A search query is chainable. This means we can append queries to queries 
itself. The result of a previous query will be used for the next query in the 
chain. Note, this pattern can give you hugh speedup but you have to take care 
on what you chain in which order or you will very quickly get a wrong result.
But the speedup can be hugh, I optimized one of my application with this 
pattern and got a speedup by 900%.

Let's cleanup the text index first:

  >>> textIndex.clear()

And add some more demo object with different values:

  >>> apple = DemoContent(u'Apple')
  >>> site['apple'] = apple
  >>> appleId = intids.register(apple)

  >>> house = DemoContent(u'House')
  >>> site['house'] = house
  >>> houseId = intids.register(house) 

  >>> tower = DemoContent(u'Tower') 
  >>> site['tower'] = tower
  >>> towerId = intids.register(tower)

  >>> every = DemoContent(u'Apple House Tower') 
  >>> site['every'] = every
  >>> everyId = intids.register(every)

And register them in the text index:

  >>> index(apple)
  >>> index(house)
  >>> index(tower)
  >>> index(every)

Now we can see that we have 3 items in the text index:

  >>> textIndex.documentCount()
  4

Let's buold some query:

  >>> appleQuery = TextQuery('textIndex', 'Apple')
  >>> houseQuery = TextQuery('textIndex', 'House')
  >>> towerQuery = TextQuery('textIndex', 'Tower')


And SearchQuery
---------------

Now we can build a search query chain with this queries. The following sample
will return all items which are returned by the 'Apple' and the 'House' query
This is only the case for the ``every`` object:

  >>> query = SearchQuery(appleQuery).And(houseQuery)
  >>> res = query.apply()
  >>> res[0] == everyId
  True

  >>> intids.getObject(res[0])
  <DemoContent u'Apple House Tower'>


Or SearchQuery
--------------

A Or search query will return all object which are contained in each query. The
search query below will return all 4 objects becaues each of them get found by 
one of the existing queries. And the ``every`` object will only get listed once:

  >>> allQuery = SearchQuery(appleQuery).Or(houseQuery).Or(towerQuery)
  >>> res = allQuery.apply()
  >>> len(res)
  4


Not SearchQuery
---------------

A Not search query will return all object which are not contained in the given 
query. The search query below will return all objects except the ones which 
contains the word ``Apple`` becaues we exclude them within the appleQuery. 
Another interesting thing is, that we can use the previous query and simple 
add another query to the chain. This is a very interesting pattern for filters.

  >>> query = allQuery.Not(appleQuery)
  >>> res = query.apply()
  >>> len(res)
  2

  >>> intids.getObject(sorted(res)[0])
  <DemoContent u'House'>

  >>> intids.getObject(sorted(res)[1])
  <DemoContent u'Tower'>


ResultSet
---------

The SearchQuery provides also a ResultSet wrapper. We can get an iterable 
ResultSet instance if we call ``searchResults`` from the search query:

  >>> allQuery = SearchQuery(appleQuery).Or(houseQuery).Or(towerQuery)
  >>> resultSet = allQuery.searchResults()
  >>> len(resultSet)
  4

Or we can get a slice from the ResultSet:

  >>> resultSet[-1:]
  [<DemoContent u'Apple House Tower'>]

  >>> resultSet[0:]
  [<DemoContent u'Apple'>, <DemoContent u'House'>, <DemoContent u'Tower'>,
   <DemoContent u'Apple House Tower'>]

  >>> resultSet[1:]
  [<DemoContent u'House'>, <DemoContent u'Tower'>,
   <DemoContent u'Apple House Tower'>]

  >>> resultSet[:-2]
  [<DemoContent u'Apple'>, <DemoContent u'House'>]

Or we can iterate over the ResultSet:

  >>> list(resultSet)
  [<DemoContent u'Apple'>, <DemoContent u'House'>, <DemoContent u'Tower'>,
   <DemoContent u'Apple House Tower'>]

Or check if a item is a part of the result set:

  >>> resultSet.__contains__(object())
  False

  >>> resultSet.__contains__(apple)
  True



Batching
--------

This ResultSet described above can be used together with the BAtch 
implementation defined in the z3c.batching package.


unindex
-------

Now after the different index and serch tests we are ready to unindex our 
indexed objects. Let's see what we have in the indexes:

  >>> textIndex.documentCount()
  4

  >>> setIndex.documentCount()
  1

  >>> valueIndex.documentCount()
  5

Now let's use our unindex method from the module indexer. This will call our
Indexer adapter and delegate the unindex call to the doUnIndex method of such
a IIndexer adapter. Let's unindex our demo object:

  >>> from z3c.indexer.indexer import unindex
  >>> unindex(demo)

Now you can see that the dome object get reomved:

  >>> textIndex.documentCount()
  4

  >>> setIndex.documentCount()
  0

  >>> valueIndex.documentCount()
  4


Coverage
--------

Let's test some line of code which are not used right now. First test if the
base class IndexerBase raises a NotImplementedError if we do not implement the 
methods:

  >>> from z3c.indexer.indexer import IndexerBase
  >>> indexerBase = IndexerBase(object())
  >>> indexerBase.doIndex()
  Traceback (most recent call last):
  ...
  NotImplementedError: Subclass must implement doIndex method.

  >>> indexerBase.doUnIndex()
  Traceback (most recent call last):
  ...
  NotImplementedError: Subclass must implement doUnIndex method.

The MutliIndexer does also not implement this methods:

  >>> from z3c.indexer.indexer import MultiIndexer
  >>> multiIndexer = MultiIndexer(object())
  >>> multiIndexer.doIndex()
  Traceback (most recent call last):
  ...
  NotImplementedError: Subclass must implement doIndex method.

  >>> multiIndexer.doUnIndex()
  Traceback (most recent call last):
  ...
  NotImplementedError: Subclass must implement doUnIndex method.

And the ValueIndexer does not implement the value attribute:

  >>> valueIndexer = ValueIndexer(object())
  >>> valueIndexer.indexName = 'textIndex'
  >>> valueIndexer.value
  Traceback (most recent call last):
  ...
  NotImplementedError: Subclass must implement value property.

Another use case which we didn't test is that a applyIn can contain the
same object twice with different values. Let's test the built in union
which removes such duplications:

  >>> demo1 = DemoContent(u'Demo 1')
  >>> demo1.description = u'Description'
  >>> demo1.field = u'Field'
  >>> demo1.value = u'Value'
  >>> demo1.iterable = (1, 2, 'Iterable')
  >>> site['demo1'] = demo1
  >>> index(demo1)

  >>> demo2 = DemoContent(u'Demo 2')
  >>> demo2.description = u'Description'
  >>> demo2.field = u'Field'
  >>> demo2.value = u'Value'
  >>> demo2.iterable = (1, 2, 'Iterable')
  >>> site['demo2'] = demo2
  >>> index(demo2)

  >>> inQuery = In('fieldIndex', ['Field', 'Field'])
  >>> query = SearchQuery(inQuery)
  >>> resultSet = query.searchResults()
  >>> resultSet.__contains__(demo1)
  True
  >>> resultSet.__contains__(demo2)
  True

A SearchQuery allows us to set a BTrees family argument:

  >>> import BTrees

  >>> textDemo = DemoContent(u'Text Demo')
  >>> textDemo.description = u'Description'
  >>> site['textDemo'] = textDemo
  >>> index(textDemo)

  >>> textQuery = TextQuery('textIndex', 'Text Demo')
  >>> query = SearchQuery(textQuery, BTrees.family32)
  >>> resultSet.__contains__(demo1)
  True
