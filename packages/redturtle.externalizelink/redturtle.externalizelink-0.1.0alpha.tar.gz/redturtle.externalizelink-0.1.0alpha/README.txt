Reference
=========

General accessibility rule used here was `taken from a guide`__ written by
`Regione Emilia Romagna`__

Javascript code here has been moved to a jQuery environment.

__ http://www.regione.emilia-romagna.it/wcm/LineeGuida/sezioni/tecnici/script.htm
__ http://www.regione.emilia-romagna.it/

Introduction
============

The idea behind this is to enable in Plone the ability to open external link in different
browser windows.

The right way to do this is to look for the **rel="external"** attribute on link elements.

As far as **Kupu** and **TinyMCE** don't support the **rel** attribute, here we also look for
the **class="external-link"** attribute.

Also anchor's *title* will be changed/completed runtime with a more accessible message that
warn user that a new window will be opened.

