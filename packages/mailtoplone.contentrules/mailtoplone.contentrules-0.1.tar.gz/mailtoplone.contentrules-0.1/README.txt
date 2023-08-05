mailtoplone.contentrules
========================

Overview
--------

content rules actions and conditions created for usage with mailtoplone

Authors
-------

Stefan Eletzhofer --
    "stefan.eletzhofer@inquant.de"

Hans-Peter Locher --
    "hans-peter.locher@inquant.de"

Copyright (c) 2007-2008 InQuant GmbH -- "http://www.inquant.de"

Dependencies
------------

Additional egg dependecies
**************************

mailtoplone.base

Contents
--------

Conditions
**********

Email Header:

     Checks a specified header for a specified value, value can be specified as regular expression
     (will check for simple containment if value isn't a regular
     expression).


Actions
*******

Deliver:

    Deliver mail to another dropbox by key, uses the BaseDropBoxFactory utility defined in
    mailtoplone.base to determine the dropboxes.


vim: set ft=rst tw=75 nocin nosi ai sw=4 ts=4 expandtab:
