RSVP for Salesforce
===================

Product home is
http://plone.org/products/collective.salesforce.rsvp

A `documentation area`_ and `issue
tracker`_ are available at
the linked locations.

.. _documentation area: http://plone.org/documentation/manual/integrating-plone-with-salesforce.com
.. _issue tracker: http://plone.org/products/collective.salesforce.rsvp/issues

A Google Group, called `Plone Salesforce Integration`_ exists with the sole aim
of discussing and developing tools to make Plone integrate well with
Salesforce.com. If you have a question, joining this group and posting to the
mailing list is the likely best way to get support.

.. _Plone Salesforce Integration: http://groups.google.com/group/plonesf

Failing that, please try using the Plone users' mailing list or the #plone irc
channel for support requests. If you are unable to get your questions answered
there, or are interested in helping develop the product, see the credits below
for individuals you might contact.

Overview
========

Using Plone's Archetypes system and archetypes.schemaextender, the RSVP for
Salesforce add-on product enables a mechanism for "marking" pieces of content
as eligible to accept RSVPs (i.e. registrations) from site visitors. The act of
"marking" content extends the existing piece of content with several additional
fields for custom RSVP behaviors.

However, this is not a generic RSVP/registration system, but as the name
suggests, is optimized to work with the Salesforce.com Customer Relationship
Management system, which is a generic system that can be used to manage Leads,
Contacts, Campaigns, and Events. By default, registrants are stored as Lead
objects with an associated CampaignMember object serving as the "junction"
between an organization's configured "Campaign" and those interested in
participating. This can be useful in cases of in person and/or virtual events
(i.e. a training, a conference, a political rally, etc.) and online campaigns
allowing participant sign-on (signature drives, pledge drives, etc.). The
default behavior of creating a Lead and CampaignMember associated with the
configured Campaign can be fully customized with the optional add-on Plone
products PloneFormGen (and dependencies) and Salesforce PFG Adapter.

Features of RSVP for Salesforce include:

  - Complete integration with the robust and powerful CRM system 
    Salesforce.com
  
  - Ability to mark and configure any Archetypes content object as RSVP-aware
  
  - Default registration form requiring minimal attendee information and 
    completely free of complex configuration demands.
  
  - Optional maximum capacity for RSVP-enabled activities
  
  - Optional acceptance of "waitlist" registrations in the event of 
    cancellations
  
  - Optional expiration date for the automatic disabling of RSVP
  
  - Ability to model "first come first served" or "apply for acceptance after 
    further consideration" type events.  This can be done by setting the 
    default signup "status" from within Salesforce.com for the RSVP-enabled 
    event (i.e. the status for a newly created CampaignMember could be "sent", 
    "applied", "responded", etc. depending upon how event attendance is 
    modeled in each case.
  
  - Optional Add-on Capability: Using PloneFormGen with Salesforce PFG Adapter 
    create enhanced and completely customizable registration forms requesting 
    and/or requiring arbitrary sign-up data that can be mapped to arbitrary 
    Salesforce.com objects.  The referring "RSVP" accepting Salesforce.com 
    object id is passed to the custom form for appropriate association.


What this isn't...
==================
... and may or may not ever be:

  - A general, feature complete ticketing, online registration system.  This is  
    simple and optimized to integrate well with Salesforce.com and is optimized 
    towards events with a flexible amount of capacity. While one can certainly 
    use this to lock down capacity a bit more tightly, the burden is upon a 
    correct configuration of the capacity related fields.

  - A system for accepting online payment to secure event attendance -- though 
    we're placing bets internally on how long it will be until this feature is 
    requested.

  - A fail safe system for absolutely capping attendance at a hard capacity.  
    Because a greater than max capacity # of participants could load a custom 
    PloneFormGen-based registration form (or the default registration form for 
    that matter) that suggests available capacity, we advise you to set 
    expectations appropriately during the signup process and via any 
    auto-response emails that are sent.  In other words, text like the 
    following goes a long way towards expectation management: "Thanks for 
    expressing your interest in attending our event. A follow-up email will be 
    sent within 24 hours confirming your space for the event."


DEPENDENCIES
============

RSVP for Salesforce requires Plone 3.0 or greater.

The following dependencies should be pulled in automatically when you install
the egg:

  * beatbox >= 0.9.1.1
  * Products.salesforcebaseconnector >= 1.0
  * archetypes.schemaextender

If you want to use custom PloneFormGen-based registration forms, then you must
have PloneFormGen >= 1.5b2.
