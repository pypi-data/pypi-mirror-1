Introduction
============

This product provides an aggregation solution for our specific environment.

What makes our environment relatively unique? 

The fact that almost all content must be available in more than 20 languages. 
In addition to that, content distributed over various subsites, each with it's
own news and events folders and various other duplications.

Inevitably, a lot of content duplication results, as News Items are located all
over the place and content creators are not aware of their existence.

slc.aggregation is therefore part of our Resource Centralisation strategy.

You could use Collections/Topics, but they have some flaws when it comes to a
multiple language environment. For example, each Collection we add, needs to be
translated into about 22 languages.

This product therefore adds a new aggregation mechanism, for use in sites with
many language versions.

How to use:
===========

A new subtype 'Aggregator' is created in descriptors.py and it can be applied
to all Folders in the Site.

When browsing in Plone, you will see that there is a 'subtypes' menu visible
in the folder actions bar.

You can click on this menu and then choose 'Aggregator' to change your folder
into an aggregator.

On reload, the Folder will now have a new view, with nothing in it, because 
nothing is yet aggregated. You will notice a new object tab labeled
'Aggregation'. You can click on it, and find the form for configuring you
aggregator. 

The values you specify will basically be used to construct a catalog query,
that fetches the objects for you.

If correctly configured, your folder's view should now show a batched listing
of the aggregated objects.

Known Issues:
=============

To use the aggregator in a multi-language site, you have to subtype all the
translations of a folder.

Since subtyping doesn't take translations into account, this has to be done
manually.

We will eventually release a product called slc.linguatools, that would among
other things allow you to subtype multiple translations simultaneously.


Dependencies:
=============

    - p4a.common
    - p4a.z2utils
    - p4a.subtyper
    - archetypes.schemaextender
    - Products.AdvancedQuery





