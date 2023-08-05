The Relationship package currently contains two main types of components: a
relationship index, and some relationship containers.  Both are designed for
use within the ZODB.  They share the model that relationships are full-fledged
objects that are indexed for optimized searches.  They also share the ability
to perform optimized intransitive and transitive relationship searches, and
to support arbitrary filter searches on relationship tokens.

The index is a very generic component that can be used to optimize searches
for N-ary relationships, can be used standalone or within a catalog, can be
used with pluggable token generation schemes, and generally tries to provide
a relatively policy-free tool.  It is expected to be used primarily as an
engine for more specialized and constrained tools and APIs.

The relationship containers use the index to manage two-way relationships,
using a derived mapping interface.  It is a good example of the index in
standalone use.

This document describes the relationship index.  See container.txt for
documentation of the relationship container.

=====
Index
=====

The index interface searches for object and relationship tokens. To use a
relationship index, you need to have interface attributes, or methods callable
with no arguments, that are treated as relationship pointers.  The pointers
may be a collection of items or a single item.

To exercise the index, we'll come up with a somewhat complex relationship to
index. Let's say we are modeling a generic set-up like SUBJECT
RELATIONSHIPTYPE OBJECT in CONTEXT.  This could let you let users define
relationship types, then index them on the fly.  The context can be something
like a project, so we could say

"Fred" "has the role of" "Project Manager" on the "zope.org redesign project".

Mapped to the parts of the relationship object, that's

["Fred" (SUBJECT)] ["has the role of" (RELATIONSHIPTYPE)]
["Project Manager" (OBJECT)] on the ["zope.org redesign project" (CONTEXT)].

Without the context, you can still do interesting things like

["Ygritte" (SUBJECT)] ["manages" (RELATIONSHIPTYPE)] ["Uther" (OBJECT)]

So let's define a basic interface without the context, and then an extended
interface with the context.

    >>> from zope import interface
    >>> class IRelationship(interface.Interface):
    ...     subjects = interface.Attribute(
    ...         'The sources of the relationship; the subject of the sentence')
    ...     relationshiptype = interface.Attribute(
    ...         '''unicode: the single relationship type of this relationship;
    ...         usually contains the verb of the sentence.''')
    ...     objects = interface.Attribute(
    ...         '''the targets of the relationship; usually a direct or
    ...         indirect object in the sentence''')
    ...
    >>> class IContextAwareRelationship(IRelationship):
    ...     def getContext():
    ...         '''return a context for the relationship'''
    ...

Now we'll create an index.  To do that, we must minimally pass in an iterable
describing the indexed values.  Each item in the iterable must either be an
interface element (a zope.interface.Attribute or zope.interface.Method
associated with an interface, typically obtained using a spelling like
`IRelationship['subjects']`) or a dict.  Each dict must have at least one key:
'element', which is the interface element to be indexed.  It then can contain
other keys to override the default indexing behavior for the element.

The element's __name__ will be used to refer to this element in queries, unless
the dict has a 'name' key, which must be a non-empty string.

The element is assumed to be a single value, unless the dict has a 'multiple'
key with a value equivalent True.  In our example, "subjects" and "objects" are
potentially multiple values, while "relationshiptype" and "getContext" are
single values.

By default, the values for the element will be tokenized and resolved using an
intid utility, and stored in a BTrees.IFBTree.  This is a good choice if you
want to make object tokens easily mergable with typical Zope 3 catalog
results.  If you need different behavior for any element, you can specify
three keys per dict:

- 'dump', the tokenizer, a callable taking (obj, index, cache) and returning a
  token;

- 'load' the token resolver, a callable taking (token, index, cache) to return
  the object which the token represents; and

- 'btree', the btree module to use to store and process the tokens, such as
  BTrees.OOBTree.

If you provide a custom 'dump' you will almost certainly need to provide a
custom 'load'; and if your tokens are not integers then you will need to
specify a different 'btree' (either BTrees.OOBTree or BTrees.OIBTree, as of
this writing).

The tokenizing function ('dump') *must* return homogenous, immutable tokens:
that is, any given tokenizer should only return tokens that sort
unambiguously, across Python versions, which usually mean that they are all of
the same type.  For instance, a tokenizer should only return ints, or only
return strings, or only tuples of strings, and so on.  Different tokenizers
used for different elements in the same index may return different types. They
also may return the same value as the other tokenizers to mean different
objects: the stores are separate.

In addition to the one required argument to the class, the signature contains
four optional arguments.  The 'defaultTransitiveQueriesFactory' is the next,
and allows you to specify a callable as described in
interfaces.ITransitiveQueriesFactory.  Without it transitive searches will
require an explicit factory every time, which can be tedious.  The index
package provides a simple implementation that supports transitive searches
following two indexed elements (TransposingTransitiveQueriesFactory) and this
document describes more complex possible transitive behaviors that can be
modeled.  For our example, "subjects" and "objects" are the default transitive
fields, so if Ygritte (SUBJECT) manages Uther (OBJECT), and Uther (SUBJECT)
manages Emily (OBJECT), a search for all those transitively managed by Ygritte
will transpose Uther from OBJECT to SUBJECT and find that Uther manages Emily.
Similarly, to find all transitive managers of Emily, Uther will change place
from SUBJECT to OBJECT in the search.

The next three arguments, 'dumpRel', 'loadRel' and 'relFamily', have
to do with the relationship tokens.  The default values assume that you will
be using intid tokens for the relationships, and so 'dumpRel' and
'loadRel' tokenize and resolve, respectively, using the intid utility; and
'relFamily' defaults to BTrees.IFBTree.

If relationship tokens (from 'findRelationshipChains' or 'apply' or
'findRelationshipTokenSet', or in a filter to most of the search methods) are
to be merged with other catalog results, relationship tokens should be based
on intids, as in the default.  For instance, if some relationships are only
available to some users on the basis of security, and you keep an index of
this, then you will want to use a filter based on the relationship tokens
viewable by the current user as kept by the catalog index.

If you are unable or unwilling to use intid relationship tokens, tokens must
still be homogenous and immutable as described above for indexed values tokens.

The last argument is 'deactivateSets', which defaults to False.  This is an
optimization to try and keep relationship index searches from consuming too
much of the ZODB's object cache.  It can cause inefficiency under some
usages--if queries against the relationship index are very frequent and often
use the same sets, for instance--and it exposes a bug in the ZODB at the time
of this writing (_p_deactivate on a new object that has been given an _p_oid
but has not yet been committed will irretrievably snuff out the object before
it has had a chance to be committed, so if you add and query in the same
transaction you will have trouble).  Pass True to this argument to enable
this optimization.

If we had an IIntId utility registered and wanted to use the defaults, then
instantiation  of an index for our relationship would look like this:

    >>> from zc.relationship import index
    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True},
    ...      IRelationship['relationshiptype'],
    ...      {'element': IRelationship['objects'], 'multiple': True},
    ...      IContextAwareRelationship['getContext']),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))

