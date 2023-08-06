=================================================
collective.traverser - object lookup by interface
=================================================

------------
Introduction
------------

This product provides a utility that returns a object which provides
a given interface. The returned object could be the given object or
any object down the path towards the root.

  >>> from collective.traverse.interfaces import ITraverse
  >>> from somewhere import IMyInterface
  >>> root_traverser = getUtility(ITraverse, name="rootTraverser")
  >>> myType = root_traverser(self.context, IMyInterface)


------------
Installation
------------

Add this to your buildout:

    [buildout]
        eggs = collective.traverse

    [instance]
        zcml = collective.traverse

And then run buildout.


