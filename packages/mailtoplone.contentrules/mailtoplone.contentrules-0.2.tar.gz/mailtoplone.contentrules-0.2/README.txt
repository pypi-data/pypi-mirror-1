mailtoplone.contentrules
========================

Overview
--------

content rules actions and conditions created for usage with mailtoplone

Authors
-------

Stefan Eletzhofer --
    "<stefan dot eletzhofer at inquant de>"

Hans-Peter Locher --
    "<hans-peter dot locher at inquant de>"

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

Has part of type:

    Checks if the email contains a part of specified maintype/subtype
    pair.

Size of mail:

    Checks the size of a mail (<=, >=) against a user specified size in megabyte.

Actions
*******

Deliver:

    Deliver mail to another dropbox by key, uses the BaseDropBoxFactory utility defined in
    mailtoplone.base to determine the dropboxes.


vim: set ft=rst tw=75 nocin nosi ai sw=4 ts=4 expandtab:
