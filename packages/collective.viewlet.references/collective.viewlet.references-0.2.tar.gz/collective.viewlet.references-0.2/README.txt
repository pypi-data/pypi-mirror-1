Introduction
============

Viewlet that shows all the references to the current article including back references, by defult it is registered to IBelowContent.
For now, it has a hard dependency on collective.contentleadimage and collective.flowplayer. This means you have to install those products in order for References to work.

Used in production in http://www.v2.nl/

To choose which types should use the viewlet go to ZMI -> portal_properties -> references_properties and add the types on apply_to separated by a space.
