Introduction
============
This package lets you add a archetypes.multifile field into any archetypes object using schemaextender.

Usage
=====
1. Install package by adding the egg into your buildout cfg::
	
	[instance]
	...
	eggs =
		collective.multifilesextender
	zcml = 
		collective.multifilesextender
		
2. Rerun buildout

3. To turn it on, mark desired type with IMultiFileExtendable marker interface. For instance the following adds multifile field into ATDocument. You can put it into any zcml that is included when you start instance::

	<five:implements
      class="Products.ATContentTypes.content.document.ATDocument"
      interface="collective.multifilesextender.interfaces.IMultiFileExtendable"
      />

4. Start the instance

5. Install it via QuickInstaller

TODO
====
Add some tests

Credits
=======
Package developed by Matous Hora http://dms4u.cz