That's the simple case.  With relatively little fuss, we have an IIndex, and a
defaultTransitiveQueriesFactory, implementing ITransitiveQueriesFactory, that
switches subjects and objects as described above.

    >>> from zc.relationship import interfaces
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(interfaces.IIndex, ix)
    True
    >>> verifyObject(
    ...     interfaces.ITransitiveQueriesFactory,
    ...     ix.defaultTransitiveQueriesFactory)
    True

For the purposes of a more complex example, though, we are going to exercise
more of the index's options--we'll use at least one of 'name', 'dump', 'load',
and 'btree'.

- 'subjects' and 'objects' will use a custom integer-based token generator.
  They will share tokens, which will let us use the default
  TransposingTransitiveQueriesFactory.  We can keep using the IFBTree sets,
  because the tokens are still integers.

- 'relationshiptype' will use a name 'reltype' and will just use the unicode
  value as the token, without translation but with a registration check.

- 'getContext' will use a name 'context' but will continue to use the intid
  utility and use the names from their interface.  We will see later that
  making transitive walks between different token sources must be handled with
  care.

We will also use the intid utility to resolve relationship tokens.  See the
relationship container (and container.txt) for examples of changing the
relationship type, especially in keyref.py.  The example also turns on the
'deactivateSets' optimization.

Here are the methods we'll use for the 'subjects' and 'objects' tokens,
followed by the methods we'll use for the 'relationshiptypes' tokens.

    >>> lookup = {}
    >>> counter = [-2147483648]
    >>> prefix = '_z_token__'
    >>> def dump(obj, index, cache):
    ...     assert (interfaces.IIndex.providedBy(index) and
    ...             isinstance(cache, dict)), (
    ...         'did not receive correct arguments')
    ...     token = getattr(obj, prefix, None)
    ...     if token is None:
    ...         token = counter[0]
    ...         counter[0] += 1
    ...         if counter[0] >= 2147483647:
    ...             raise RuntimeError("Whoa!  That's a lot of ids!")
    ...         assert token not in lookup
    ...         setattr(obj, prefix, token)
    ...         lookup[token] = obj
    ...     return token
    ...
    >>> def load(token, index, cache):
    ...     assert (interfaces.IIndex.providedBy(index) and
    ...             isinstance(cache, dict)), (
    ...         'did not receive correct arguments')
    ...     return lookup[token]
    ...
    >>> relTypes = []
    >>> def relTypeDump(obj, index, cache):
    ...     assert obj in relTypes, 'unknown relationshiptype'
    ...     return obj
    ...
    >>> def relTypeLoad(token, index, cache):
    ...     assert token in relTypes, 'unknown relationshiptype'
    ...     return obj
    ...

Note that these implementations are completely silly if we actually cared about
ZODB-based persistence: to even make it half-acceptable we should make the
counter, lookup, and and relTypes persistently stored somewhere using a
reasonable persistent data structure.  This is just a demonstration example.

Now we can make an index.

As in our initial example, we are going to use the simple transitive query
factory defined in the index module for our default transitive behavior: when
you want to do transitive searches, transpose 'subjects' with 'objects' and
keep everything else; and if both subjects and objects are provided, don't do
any transitive search.

    >>> from BTrees import OIBTree # could also be OOBTree
    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True,
    ...       'dump': dump, 'load': load},
    ...      {'element': IRelationship['relationshiptype'],
    ...       'dump': relTypeDump, 'load': relTypeLoad, 'btree': OIBTree,
    ...       'name': 'reltype'},
    ...      {'element': IRelationship['objects'], 'multiple': True,
    ...       'dump': dump, 'load': load},
    ...      {'element': IContextAwareRelationship['getContext'],
    ...       'name': 'context'}),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))

We'll want to put the index somewhere in the system so it can find the intid
utility.  We'll add it as a utility just as part of the example.  As long as
the index has a valid __parent__ that is itself connected transitively to a
site manager with the desired intid utility, everything should work fine, so
no need to install it as utility.  This is just an example.

    >>> from zope import interface
    >>> sm = app.getSiteManager()
    >>> sm['rel_index'] = ix
    >>> import zope.component.interfaces
    >>> registry = zope.component.interfaces.IComponentRegistry(sm)
    >>> registry.registerUtility(ix, interfaces.IIndex)
    >>> import transaction
    >>> transaction.commit()

Now we'll create some representative objects that we can relate, and create
and index our first example relationship.

In the example, note that the context will only be available as an adapter to
ISpecialRelationship objects: the index tries to adapt objects to the
appropriate interface, and considers the value to be empty if it cannot adapt.

    >>> import persistent
    >>> from zope.app.container.contained import Contained
    >>> class Base(persistent.Persistent, Contained):
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return '<%s %r>' % (self.__class__.__name__, self.name)
    ...
    >>> class Person(Base): pass
    ...
    >>> class Role(Base): pass
    ...
    >>> class Project(Base): pass
    ...
    >>> class Company(Base): pass
    ...
    >>> class Relationship(persistent.Persistent, Contained):
    ...     interface.implements(IRelationship)
    ...     def __init__(self, subjects, relationshiptype, objects):
    ...         self.subjects = subjects
    ...         assert relationshiptype in relTypes
    ...         self.relationshiptype = relationshiptype
    ...         self.objects = objects
    ...     def __repr__(self):
    ...         return '<%r %s %r>' % (
    ...             self.subjects, self.relationshiptype, self.objects)
    ...
    >>> class ISpecialRelationship(interface.Interface):
    ...     pass
    ...
    >>> from zope import component
    >>> class ContextRelationshipAdapter(object):
    ...     component.adapts(ISpecialRelationship)
    ...     interface.implements(IContextAwareRelationship)
    ...     def __init__(self, adapted):
    ...         self.adapted = adapted
    ...     def getContext(self):
    ...         return getattr(self.adapted, '_z_context__', None)
    ...     def setContext(self, value):
    ...         self.adapted._z_context__ = value
    ...     def __getattr__(self, name):
    ...         return getattr(self.adapted, name)
    ...
    >>> component.provideAdapter(ContextRelationshipAdapter)
    >>> class SpecialRelationship(Relationship):
    ...     interface.implements(ISpecialRelationship)
    ...
    >>> people = {}
    >>> for p in ['Abe', 'Bran', 'Cathy', 'David', 'Emily', 'Fred', 'Gary',
    ...           'Heather', 'Ingrid', 'Jim', 'Karyn', 'Lee', 'Mary',
    ...           'Nancy', 'Olaf', 'Perry', 'Quince', 'Rob', 'Sam', 'Terry',
    ...           'Uther', 'Van', 'Warren', 'Xen', 'Ygritte', 'Zane']:
    ...     app[p] = people[p] = Person(p)
    ...
    >>> relTypes.extend(
    ...     ['has the role of', 'manages', 'taught', 'commissioned'])
    >>> roles = {}
    >>> for r in ['Project Manager', 'Software Engineer', 'Designer',
    ...           'Systems Administrator', 'Team Leader', 'Mascot']:
    ...     app[r] = roles[r] = Role(r)
    ...
    >>> projects = {}
    >>> for p in ['zope.org redesign', 'Zope 3 manual',
    ...           'improved test coverage', 'Vault design and implementation']:
    ...     app[p] = projects[p] = Project(p)
    ...
    >>> companies = {}
    >>> for c in ['Ynod Corporation', 'HAL, Inc.', 'Zookd']:
    ...     app[c] = companies[c] = Company(c)
    ...

    >>> app['fredisprojectmanager'] = rel = SpecialRelationship(
    ...     (people['Fred'],), 'has the role of', (roles['Project Manager'],))
    >>> IContextAwareRelationship(rel).setContext(
    ...     projects['zope.org redesign'])
    >>> ix.index(rel)
    >>> transaction.commit()

