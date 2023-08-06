Introduction
============

CompositeIndex is a plugin index for the ZCatalog. Indexes
containing more than one attribute to index an object are called
"composite index". Such indexes should be created if you expect to run
queries that will have multiple attributes in the search phrase and
all attributes combined will give significantly less hits than the any
of the attributes alone. The key of a composite index is called
"composite key" and is composed of two or more attributes of an
object.

Catalog queries containing attributes managed by CompositeIndex
are transparently catched and transformed into a CompositeIndex query
(monkey patch). In particular, large sites with a combination of
additional indexes (FieldIndex, KeywordIndex) and lots of content
(>100k) will profit. The expected performance enhancement for catalog
queries is about a factor of >2-3.

Statistics
==========


.. figure:: https://svn.plone.org/svn/collective/unimr.compositeindex/trunk/docs/stats-plot.png
   :alt: Ratio of Calculation Time bet. Atomic- and Composite Index 

   Ratio of Calculation Time between Atomic- and Composite Index queries.

   The plot shows that the performance of CompositeIndex increases
   significantly with increasing number of indexed objects (>1000
   catalog entries) and with increasing number of combined
   attributes. The hit rate of the queries was about 6% for two
   combined attributes and 1% for three combined attributes of the
   total number of catalog entries. For uniform comparability, the
   ZODB cache was cleared before each query.
   

Usage
=====

From the ZCatalog indexes tab, add an index of type CompositeIndex.

Id
    pick any valid id you like


Composite key
    names of attributes to concatenate


Example for Plone's portal_catalog
==================================

Many catalog queries in plone are based on the combination of indexed
attributes as follows: is_default_page, review_state, portal_type and
allowedRolesAndUsers. Normally, the ZCatalog sequentially executes
each corresponding atomic index and calculates intersection between each
result. This strategy, in particular for large sites, decreases the
performance of the catalog and simultaneously increases the volatility
of ZODB's object cache, because each index individually has a high
number of hits whereas the the intersection between each index result
has a low number of hits.

CompositeIndex overcomes this difficulty because it already contains a
pre-calculateted intersection by means of its composite keys. The
loading of large sets and the following expensive computation of the
intersection is therefore obsolete.

Here we show a configuration example for plone. From the portal_catalog
indexes tab, add a index of type CompositeIndex.

  Id: comp01

  Composite key: is_default_page,review_state,portal_type,allowedRolesAndUsers


Reindex the CompositeIndex "comp01".


Now each query which contains two ore more components of the composite
key is automatically transformed into a query on the CompositeIndex
"comp01".
