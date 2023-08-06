Introduction
============

Have you ever feel the need to give to normal (AKA non-manager) Plone member the power to manage a group?

Right now in Plone you can make this possible playin with the **Manage users** and **Manage Groups**
permissions of the portal (also for Plone 2.5).

What is (obviously) impossible is to limit the group on which a member can add.

This products make something very dangerous: with a minimal configuration a member of the Plone portal
(or all members in a group) will be able to manage the users of a group overriding the portal security.

The utility also react to the **Add portal members** permission. If the current user has this permission
you will be able to add new portal members.

Be aware!
---------

This products override all normal Plone permissions noted above!
This can create **security black-holes** in your portal!

.. figure:: http://keul.it/images/Black_Hole_Milkyway.jpg
   :scale: 50

Plone 2.5 support
-----------------

This product is done to work with the old Plone 2.5 release also. To use it, copy the *SimpleGroupsManagement*
in your *Products* section.