Token conversion
================

Before we examine the searching features, we should quickly discuss the
tokenizing API on the index.  All search queries must use value tokens, and
search results can sometimes be value or relationship tokens.  Therefore
converting between tokens and real values can be important.  The index
provides a number of conversion methods for this purpose.

Arguably the most important is `tokenizeQuery`: it takes a query, in which
each key and value are the name of an indexed value and an actual value,
respectively; and returns a query in which the actual values have been
converted to tokens.  For instance, consider the following example.  It's a
bit hard to show the conversion reliably (we can't know what the intid tokens
will be, for instance) so we just show that the result's values are tokenized
versions of the inputs.

    >>> res = ix.tokenizeQuery(
    ...     {'objects': roles['Project Manager'],
    ...      'context': projects['zope.org redesign']})
    >>> res['objects'] == dump(roles['Project Manager'], ix, {})
    True
    >>> from zope.app.intid.interfaces import IIntIds
    >>> intids = component.getUtility(IIntIds, context=ix)
    >>> res['context'] == intids.getId(projects['zope.org redesign'])
    True

Tokenized queries can be resolved to values again using resolveQuery.

    >>> sorted(ix.resolveQuery(res).items()) # doctest: +NORMALIZE_WHITESPACE
    [('context', <Project 'zope.org redesign'>),
     ('objects', <Role 'Project Manager'>)]

Other useful conversions are `tokenizeValues`, which returns an iterable of
tokens for the values of the given index name;

    >>> examples = (people['Abe'], people['Bran'], people['Cathy'])
    >>> res = list(ix.tokenizeValues(examples, 'subjects'))
    >>> res == [dump(o, ix, {}) for o in examples]
    True

`resolveValueTokens`, which returns an iterable of values for the tokens of
the given index name;

    >>> list(ix.resolveValueTokens(res, 'subjects'))
    [<Person 'Abe'>, <Person 'Bran'>, <Person 'Cathy'>]

`tokenizeRelationship`, which returns a token for the given relationship;

    >>> res = ix.tokenizeRelationship(rel)
    >>> res == intids.getId(rel)
    True

`resolveRelationshipToken`, which returns a relationship for the given token;

    >>> ix.resolveRelationshipToken(res) is rel
    True

`tokenizeRelationships`, which returns an iterable of tokens for the relations
given; and

    >>> app['another_rel'] = another_rel = Relationship(
    ...     (companies['Ynod Corporation'],), 'commissioned',
    ...     (projects['Vault design and implementation'],))
    >>> res = list(ix.tokenizeRelationships((another_rel, rel)))
    >>> res == [intids.getId(r) for r in (another_rel, rel)]
    True

`resolveRelationshipTokens`, which returns an iterable of relations for the
tokens given.

    >>> list(ix.resolveRelationshipTokens(res)) == [another_rel, rel]
    True

Basic searching
===============

Now we move to the meat of the interface: searching.  The index interface
defines several searching methods:

- `findValues` and `findValueTokens` ask "to what is this related?";

- `findRelationshipChains` and `findRelationshipTokenChains` ask "how is this
  related?", especially for transitive searches;

- `isLinked` asks "does a relationship like this exist?";

- `findRelationshipTokenSet` asks "what are the intransitive relationships
  that match my query?" and is particularly useful for low-level usage of the
  index data structures;

- `findRelationships` asks the same question, but returns an iterable of
  relationships rather than a set of tokens;

- `findValueTokenSet` asks "what are the value tokens for this particular
  indexed name and this relationship token?" and is useful for low-level
  usage of the index data structures such as transitive query factories; and

- the standard zope.index method `apply` essentially exposes the
  `findRelationshipTokenSet` and `findValueTokens` methods via a query object
  spelling.

`findRelationshipChains` and `findRelationshipTokenChains` are paired methods,
doing the same work but with and without resolving the resulting tokens; and
`findValues` and `findValueTokens` are also paired in the same way.

It is very important to note that all queries must use tokens, not actual
objects.  As introduced above, the index provides a method to ease that
requirement, in the form of a `tokenizeQuery` method that converts a dict with
objects to a dict with tokens.  You'll see below that we shorten our calls by
stashing `tokenizeQuery` away in the 'q' name.

We have indexed our first example relationship--"Fred has the role of project
manager in the zope.org redesign"--so we can search for it.  We'll first look
at `findValues` and `findValueTokens`.  Here, we ask 'who has the role of
project manager in the zope.org redesign?'.  We do it first with findValues
and then with findTokenValues.

    >>> q = ix.tokenizeQuery
    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))
    [<Person 'Fred'>]

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']}))]
    [<Person 'Fred'>]

If we want to find all the relationships for which Fred is a subject, we can
use `findRelationshipTokenSet`.  It, combined with `findValueTokenSet`, is
useful for querying the index data structures at a fairly low level, when you
want to use the data in a way that the other search methods don't support.

`findRelationshipTokenSet`, given a single dictionary of {indexName: token},
returns a set (based on the btree family for relationships in the index) of
relationship tokens that match it, intransitively.

    >>> res = ix.findRelationshipTokenSet(q({'subjects': people['Fred']}))
    >>> res # doctest: +ELLIPSIS
    <BTrees._IFBTree.IFTreeSet object at ...>
    >>> [intids.getObject(t) for t in res]
    [<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>]

`findRelationships` does the same thing but with resolving the relationships.

    >>> list(ix.findRelationships(q({'subjects': people['Fred']})))
    [<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>]

`findValueTokenSet`, given a relationship token and a value name, returns a
set (based on the btree family for the value) of value tokens for that
relationship.

    >>> res = ix.findValueTokenSet(list(res)[0], 'subjects')
    >>> res # doctest: +ELLIPSIS
    <BTrees._IFBTree.IFTreeSet object at ...>
    >>> [load(t, ix, {}) for t in res]
    [<Person 'Fred'>]

The apply method, part of the zope.index.interfaces.IIndexSearch interface,
can essentially only duplicate the `findValueTokens` and
`findRelationshipTokenSet` search calls.  The only additional functionality
is that the results always are IFBTree sets: if the tokens requested are not
in an IFBTree set (on the basis of the 'btree' key during instantiation, for
instance) then the index raises a ValueError.  A wrapper dict specifies the
type of search with the key, and the value should be the arguments for the
search.

Here, we ask for the current known roles on the zope.org redesign.

    >>> res = ix.apply({'values':
    ...     {'resultName': 'objects', 'query':
    ...         q({'reltype': 'has the role of',
    ...            'context': projects['zope.org redesign']})}})
    >>> res # doctest: +ELLIPSIS
    IFSet([...])
    >>> [load(t, ix, {}) for t in res]
    [<Role 'Project Manager'>]

