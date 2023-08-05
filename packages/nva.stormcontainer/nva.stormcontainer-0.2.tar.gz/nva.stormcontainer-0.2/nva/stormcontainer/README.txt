Introduction
------------

This packages helps you to use Storm with Zope.
The stormcontainer act s like a normal container
the main difference of course is that this container
get its data from an RDBMS.

Many thanks to the zalchemy product and storm, 
because stormcontainer is inspired by these products.

The first part of this doctest is from the storm.zope package.
It´s the basic setup to work wih zope.storm.
 
The storm.zope package contains the ZStorm utility which provides
seamless integration between Storm and Zope 3's transaction system.
Setting up ZStorm is quite easy.  In most cases, you want to include
storm/zope/configure.zcml in your application.  For the purposes of
this doctest we'll register ZStorm manually.
	
  >>> from zope.component import provideUtility, getUtility
  >>> import transaction
  >>> from storm.zope.interfaces import IZStorm
  >>> from storm.zope.zstorm import global_zstorm

  >>> provideUtility(global_zstorm, IZStorm)
  >>> zstorm = getUtility(IZStorm)
  >>> zstorm
  <storm.zope.zstorm.ZStorm object at ...>


Getting stores
--------------

The ZStorm utility allows us work with named stores.

  >>> zstorm.set_default_uri("test", "sqlite:")

Setting a default URI for stores isn't strictly required.  We could
pass it as the second argument to zstorm.get.  Providing a default URI
makes it possible to use zstorm.get more easily; this is especially
handy when multiple threads are used as we'll see further on.

  >>> store = zstorm.get("test")
  >>> store
  <storm.store.Store object at ...>

ZStorm has automatically created a store instance for us.  If we ask
for a store by name again, we should get the same instance.

  >>> same_store = zstorm.get("test")
  >>> same_store is store
  True

The stores provided by ZStorm are per-thread.  If we ask for the named
store in a different thread we should get a different instance.


Creating a Example DB
---------------------

  >>> result = store.execute("""
  ...     CREATE TABLE person (
  ...         id INTEGER PRIMARY KEY,
  ...         name TEXT)
  ... """)
  >>> store.commit()

We'll need a Person class to use with this database.

  >>> from storm.locals import Storm, Int, Unicode

  >>> class Person(Storm):
  ...
  ...     __storm_table__ = "person"
  ...
  ...     id = Int(primary=True)
  ...     name = Unicode()
  ...

Great!  Let's try it out.

Lets create a StormContainer
----------------------------

We create now a container which holds the Person objects.
This objects should be automatically go into our DB.

   >>> from nva.stormcontainer import StormContainer
   >>> from nva.stormcontainer.interfaces import IStormContainer
   >>> container = StormContainer()
   >>> container
   <nva.stormcontainer.container.StormContainer object at ...>

I have to use a seperate *helper* class for Person to make
sure that the class could be resolved.

   >>> container.setClassName('nva.stormcontainer.tests.test_doctests.Person')
   >>> container.getClassName()
   'nva.stormcontainer.tests.test_doctests.Person'

Test the name of the store utility

   >>> container.setStoreUtilityName('test')
   >>> container.getStoreUtilityName()
   'test'

Check the contents of the container. As we have nothing
saved yet. There should be no objects in our container.

   >>> len(container)
   0

Let s create some Persons
--------------------------

   >>> joe = Person()
   >>> joe.id = 1
   >>> joe.name = u"Joe Frazier"
   >>> joe
   <Person object at ...>

Save joe into the Container

It doesn not matter what id pass as name for the object,
because the container saves the object to database.

   >>> container['id'] = joe
   >>> transaction.commit()

The length of the container should be 1.

   >>> len(container)
   1

We should have a generator for items.

   >>> container.items()
   <generator object at ...>


We can iterate over the items

   >>> [item.id for key, item in container.items()]
   [1]

We can iterate over the keys. The second suffix after the -
is not nice. Maybe i will find a better solution for this.

   >>> [key for key in container.keys()] 
   ['Person-aW50OjE7']

We can delete the object.

   >>> del(container['Person-aW50OjE7'])

And the length of the container should be 0 again.

   >>> len(container)
   0
