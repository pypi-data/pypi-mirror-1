
Introduction
============

This egg is just an adapter which let all the ATContentTypes to be "mappable" on a GoogleMap
managed by Products.Maps

We managed the way the baloon is drawn since it's supposed that on the first tab should appear 
the most informative fields. So, the first tab contains:

 * title
 * description
 * `<other type-depending infos>`, tipically the text of the object or the image or the link to the file; see browser "base" view

Every ATObject has a default different baloon behaviour. It could be effective for the 50% of
the usual cases. you can always override it easily and quickly. Take them as an esample.


TO DO
=====

 * the skin layer must be installed before the Maps layer: actually you need to move it manually :(
 * Integration with p4a.subtyper?
 * translations
 * get less text from text field