Ideally, this would fail, because the tokens, while integers, are not actually
mergable with a intid-based catalog results.  However, the index only complains
if it can tell that the returning set is not an IFTreeSet or IFSet.

Here, we ask for the relationships that have the 'has the role of' type.

    >>> res = ix.apply({'relationships':
    ...     q({'reltype': 'has the role of'})})
    ... doctest: +ELLIPSIS
    >>> res # doctest: +ELLIPSIS
    <BTrees._IFBTree.IFTreeSet object at ...>
    >>> [intids.getObject(t) for t in res]
    [<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>]

Here, we ask for the known relationships for the zope.org redesign.  It
will fail, because the result cannot be expressed as an IFBTree.IFTreeSet

    >>> res = ix.apply({'values':
    ...     {'resultName': 'reltype', 'query':
    ...         q({'context': projects['zope.org redesign']})}})
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: cannot fulfill `apply` interface because cannot return an
                IFBTree-based result

The last basic search methods, `isLinked`, `findRelationshipTokenChains`, and
`findRelationshipChains`, are most useful for transitive searches.  We
have not yet created any relationships that we can use transitively.  They
still will work with intransitive searches, so we will demonstrate them here
as an introduction, then discuss them more below when we introduce transitive
relationships.

`findRelationshipChains` and `findRelationshipTokenChains` let you find
transitive relationship paths. Right now a single relationship--a single
point--can't create much of a line. So first, here's a somewhat useless
example:

    >>> [[intids.getObject(t) for t in path] for path in
    ...  ix.findRelationshipTokenChains(
    ...     q({'reltype': 'has the role of'}))]
    ... # doctest: +NORMALIZE_WHITESPACE
    [[<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>]]

That's useless, because there's no chance of it being a transitive search, and
so you might as well use findRelationshipTokenSet.  This will become more
interesting later on.

Here's the same example with findRelationshipChains, which resolves the
relationship tokens itself.

    >>> list(ix.findRelationshipChains(q({'reltype': 'has the role of'})))
    ... # doctest: +NORMALIZE_WHITESPACE
    [(<(<Person 'Fred'>,) has the role of (<Role 'Project Manager'>,)>,)]

`isLinked` returns a boolean if there is at least one path that matches the
search--in fact, the implementation is essentially ::

    try:
        iter(ix.findRelationshipTokenChains(...args...)).next()
    except StopIteration:
        return False
    else:
        return True

So, we can say

    >>> ix.isLinked(q({'subjects': people['Fred']}))
    True
    >>> ix.isLinked(q({'subjects': people['Gary']}))
    False
    >>> ix.isLinked(q({'subjects': people['Fred'],
    ...                'reltype': 'manages'}))
    False

This is reasonably useful as is, to test basic assertions.  It also works with
transitive searches, as we will see below.


An even simpler example
-----------------------

(This was added to test that searching for a simple relationship works
even when the transitive query factory is not set.)

Let's create a very simple relation type, using strings as the source
and target types:

  >>> class IStringRelation(interface.Interface):
  ...     name = interface.Attribute("The name of the value.")
  ...     value = interface.Attribute("The value associated with the name.")

  >>> class StringRelation(persistent.Persistent, Contained):
  ...     interface.implements(IStringRelation)
  ...
  ...     def __init__(self, name, value):
  ...         self.name = name
  ...         self.value = value

  >>> app[u"string-relation-1"] = StringRelation("name1", "value1")
  >>> app[u"string-relation-2"] = StringRelation("name2", "value2")

  >>> transaction.commit()

We can now create an index that uses these:

  >>> from BTrees import OOBTree

  >>> sx = index.Index(
  ...     ({"element": IStringRelation["name"],
  ...       "load": None, "dump": None, "btree": OOBTree},
  ...      {"element": IStringRelation["value"],
  ...       "load": None, "dump": None, "btree": OOBTree},
  ...      ))

  >>> app["sx"] = sx
  >>> transaction.commit()

And we'll add the relations to the index:

  >>> app["sx"].index(app["string-relation-1"])
  >>> app["sx"].index(app["string-relation-2"])

Getting a relationship back out should be very simple.  Let's look for
all the values associates with "name1":

  >>> query = sx.tokenizeQuery({"name": "name1"})
  >>> list(sx.findValues("value", query))
  ['value1']



Searching for empty sets
------------------------

We've examined the most basic search capabilities.  One other feature of the
index and search is that one can search for relationships to an empty set, or,
for single-value relationships like 'reltype' and 'context' in our
examples, None.

Let's add a relationship with a 'manages' relationshiptype, and no context; and
a relationship with a 'commissioned' relationship type, and a company context.

Notice that there are two ways of adding indexes, by the way.  We have already
seen that the index has an 'index' method that takes a relationship.  Here we
use 'index_doc' which is a method defined in zope.index.interfaces.IInjection
that requires the token to already be generated.  Since we are using intids
to tokenize the relationships, we must add them to the ZODB app object to give
them the possibility of a connection.

    >>> app['abeAndBran'] = rel = Relationship(
    ...     (people['Abe'],), 'manages', (people['Bran'],))
    >>> ix.index_doc(intids.register(rel), rel)
    >>> app['abeAndVault'] = rel = SpecialRelationship(
    ...     (people['Abe'],), 'commissioned',
    ...     (projects['Vault design and implementation'],))
    >>> IContextAwareRelationship(rel).setContext(companies['Zookd'])
    >>> ix.index_doc(intids.register(rel), rel)

Now we can search for Abe's relationship that does not have a context.  The
None value is always used to match both an empty set and a single `None` value.
The index does not support any other "empty" values at this time.

    >>> sorted(
    ...     repr(load(t, ix, {})) for t in ix.findValueTokens(
    ...         'objects',
    ...         q({'subjects': people['Abe']})))
    ["<Person 'Bran'>", "<Project 'Vault design and implementation'>"]
    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects', q({'subjects': people['Abe'], 'context': None}))]
    [<Person 'Bran'>]
    >>> sorted(
    ...     repr(v) for v in ix.findValues(
    ...         'objects',
    ...         q({'subjects': people['Abe']})))
    ["<Person 'Bran'>", "<Project 'Vault design and implementation'>"]
    >>> list(ix.findValues(
    ...     'objects', q({'subjects': people['Abe'], 'context': None})))
    [<Person 'Bran'>]

Note that the index does not currently support searching for relationships that
have any value, or one of a set of values.  This may be added at a later date;
the spelling for such queries are among the more troublesome parts.

Working with transitive searches
================================

It's possible to do transitive searches as well.  This can let you find all
transitive bosses, or transitive subordinates, in our 'manages' relationship
type.  Let's set up some example relationships.  Using letters to represent our
people, we'll create three hierarchies like this::

        A        JK           R
       / \      /  \
      B   C    LM   NOP     S T U
     / \  |     |          /| |  \
    D  E  F     Q         V W X   |
    |     |                    \--Y
    H     G                       |
    |                             Z
    I

