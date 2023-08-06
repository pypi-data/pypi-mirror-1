Salesforce Auth Plugin
======================
Product home is
http://plone.org/products/salesforceauthplugin.
A `documentation area`_ and `issue
tracker`_ are available at
the linked locations.

.. _documentation area: http://plone.org/products/salesforceauthplugin/documentation
.. _issue tracker: http://plone.org/products/salesforcebaseconnector/issues

A Google Group, called `Plone Salesforce Integration`_ 
exists with the sole aim of discussing and developing tools to make Plone integrate well
with Salesforce.com.  If you have a question, joining this group and posting to the 
mailing list is the likely best way to get support.

.. _Plone Salesforce Integration: http://groups.google.com/group/plonesf

Failing that, please try using the Plone users' mailing list or the #plone irc channel for
support requests. If you are unable to get your questions answered there, or are 
interested in helping develop the product, see the credits below for 
individuals you might contact.

Overview
========
Using the architecture of Zope's Pluggable Authentication Service and PlonePAS, Salesforce
Auth Plugin provides the infrastructure to manage site users as arbitrary objects within a 
Plone portal.  Features and capabilities for Plone user management via Salesforce.com include:


- Configurable SFObject type to serve as Plone user for authentication
- Configurable username and password field on an SFObject for credential checking
- Optional password encryption
- Optional caching of user data from Salesforce.com to improve performance
- Addition of new users as designated SFObject type from Plone portal into Salesforce.com
- Property retrieval and setting for Plone users as stored in Salesforce.com


Install & Dependencies
======================
See ./docs/INSTALL.txt

Known Problems
==============
See "Caveats" in ./docs/INSTALL.txt

Credits
=======
The Plone & Salesforce crew in Seattle and Portland:


- Jon Baldivieso <jonb --AT-- onenw --DOT-- org>
- Andrew Burkhalter <andrewb --AT-- onenw --DOT-- org>
- Brian Gershon <briang --AT-- webcollective --DOT-- coop>
- David Glick <davidglick --AT-- onenw --DOT-- orgg> 
- Jesse Snyder <jesses --AT-- npowerseattle --DOT-- org>


Salesforce.com Foundation and Enfold Systems for their gift and work on beatbox
and the original proof of concept code that has become Salesforce Auth Plugin (see: 
http://gokubi.com/archives/onenorthwest-gets-grant-from-salesforcecom-to-integrate-with-plone)

See the HISTORY.txt file for the growing list of people who helped
with particular features or bugs.

License
=======
Distributed under the GPL.

See LICENSE.txt and LICENSE.GPL for details.

Running Tests
=============
It is strongly recommended that you run your tests
against a free developer account, rather than a real
production Salesforce.com instance. ... With that said,
to run the tests for Salesforce Auth Plugin do the following:

=======================================
Configure your Salesforce.com instance:
=======================================
In order to successfully run all of the automated unit tests, 
some modifications need to happen within your Salesforce.com 
instance.  

In many of the tests, authentication, user creation,
and modification happen against the Salesforce.com contact 
and/or lead object.  Specifically, the unit tests create objects
and then authenticate against two custom fields: Password and UserName.

For all tests to successfully work create and configure the following 
fields as shown below:

    Field Label         Field Name          Field Type
    
    -----------         ----------          ----------
    
    Password            Password            Text(100)
    
    User Name           UserName            Text(50)
    
    Favorite Boolean    FavoriteBoolean     Checkbox
    
    Favorite Float      FavoriteFloat       Number(13, 5)
    

Note: You can accept the defaults for the other field attributes.

=====
Read:
=====

Running Tests --> "To run tests in a unix-like environment" from
`SalesforceBaseConnector`_, which is a dependency, so you should have it :)

.. _SalesforceBaseConnector: http://plone.org/products/salesforcebaseconnector

=================
Do the following:
=================
Rather than running the test suite for salesforcebaseconnector
do the following:

    $INSTANCE/bin/zopectl test -s collective.salesforce.authplugin

=======================
FAQ about running tests
=======================
If you have trouble running tests, consult "FAQ about running tests" from
SalesforceBaseConnector.
