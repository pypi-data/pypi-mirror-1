========
ON Sales
========

This package contains content types to handle the sales organization
part of the website of a middle-sized business, mainly sales agents and
their sales areas.

For general usage hints, please see the README.txt file in the 'docs'
dir at the top of this egg.

This test uses zope.testbrowser to simulate browser interaction and
also to show how this product is supposed to work.

At first we set up the test environment and log in.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> self.portal.error_log._ignored_exceptions = ()

    >>> portal_url = self.portal.absolute_url()
    >>> print str(portal_url)
    http://nohost/plone

    >>> from Products.PloneTestCase.setup import portal_owner, default_password

    >>> browser.open(portal_url + '/login')
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

    >>> browser.open('http://nohost/plone/prefs_install_products_form')

Let's see if the product made it to the quickinstaller already:

    >>> 'ON Sales Management' in browser.contents
    True

    >>> browser.open(portal_url)

Verify that we have the links to create Sales Agents and Areas in the "add
item" menu:

    >>> browser.getLink(id='salesarea').url.endswith("createObject?type_name=SalesArea")
    True

    >>> browser.getLink(id='salesagent').url.endswith("createObject?type_name=SalesAgent")
    True

    >>> browser.getLink(id='salesagentproxy').url.endswith("createObject?type_name=SalesAgentProxy")
    True


Addable content
---------------

This package contains three content types: SalesAgent, SalesAgentProxy
and SalesArea.  

SalesAgent represents a salesperson. It has several fields for
(contact) information and an image widget for a portrait. You needn't
fill it, but if you do it gives your customer an idea to whom he may
talk. Sales agent is derived from a simple page. Let us first create
such a salesperson.

At first, let's see if the interfaces are half-way sane:

    >>> from zope.interface import Interface, providedBy
    >>> from on.sales import interfaces
    >>> Interface.providedBy(interfaces.ISalesAgent)
    True

See wether everything is in place

    >>> from on.sales import salesagent
    
    >>> salesagent.SalesAgent
    <class 'on.sales.salesagent.SalesAgent'>

    >>> interfaces.ISalesAgent.implementedBy(salesagent.SalesAgent)
    True

Now we try to insert a Sales Agent:

    >>> browser.getLink(id='salesagent').click()
    >>> browser.getControl(name='title').value = "John Doe"
    >>> browser.getControl(name='description').value = "Description"
    >>> browser.getControl(name='email').value = "jdoe@omain.de"

    >>> browser.getControl(name='form_submit').click()

Check wether everything has gone right:

    >>> 'john-doe' in self.portal.objectIds()
    True
    >>> vendor1 = self.portal['john-doe']
    >>> vendor1.title
    'John Doe'
    >>> vendor1.email
    'jdoe@omain.de'

The "internal" field has a default value:

    >>> vendor1.internal
    False

Wow! Let us repeat the wonder:

    >>> browser.open(portal_url)

    >>> browser.getLink(id='salesagent').click()
    >>> browser.url
    'http://nohost/plone/portal_factory/SalesAgent/...'

    >>> browser.getControl(name='title').value = "Johnny Walker"
    >>> browser.getControl(name='description').value = "best whiskey"
    >>> browser.getControl(name='email').value = "jwalker@omain.de"
    >>> browser.getControl(name='department').value = "ireland"

Here, we also set the "internal" value to "True". This feature is to
prevent certain sales persons from being assigned to a certain area,
e.g. because you want her to show up as a contact, but she is for key
accounts worldwide. 

    >>> browser.getControl(name='internal:boolean').getControl("Internal only").selected = True

    >>> browser.getControl(name='form_submit').click()

    >>> 'johnny-walker' in self.portal.objectIds()
    True
    >>> vendor2 = self.portal['johnny-walker']
    >>> vendor2.title
    'Johnny Walker'
    >>> vendor2.internal
    True

We need to publish our Salesmen to make them available for assignment
to a sales area:

    >>> self.setRoles(('Manager',))
    >>> browser.open(portal_url)

    >>> self.portal.portal_workflow.doActionFor(vendor1, 'publish')
    >>> self.portal.portal_workflow.doActionFor(vendor2, 'publish')

SalesArea represents a Sales area (how surprising ...). It is
folderish so that it can keep an arbitrary count of other sales areas,
thus allowing to build up a hirarchy of them. The other content type
allowed in Sales areas are SalesAgentProxies. SalesArea also provides
an image widget which is supposed to show e.g. the outlines of the
area, a photo of the plant or a flag. Again, the usage of this feature
is deliberate.