This means that, for instance, person "A" ("Abe") manages "B" ("Bran") and "C"
("Cathy").

We already have a relationship from Abe to Bran, so we'll only be adding the
rest.

    >>> relmap = (
    ...     ('A', 'C'), ('B', 'D'), ('B', 'E'), ('C', 'F'),
    ...     ('F', 'G'), ('D', 'H'), ('H', 'I'), ('JK', 'LM'), ('JK', 'NOP'),
    ...     ('LM', 'Q'), ('R', 'STU'), ('S', 'VW'), ('T', 'X'), ('UX', 'Y'),
    ...     ('Y', 'Z'))
    >>> letters = dict((name[0], ob) for name, ob in people.items())
    >>> for subs, obs in relmap:
    ...     subs = tuple(letters[l] for l in subs)
    ...     obs = tuple(letters[l] for l in obs)
    ...     app['%sManages%s' % (''.join(o.name for o in subs),
    ...                          ''.join(o.name for o in obs))] = rel = (
    ...         Relationship(subs, 'manages', obs))
    ...     ix.index(rel)
    ...

Now we can do both transitive and intransitive searches.  Here are a few
examples.

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'objects': people['Ingrid'],
    ...        'reltype': 'manages'}))
    ...     ]
    [<Person 'Heather'>, <Person 'David'>, <Person 'Bran'>, <Person 'Abe'>]

Here's the same thing using findValues.

    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'objects': people['Ingrid'],
    ...        'reltype': 'manages'})))
    [<Person 'Heather'>, <Person 'David'>, <Person 'Bran'>, <Person 'Abe'>]

Notice that they are in order, walking away from the search start.  It also
is breadth-first--for instance, look at the list of superiors to Zane: Xen and
Uther come before Rob and Terry.

    >>> res = list(ix.findValues(
    ...     'subjects',
    ...     q({'objects': people['Zane'], 'reltype': 'manages'})))
    >>> res[0]
    <Person 'Ygritte'>
    >>> sorted(repr(p) for p in res[1:3])
    ["<Person 'Uther'>", "<Person 'Xen'>"]
    >>> sorted(repr(p) for p in res[3:])
    ["<Person 'Rob'>", "<Person 'Terry'>"]

Notice that all the elements of the search are maintained as it is walked--only
the transposed values are changed, and the rest remain statically.  For
instance, notice the difference between these two results.

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects',
    ...     q({'subjects': people['Cathy'], 'reltype': 'manages'}))]
    [<Person 'Fred'>, <Person 'Gary'>]
    >>> res = [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects',
    ...     q({'subjects': people['Cathy']}))]
    >>> res[0]
    <Person 'Fred'>
    >>> sorted(repr(i) for i in res[1:])
    ["<Person 'Gary'>", "<Role 'Project Manager'>"]

The first search got what we expected for our management relationshiptype--
walking from Cathy, the relationshiptype was maintained, and we only got the
Gary subordinate.  The second search didn't specify the relationshiptype, so
the transitive search included the Role we added first (Fred has the role of
Project Manager for the zope.org redesign).

The `maxDepth` argument allows control over how far to search.  For instance,
if we only want to search for Bran's subordinates a maximum of two steps deep,
we can do so:

    >>> res = [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects',
    ...     q({'subjects': people['Bran']}),
    ...     maxDepth=2)]
    >>> sorted(repr(i) for i in res)
    ["<Person 'David'>", "<Person 'Emily'>", "<Person 'Heather'>"]

The same is true for findValues.

    >>> res = list(ix.findValues(
    ...     'objects',
    ...     q({'subjects': people['Bran']}), maxDepth=2))
    >>> sorted(repr(i) for i in res)
    ["<Person 'David'>", "<Person 'Emily'>", "<Person 'Heather'>"]

A minimum depth--a number of relationships that must be traversed before
results are desired--can also be achieved trivially using the targetFilter
argument described soon below.  For now, we will continue in the order of the
arguments list, so `filter` is up next.

The `filter` argument takes an object (such as a function) that provides
interfaces.IFilter.  As the interface lists, it receives the current chain
of relationship tokens ("relchain"), the original query that started the search
("query"), the index object ("index"), and a dictionary that will be used
throughout the search and then discarded that can be used for optimizations
("cache").  It should return a boolean, which determines whether the given
relchain should be used at all--traversed or returned.  For instance, if
security dictates that the current user can only see certain relationships,
the filter could be used to make only the available relationships traversable.
Other uses are only getting relationships that were created after a given time,
or that have some annotation (available after resolving the token).

Let's look at an example of a filter that only allows relationships in a given
set, the way a security-based filter might work.  We'll then use it to model
a situation in which the current user can't see that Ygritte is managed by
Uther, in addition to Xen.

    >>> s = set(intids.getId(r) for r in app.values()
    ...         if IRelationship.providedBy(r))
    >>> relset = list(
    ...     ix.findRelationshipTokenSet(q({'subjects': people['Xen']})))
    >>> len(relset)
    1
    >>> s.remove(relset[0])
    >>> dump(people['Uther'], ix, {}) in list(
    ...     ix.findValueTokens('subjects', q({'objects': people['Ygritte']})))
    True
    >>> dump(people['Uther'], ix, {}) in list(ix.findValueTokens(
    ...     'subjects', q({'objects': people['Ygritte']}),
    ...     filter=lambda relchain, query, index, cache: relchain[-1] in s))
    False
    >>> people['Uther'] in list(
    ...     ix.findValues('subjects', q({'objects': people['Ygritte']})))
    True
    >>> people['Uther'] in list(ix.findValues(
    ...     'subjects', q({'objects': people['Ygritte']}),
    ...     filter=lambda relchain, query, index, cache: relchain[-1] in s))
    False

The next two search arguments are the targetQuery and the targetFilter.  They
both are filters on the output of the search methods, while not affecting the
traversal/search process.  The targetQuery takes a query identical to the main
query, and the targetFilter takes an IFilter identical to the one used by the
`filter` argument.  The targetFilter can do all of the work of the targetQuery,
but the targetQuery makes a common case--wanting to find the paths between two
objects, or if two objects are linked at all, for instance--convenient.

We'll skip over targetQuery for a moment (we'll return when we revisit
`findRelationshipChains` and `isLinked`), and look at targetFilter.
targetFilter can be used for many tasks, such as only returning values that
are in specially annotated relationships, or only returning values that have
traversed a certain hinge relationship in a two-part search, or other tasks.
A very simply one, though, is to effectively specify a minimum traversal depth.
Here, we find the people who are precisely two steps down from Bran, no more
and no less.  We do it twice, once with findValueTokens and once with
findValues.

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'objects', q({'subjects': people['Bran']}), maxDepth=2,
    ...     targetFilter=lambda relchain, q, i, c: len(relchain)>=2)]
    [<Person 'Heather'>]
    >>> list(ix.findValues(
    ...     'objects', q({'subjects': people['Bran']}), maxDepth=2,
    ...     targetFilter=lambda relchain, q, i, c: len(relchain)>=2))
    [<Person 'Heather'>]

