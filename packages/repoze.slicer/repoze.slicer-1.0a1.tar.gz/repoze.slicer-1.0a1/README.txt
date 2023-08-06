Introduction
=============

`repoze.slicer` is a simple piece of WSGI middleware that can extract part of a
HTML response. This can be used to reduce the amount of parsing and
manipulation of DOM trees in browsers, which is especially expensive with older
versions of IE.
