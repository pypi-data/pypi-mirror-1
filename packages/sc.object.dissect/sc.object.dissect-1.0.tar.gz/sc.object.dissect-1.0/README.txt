Introduction
============

This products adds a browser view that list all methods and attributes of any object in Zope. 

It removes the methods "__roles__" and "manage_" from this list because it sucks.

To install adds the product to sections eggs and zcml of your buildout.

   eggs = ...
        sc.object.dissect
   ...
   zcml = ...
        sc.object.dissect


To use, just add /dissect after the object URL in your web browser address bar. The /@@dissect also can be used.

Authors
=======
* Thiago Tamosauskas [tamosauskas]
* Luciano Pacheco [lucmult]
* And, of course, Simples Consultoria http://www.simplesconsultoria.com.br


