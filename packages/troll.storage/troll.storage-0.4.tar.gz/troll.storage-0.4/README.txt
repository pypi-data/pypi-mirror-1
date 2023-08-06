======================
What is troll.storage?
======================

The ``troll.storage`` package provides an abstract approach for the
storage problematics. It defines a simple, yet exhaustive, api to deal
with all kind of storage.

It provides :

- A clear API as interfaces

- A base class adapter that provides a basic implementation.

- A demonstrative, yet functional, annotation descriptor, to handle
  annotation storages. 


=================
How does it work?
=================

The system uses the basic zope3 components system to be flexible and
pluggable. There are 3 main parts :

- the Handler : the straightforward API to store, retrieve and
  delete. It's implemented as an adapter.

- the Storage : a storage object that implements IStorage. It can be a
  zope container or a layer to write in a relational database.

- the Stored Item : a very lightly contrained object that is to be
  stored in Storage.


==========
Learn more
==========

Nothing is like code reading to understand how to use it and why to
use it. I recommand you read the tests. They demonstrate all the basic
usecases.
