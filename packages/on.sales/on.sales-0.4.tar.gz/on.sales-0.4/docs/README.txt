
=======================================
How this product is intended to be used
=======================================

If you have successfully installed this product (to do this, relay to
the file "INSTALL.txt" in this directory), you should be able to add
it to your plone site via the ZMI "portal_quickinstaller" tool, or via
the PMI "Addon Products" menu. If you enter your plone instance as an
administrator after doing so, you will see three new content types in
your "add" pullddown menu: "Sales Area", "Sales Agent" and "Sales
Agent Proxy".

The three content types mentioned above can collectively be used to
model a sales organization along geographic boundaries, as are usually
presented to the general public as part of a company website.


The Content Types
=================

Sales Area
----------

The "Sales Area" is a folderish type which may contain nested (sub-)
areas, described by instances of the "Sales Area" type itself, and
instances of "Sales Agent Proxy". You can add an image to an instance
of a Sales Area, which is intended to graphically highlight the region
you want to describe.


Sales Agent
-----------

The "Sales Agent" is a type that carries the contact data and
descriptive text for a sales representative whom you assign specific
responsibilities for certain sales areas.


Sales Agent Proxy
-----------------

The "Sales Agent Proxy" type is a proxy which is intended to be used
in instances of the Sales Area type, instead of directly using Sales
Agent instances. The indirection provided by this type is intended to
allow you to maintain the actual information about your sales
personell in one place only, while referencing them in various places
w/o worrying about whether you might inadvertantly retire a sales
person because you delete a no-longer needed sales area, or whether
one sales person might have different phone numbers, depending on
which region he is listed in. On display, the Sales Agent Proxy
displays like a Sales Agent, but maintains the current context instead
of revealing the location where the Sales Agent object is stored.


General Usage
=============

Since instances of Sales Agent Proxy can only reference published
instances of Sales Agents, it is highly advisable to build a
collection of Sales Agents first, before starting to assign Sales
Agents to Sales Areas. Currently, this workflow is enforced by
preventing Sales Agents from being directly added to Sales Areas.

You also add a hierarchy of "Sales Area"s, starting out with
some kind of a top level object ("The World"), which you can subdivide
to any level of detail you see fit. To each of these areas, you can
add sales representatives.


A user of the site should be able to navigate to his desired area and
send an inquiry to the group of sales representatives who are
responsible for the current area. If there is no sales representative
assigned to the current area, the product attempts to collect email
addresses from sales personell listed in areas up the hierarchy. You
must have at least one email address at the top level Sales Area
object, which you assign through a sales person assigned to that area.

Currently, the product throws an exception if you don't effectively
assign an email address at the top level (via a sales person).



Restricting "add" properties
============================

While you can use these content types wherever you want, it's
advisable, and intended, to use "Sales Agent Proxy" instances only
within a "Sales Area".

Therefore, we recommend to restrict the possibility to add Sales Agent
Proxies to Sales Areas because they are constructed to co-work with
them and won't work well in other places. To accomplisch this, enter
the ZMI -> Your Plone Site -> portal_content_types -> Sales Agent
Proxy. In its controll panel, make shure that the choice "Implicitly
addable" is de-selected. To restrict the other two content types of
this products, you might as well use the "restrict..."  control panel
that is available for every Plone folder in the bottom of the "add"
menu.