A SalesAgentProxy is a sort of link between SalesArea and SalesAgent:
it is contained in a salesarea and points to a SalesAgent, thus
allowing to assign various areas at the same time to one salesman. The
SalesAgentProxy contains a link to the according SalesAgent. Following
that link it accesses the SalesAgent's data and shows them.

So let's create a sales area and assign a sales person to it!

    >>> Interface.providedBy(interfaces.ISalesArea)
    True

    >>> from on.sales import salesarea
    
    >>> salesarea.SalesArea
    <class 'on.sales.salesarea.SalesArea'>

    >>> interfaces.ISalesArea.implementedBy(salesarea.SalesArea)
    True

    >>> browser.getLink(id='salesarea').click()
    >>> browser.getControl(name='title').value = "Europe"
    >>> browser.getControl(name='description').value = "first sales area"

    >>> browser.getControl(name='form_submit').click()

What does the new Sales Area look like?

    >>> 'europe' in self.portal.objectIds()
    True
    >>> area1 = self.portal['europe']
    
    >>> area1
    <SalesArea at /plone/europe>
    
    >>> area1.description
    'first sales area'

And what's in it?
    >>> area1_url = area1.absolute_url()
    >>> browser.open(area1_url)

    >>> browser.getLink(id='salesarea').url.endswith("createObject?type_name=SalesArea")
    True
    
    >>> browser.getLink(id='salesagentproxy').url.endswith("createObject?type_name=SalesAgentProxy")
    True

The "normal" content types shouldn't be there. We don't check this for _every_ content type but just choose one:
    >>> browser.getLink(id='page').url.endswith("createObject?type_name=Page")
    Traceback (most recent call last):
    ...    
    LinkNotFoundError

Now let us add a SalesAgentProxy. 

    >>> browser.getLink(id='salesagentproxy').click()

    >>> browser.getControl(name='title').value = "Primary Seller"
    >>> browser.getControl(name='description').value = "our best whiskey drinker"

    >>> browser.getControl(name='real_salesagent').getControl("Johnny Walker").selected = True

    >>> browser.getControl(name='form_submit').click()

Let's verify that the proxy object pulls data from the salesagent it is assigned to:

    >>> "jwalker@omain.de" in browser.contents
    True

    >>> "ireland" in browser.contents
    True

And the salesagentproxy is shown in the area under his name:

    >>> browser.open(area1_url)

    >>> '<a href="primary-seller/view">' in browser.contents
    True

Now we put in a second sales agent proxy.

    >>> browser.open(area1_url)

    >>> browser.getLink(id='salesagentproxy').click()
    >>> browser.getControl(name='title').value = "Second Seller"
    >>> browser.getControl(name='description').value = "our best cola seller"
    >>> browser.getControl(name='real_salesagent').getControl("John Doe").selected = True
    >>> browser.getControl(name='form_submit').click()

Now what's in the area ?

    >>> browser.open(area1_url)

    >>> '<a href="second-seller/view">' in browser.contents
    True

And the first proxy we added?
    
    >>> '<a href="primary-seller/view">' in browser.contents
    False

Uh? Where is the first sales agent?  This demonstrates a feature. The
first proxy we created pointed to the sales agent "Johnny Walker. Do
you remember that we set the "internal" flag to "true" for him at the
beginning of the test? As long as we had no other sales agent proxy in
our area with that flag set to "False" this didn't matter, but as soon
as we assign a sales agent with "internal" set to "false" the product
doesn't show those agents who have it set to "True".

Now let's test an other feature: the salesmail form that is hidden
behind the "flying envelope" in the head of each sales area.

    >>> '@@Email_Form' in browser.contents
    True

    >>> mailform = area1_url + "/@@Email_Form"
    >>> browser.open(mailform)
    
    >>> browser.getControl(name='form.subject').value = "testmail"
    >>> browser.getControl(name='form.name').value = "Mr. X"
    >>> browser.getControl(name='form.email_address').value = "mr.x.test.org"
    >>> browser.getControl(name='form.message').value = "test message"

    >>> browser.getControl(name='form.actions.send').click()

Now let's see where the mail is going to. In the salesmail.py we
defined the action "send" such that a function "mailaddresses" in the
context is invoked which in turn collects the mail addresses of the
responsible salesagents. It works quite similar to the function that
pulls the real sales agent's data by following the link from the sales
agent proxy to its corresponding sales agent. As we can't catch the
list of mail addresses in the form we call the form directly to see
how it works.

    >>> browser.open(area1_url)
    >>> salesarea.getMaillist(context)    
