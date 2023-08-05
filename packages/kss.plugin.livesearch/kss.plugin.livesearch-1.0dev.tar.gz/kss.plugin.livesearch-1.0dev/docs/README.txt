
KSS plugin package "kss.plugin.livesearch"

Installation and Setup
======================

Read INSTALL.txt

Documentation
=============


Features implemented
--------------------

- Identical replacement of the original livesearch.

  I "wrapped" the original code to a kss event, making the following changes:

  - I transformed functions to class methods. While this would have been
    strictly necessary, it corresponds to the kss event model better and also
    makes the javascript code more structured.

  - I got rid of the LSResult / LSShadow tricks. Now there is no placeholder
    originally, but the snippet is inserted as the last node of the block that
    holds the triggering import node. This may be changed later if necessary,
    for more general purpose use, by introducing parameters for the place of
    insertion, for example.

    Remarks:

      1. The original port worked without this change. However it is better now
         since we have a single kss event to bind. Also I believe this is an
         improvement on the original code.

      2. Meanwhile there was a resizing part of the code that is now commented
         out and not effective. I simply don't know what its purpose was, and I
         do not see any difference in the result without it. Once I find out
         what is broken now.  I can put the code part back or get the desired
         effect in any other way.

  Missing/TODOS:

     - Generalize the server action and enable to use it with other use cases,
       e.g.  autocomplete.

KSS extensions defined for general purpose use
----------------------------------------------

- The livesearch-searchbox event can be used for general purpose components.


- client action for submitting to an url

- client action for submitting the current form