Heather is the only person precisely two steps down from Bran.

Notice that we specified both maxDepth and targetFilter.  We could have
received the same output by specifying a targetFilter of `len(relchain)==2`
and no maxDepth, but there is an important difference in efficiency.  maxDepth
and filter can reduce the amount of work done by the index because they can
stop searching after reaching the maxDepth, or failing the filter; the
targetFilter and targetQuery arguments simply hide the results obtained, which
can reduce a bit of work in the case of getValues but generally don't reduce
any of the traversal work.

The last argument to the search methods is `transitiveQueriesFactory`.  It is
a powertool that replaces the index's default traversal factory for the
duration of the search.  This allows custom traversal for individual searches,
and can support a number of advanced use cases.  For instance, our index
assumes that you want to traverse objects and sources, and that the context
should be constant; that may not always be the desired traversal behavior.  If
we had a relationship of PERSON1 TAUGHT PERSON2 (the lessons of PERSON3) then
to find the teachers of any given person you might want to traverse PERSON1,
but sometimes you might want to traverse PERSON3 as well.  You can change the
behavior by providing a different factory.

To show this example we will need to add a few more relationships.  We will say
that Mary teaches Rob the lessons of Abe; Olaf teaches Zane the lessons of
Bran; Cathy teaches Bran the lessons of Lee; David teaches Abe the lessons of
Zane; and Emily teaches Mary the lessons of Ygritte.

In the diagram, left-hand lines indicate "taught" and right-hand lines indicate
"the lessons of", so ::

  E   Y
   \ /
    M

should be read as "Emily taught Mary the lessons of Ygritte".  Here's the full
diagram::

            C   L
             \ /
          O   B
           \ /
  E   Y D   Z
   \ /   \ /
    M     A
     \   /
      \ /
       R

You can see then that the transitive path of Rob's teachers is Mary and Emily,
but the transitive path of Rob's lessons is Abe, Zane, Bran, and Lee.

Transitive queries factories must do extra work when the transitive walk is
across token types.  We have used the TransposingTransitiveQueriesFactory to
build our transposers before, but now we need to write a custom one that
translates the tokens (ooh!  a
TokenTranslatingTransposingTransitiveQueriesFactory!  ...maybe we won't go that
far...).

We will add the relationships, build the custom transitive factory, and then
again do the search work twice, once with findValueTokens and once with
findValues.

    >>> for triple in ('EMY', 'MRA', 'DAZ', 'OZB', 'CBL'):
    ...     teacher, student, source = (letters[l] for l in triple)
    ...     rel = SpecialRelationship((teacher,), 'taught', (student,))
    ...     app['%sTaught%sTo%s' % (
    ...         teacher.name, source.name, student.name)] = rel
    ...     IContextAwareRelationship(rel).setContext(source)
    ...     ix.index_doc(intids.register(rel), rel)
    ...

    >>> def transitiveFactory(relchain, query, index, cache):
    ...     dynamic = cache.get('dynamic')
    ...     if dynamic is None:
    ...         intids = cache['intids'] = component.getUtility(
    ...             IIntIds, context=index)
    ...         static = cache['static'] = {}
    ...         dynamic = cache['dynamic'] = []
    ...         names = ['objects', 'context']
    ...         for nm, val in query.items():
    ...             try:
    ...                 ix = names.index(nm)
    ...             except ValueError:
    ...                 static[nm] = val
    ...             else:
    ...                 if dynamic:
    ...                     # both were specified: no transitive search known.
    ...                     del dynamic[:]
    ...                     cache['intids'] = False
    ...                     break
    ...                 else:
    ...                     dynamic.append(nm)
    ...                     dynamic.append(names[not ix])
    ...         else:
    ...             intids = component.getUtility(IIntIds, context=index)
    ...             if dynamic[0] == 'objects':
    ...                 def translate(t):
    ...                     return dump(intids.getObject(t), index, cache)
    ...             else:
    ...                 def translate(t):
    ...                     return intids.register(load(t, index, cache))
    ...             cache['translate'] = translate
    ...     else:
    ...         static = cache['static']
    ...         translate = cache['translate']
    ...     if dynamic:
    ...         for r in index.findValueTokenSet(relchain[-1], dynamic[1]):
    ...             res = {dynamic[0]: translate(r)}
    ...             res.update(static)
    ...             yield res

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'objects': people['Rob'], 'reltype': 'taught'}))]
    [<Person 'Mary'>, <Person 'Emily'>]
    >>> [intids.getObject(t) for t in ix.findValueTokens(
    ...     'context',
    ...     q({'objects': people['Rob'], 'reltype': 'taught'}),
    ...     transitiveQueriesFactory=transitiveFactory)]
    [<Person 'Abe'>, <Person 'Zane'>, <Person 'Bran'>, <Person 'Lee'>]

    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'objects': people['Rob'], 'reltype': 'taught'})))
    [<Person 'Mary'>, <Person 'Emily'>]
    >>> list(ix.findValues(
    ...     'context',
    ...     q({'objects': people['Rob'], 'reltype': 'taught'}),
    ...     transitiveQueriesFactory=transitiveFactory))
    [<Person 'Abe'>, <Person 'Zane'>, <Person 'Bran'>, <Person 'Lee'>]

transitiveQueryFactories can be very powerful, and we aren't finished talking
about them in this document: see "Transitively mapping multiple elements"
below.

We have now discussed, or at least mentioned, all of the available search
arguments.  The `apply` method's 'values' search has the same arguments and
features as `findValues`, so it can also do these transitive tricks.  Let's
get all of Karyn's subordinates.

    >>> res = ix.apply({'values':
    ...     {'resultName': 'objects', 'query':
    ...         q({'reltype': 'manages',
    ...           'subjects': people['Karyn']})}})
    >>> res # doctest: +ELLIPSIS
    IFSet([...])
    >>> sorted(repr(load(t, ix, {})) for t in res)
    ... # doctest: +NORMALIZE_WHITESPACE
    ["<Person 'Lee'>", "<Person 'Mary'>", "<Person 'Nancy'>",
     "<Person 'Olaf'>", "<Person 'Perry'>", "<Person 'Quince'>"]

As we return to `findRelationshipChains` and `findRelationshipTokenChains`, we
also return to the search argument we postponed above: targetQuery.

The `findRelationshipChains` and `findRelationshipTokenChains` can simply find
all paths:

    >>> res = [repr([intids.getObject(t) for t in path]) for path in
    ...  ix.findRelationshipTokenChains(
    ...     q({'reltype': 'manages', 'subjects': people['Jim']}
    ...     ))]
    >>> len(res)
    3
    >>> sorted(res[:2]) # doctest: +NORMALIZE_WHITESPACE
    ["[<(<Person 'Jim'>, <Person 'Karyn'>) manages
        (<Person 'Lee'>, <Person 'Mary'>)>]",
     "[<(<Person 'Jim'>, <Person 'Karyn'>) manages
        (<Person 'Nancy'>, <Person 'Olaf'>, <Person 'Perry'>)>]"]
    >>> res[2] # doctest: +NORMALIZE_WHITESPACE
    "[<(<Person 'Jim'>, <Person 'Karyn'>) manages
       (<Person 'Lee'>, <Person 'Mary'>)>,
      <(<Person 'Lee'>, <Person 'Mary'>) manages
       (<Person 'Quince'>,)>]"
    >>> res == [repr(list(p)) for p in
    ...  ix.findRelationshipChains(
    ...     q({'reltype': 'manages', 'subjects': people['Jim']}
    ...     ))]
    True

Like `findValues`, this is a breadth-first search.

If we use a targetQuery with `findRelationshipChains`, you can find all paths
between two searches. For instance, consider the paths between Rob and
Ygritte.  While a `findValues` search would only include Rob once if asked to
search for supervisors, there are two paths.  These can be found with the
targetSearch.

    >>> res = [repr([intids.getObject(t) for t in path]) for path in
    ...  ix.findRelationshipTokenChains(
    ...     q({'reltype': 'manages', 'subjects': people['Rob']}),
    ...     targetQuery=q({'objects': people['Ygritte']}))]
    >>> len(res)
    2
    >>> sorted(res[:2]) # doctest: +NORMALIZE_WHITESPACE
    ["[<(<Person 'Rob'>,) manages
        (<Person 'Sam'>, <Person 'Terry'>, <Person 'Uther'>)>,
       <(<Person 'Terry'>,) manages (<Person 'Xen'>,)>,
       <(<Person 'Uther'>, <Person 'Xen'>) manages (<Person 'Ygritte'>,)>]",
     "[<(<Person 'Rob'>,) manages
        (<Person 'Sam'>, <Person 'Terry'>, <Person 'Uther'>)>,
       <(<Person 'Uther'>, <Person 'Xen'>) manages (<Person 'Ygritte'>,)>]"]

Here's a query with no results:

    >>> len(list(ix.findRelationshipTokenChains(
    ...     q({'reltype': 'manages', 'subjects': people['Rob']}),
    ...     targetQuery=q({'objects': companies['Zookd']}))))
    0

`isLinked` takes the same arguments as all of the other transitive-aware
methods.  For instance, Rob and Ygritte are transitively linked, but Abe and
Zane are not.

    >>> ix.isLinked(
    ...     q({'reltype': 'manages', 'subjects': people['Rob']}),
    ...     targetQuery=q({'objects': people['Ygritte']}))
    True
    >>> ix.isLinked(
    ...     q({'reltype': 'manages', 'subjects': people['Abe']}),
    ...     targetQuery=q({'objects': people['Ygritte']}))
    False

Detecting cycles
----------------

Suppose we're modeling a 'king in disguise': someone high up in management also
works as a peon to see how his employees' lives are.  We could model this a
number of ways that might make more sense than what we'll do now, but to show
cycles at work we'll just add an additional relationship so that Abe works for
Gary.  That means that the very longest path from Ingrid up gets a lot longer--
in theory, it's infinitely long, because of the cycle.

The index keeps track of this and stops right when the cycle happens, and right
before the cycle duplicates any relationships.  It marks the chain that has
cycle as a special kind of tuple that implements ICircularRelationshipPath.
The tuple has a 'cycled' attribute that contains the one or more searches
that would be equivalent to following the cycle (given the same transitiveMap).

Let's actually look at the example we described.

    >>> res = list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'], 'reltype': 'manages'})))
    >>> len(res)
    4
    >>> len(res[3])
    4
    >>> interfaces.ICircularRelationshipPath.providedBy(res[3])
    False
    >>> rel = Relationship(
    ...     (people['Gary'],), 'manages', (people['Abe'],))
    >>> app['GaryManagesAbe'] = rel
    >>> ix.index(rel)
    >>> res = list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'], 'reltype': 'manages'})))
    >>> len(res)
    8
    >>> len(res[7])
    8
    >>> interfaces.ICircularRelationshipPath.providedBy(res[7])
    True
    >>> [sorted(
    ...     (nm, nm == 'objects' and load(t, ix, {}) or t)
    ...     for nm, t in search.items()) for search in res[7].cycled]
    ... # doctest: +NORMALIZE_WHITESPACE
    [[('objects', <Person 'Abe'>),
      ('reltype', 'manages')]]

Notice that there is nothing special about the new relationship, by the way.
If we had started to look for Fred's supervisors, the cycle marker would have
been given for the relationship that points back to Fred as a supervisor to
himself.  There's no way for the computer to know which is the "cause" without
further help and policy.

Handling cycles can be tricky.  Now imagine that we have a cycle that involves
a relationship with two objects, only one of which causes the cycle.  The other
object should continue to be followed.

For instance, lets have Q manage L and Y.  The link to L will be a cycle, but
the link to Y is not, and should be followed.  This means that only the middle
relationship chain will be marked as a cycle.

    >>> rel = Relationship((people['Quince'],), 'manages',
    ...                    (people['Lee'], people['Ygritte']))
    >>> app['QuinceManagesLeeYgritte'] = rel
    >>> ix.index_doc(intids.register(rel), rel)
    >>> res = [p for p in ix.findRelationshipTokenChains(
    ...     q({'reltype': 'manages', 'subjects': people['Mary']}))]
    >>> [interfaces.ICircularRelationshipPath.providedBy(p) for p in res]
    [False, True, False]
    >>> [[intids.getObject(t) for t in p] for p in res]
    ... # doctest: +NORMALIZE_WHITESPACE
    [[<(<Person 'Lee'>, <Person 'Mary'>) manages (<Person 'Quince'>,)>],
     [<(<Person 'Lee'>, <Person 'Mary'>) manages (<Person 'Quince'>,)>,
      <(<Person 'Quince'>,) manages (<Person 'Lee'>, <Person 'Ygritte'>)>],
     [<(<Person 'Lee'>, <Person 'Mary'>) manages (<Person 'Quince'>,)>,
      <(<Person 'Quince'>,) manages (<Person 'Lee'>, <Person 'Ygritte'>)>,
      <(<Person 'Ygritte'>,) manages (<Person 'Zane'>,)>]]
    >>> [sorted(
    ...     (nm, nm == 'reltype' and t or load(t, ix, {}))
    ...     for nm, t in search.items()) for search in res[1].cycled]
    [[('reltype', 'manages'), ('subjects', <Person 'Lee'>)]]

Transitively mapping multiple elements
--------------------------------------

Transitive searches can do whatever searches the transitiveQueriesFactory
returns, which means that complex transitive behavior can be modeled.  For
instance, imagine genealogical relationships.  Let's say the basic
relationship is "MALE and FEMALE had CHILDREN".  Walking transitively to get
ancestors or descendants would need to distinguish between male children and
female children in order to correctly generate the transitive search.  This
could be accomplished by resolving each child token and examining the object
or, probably more efficiently, getting an indexed collection of males and
females (and cacheing it in the cache dictionary for further transitive steps)
and checking the gender by membership in the indexed collections.  Either of
these approaches could be performed by a transitiveQueriesFactory.  A full
example is left as an exercise to the reader.

Lies, damn lies, and statistics
===============================

