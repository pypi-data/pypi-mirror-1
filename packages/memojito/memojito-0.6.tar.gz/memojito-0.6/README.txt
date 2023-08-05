==========
 memojito
==========

:author: whit <whit@openplans.org>
:date: April 19 2006
:version:  0.5
:abstract: *A little library of decorators for doing memos*


"Memoization is a technique used to speed up computer programs by
storing the results of functions for later reuse, rather than
recomputing them. Memoization is a characteristic of dynamic
programming."

"Ernest Hemingway was fond of the Mojitos at La Bodeguita del Medio in
Havana, Cuba, though his recipe had no sugar."

                         *From Wikipedia, the free encyclopedia*


Introduction
============

memojito is memo sugar for python object methods. It comes in 2
flavors of decorators::

 * memojito.memoize : stores method return as memo, returns memo if
signature matches

 * memojito.memoizedproperty :  memoizes a method *and* creates a
  property rather than a method


To complement, it also includes some simple clean up decorators::

 * clearbefore : clears all memos before returning method

 * clearafter : clears all memos before return method