The zope.index.interfaces.IStatistics methods are implemented to provide
minimal introspectability.  wordCount always returns 0, because words are
irrelevant to this kind of index.  documentCount returns the number of
relationships indexed.

    >>> ix.wordCount()
    0
    >>> ix.documentCount()
    25

Reindexing and removing relationships
=====================================

Using an index over an application's lifecycle usually requires changes to the
indexed objects.  As per the zope.index interfaces, `index_doc` can reindex
relationships, `unindex_doc` can remove them, and `clear` can clear the entire
index.

Here we change the zope.org project manager from Fred to Emily.

    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']}))]
    [<Person 'Fred'>]
    >>> rel = intids.getObject(list(ix.findRelationshipTokenSet(
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))[0])
    >>> rel.subjects = (people['Emily'],)
    >>> ix.index_doc(intids.register(rel), rel)
    >>> q = ix.tokenizeQuery
    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']}))]
    [<Person 'Emily'>]

Here we remove the relationship that made a cycle for Abe in the 'king in
disguise' scenario.

    >>> res = list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'],
    ...        'reltype': 'manages'})))
    >>> len(res)
    8
    >>> len(res[7])
    8
    >>> interfaces.ICircularRelationshipPath.providedBy(res[7])
    True
    >>> rel = intids.getObject(list(ix.findRelationshipTokenSet(
    ...     q({'subjects': people['Gary'], 'reltype': 'manages',
    ...        'objects': people['Abe']})))[0])
    >>> ix.unindex(rel) # == ix.unindex_doc(intids.getId(rel))
    >>> ix.documentCount()
    24
    >>> res = list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'], 'reltype': 'manages'})))
    >>> len(res)
    4
    >>> len(res[3])
    4
    >>> interfaces.ICircularRelationshipPath.providedBy(res[3])
    False

Finally we clear out the whole index.

    >>> ix.clear()
    >>> ix.documentCount()
    0
    >>> list(ix.findRelationshipTokenChains(
    ...     q({'objects': people['Ingrid'], 'reltype': 'manages'})))
    []
    >>> [load(t, ix, {}) for t in ix.findValueTokens(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']}))]
    []

Optimizing relationship index use
=================================

There are three optimization opportunities built into the index.

- use the cache to load and dump tokens;

- don't load or dump tokens (the values themselves may be used as tokens); and

- have the returned value be of the same btree family as the result family.

For some operations, particularly with hundreds or thousands of members in a
single relationship value, some of these optimizations can speed up some
common-case reindexing work by around 100 times.

The easiest (and perhaps least useful) optimization is that all dump
calls and all load calls generated by a single operation share a cache
dictionary per call type (dump/load), per indexed relationship value.
Therefore, for instance, we could stash an intids utility, so that we
only had to do a utility lookup once, and thereafter it was only a
single dictionary lookup. This is what the default `generateToken` and
`resolveToken` functions in index.py do: look at them for an example.

A further optimization is to not load or dump tokens at all, but use values
that may be tokens.  This will be particularly useful if the tokens have
__cmp__ (or equivalent) in C, such as built-in types like ints.  To specify
this behavior, you create an index with the 'load' and 'dump' values for the
indexed attribute descriptions explicitly set to None.

    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True,
    ...       'dump': None, 'load': None},
    ...      {'element': IRelationship['relationshiptype'],
    ...       'dump': relTypeDump, 'load': relTypeLoad, 'btree': OIBTree,
    ...       'name': 'reltype'},
    ...      {'element': IRelationship['objects'], 'multiple': True,
    ...       'dump': None, 'load': None},
    ...      {'element': IContextAwareRelationship['getContext'],
    ...       'name': 'context'}),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    ...
    >>> sm['rel_index_2'] = ix
    >>> app['ex_rel_1'] = rel = Relationship((1,), 'has the role of', (2,))
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 1}))
    [2]

Finally, if you have single relationships that relate hundreds or thousands
of objects, it can be a huge win if the value is a 'multiple' of the same type
as the stored BTree for the given attribute.  The default BTree family for
attributes is IFBTree; IOBTree is also a good choice, and may be preferrable
for some applications.

    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True,
    ...       'dump': None, 'load': None},
    ...      {'element': IRelationship['relationshiptype'],
    ...       'dump': relTypeDump, 'load': relTypeLoad, 'btree': OIBTree,
    ...       'name': 'reltype'},
    ...      {'element': IRelationship['objects'], 'multiple': True,
    ...       'dump': None, 'load': None},
    ...      {'element': IContextAwareRelationship['getContext'],
    ...       'name': 'context'}),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    ...
    >>> sm['rel_index_3'] = ix
    >>> from BTrees import IFBTree
    >>> app['ex_rel_2'] = rel = Relationship(
    ...     IFBTree.IFTreeSet((1,)), 'has the role of', IFBTree.IFTreeSet((2,)))
    >>> ix.index(rel)
    >>> list(ix.findValueTokens('objects', {'subjects': 1}))
    [2]

Remember that BTrees (not just BTreeSets) can be used for these values: the keys
are used as the values in that case.

__contains__ and Unindexing
=============================

You can test whether a relationship is in an index with __contains__.  Note
that this uses the actual relationship, not the relationship token.

    >>> ix = index.Index(
    ...     ({'element': IRelationship['subjects'], 'multiple': True,
    ...       'dump': dump, 'load': load},
    ...      {'element': IRelationship['relationshiptype'],
    ...       'dump': relTypeDump, 'load': relTypeLoad, 'btree': OIBTree,
    ...       'name': 'reltype'},
    ...      {'element': IRelationship['objects'], 'multiple': True,
    ...       'dump': dump, 'load': load},
    ...      {'element': IContextAwareRelationship['getContext'],
    ...       'name': 'context'}),
    ...     index.TransposingTransitiveQueriesFactory('subjects', 'objects'))
    >>> ix.documentCount()
    0
    >>> app['fredisprojectmanager'].subjects = (people['Fred'],)
    >>> ix.index(app['fredisprojectmanager'])
    >>> ix.index(app['another_rel'])
    >>> ix.documentCount()
    2
    >>> app['fredisprojectmanager'] in ix
    True
    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))
    [<Person 'Fred'>]

    >>> app['another_rel'] in ix
    True

    >>> app['abeAndBran'] in ix
    False

As noted, you can unindex using unindex(relationship) or
unindex_doc(relationship token).

    >>> ix.unindex_doc(ix.tokenizeRelationship(app['fredisprojectmanager']))
    >>> app['fredisprojectmanager'] in ix
    False
    >>> list(ix.findValues(
    ...     'subjects',
    ...     q({'reltype': 'has the role of',
    ...       'objects': roles['Project Manager'],
    ...       'context': projects['zope.org redesign']})))
    []

    >>> ix.unindex(app['another_rel'])
    >>> app['another_rel'] in ix
    False

As defined by zope.index.interfaces.IInjection, if the relationship is
not in the index then calling unindex_doc is a no-op; the same holds
true for unindex.

    >>> ix.unindex(app['abeAndBran'])
    >>> ix.unindex_doc(ix.tokenizeRelationship(app['abeAndBran']))
