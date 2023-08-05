qi.LiveChat Package Readme
=========================

Overview
--------

qi.LiveChat is a simple ajax chat product for plone.

It requires an external utility that handles message keeping. At the moment only an xmlrpc server is provided. However it is very easy to add other implementations in order to use sql or use a logging facility.

Usage
_____
In order to use the provided xmlrpc message keeper you have to run the qi.LiveChat/qi/LiveChat/server/xmlrpcServer.py script.
This package is an egg, if you don't use buildout put it in INSTANCE/lib/python and add a file named qi.LiveChat-configure.zcml in INSTANCE/etc/package-includes with the following line:

<include package="qi.LiveChat" file="configure.zcml" />

Go to portal quick installer and install qi.LiveChat.
Add a chat room and chat away!

Written by G. Gozadinos and D. Moraitis http://qiweb.net
Smiley support code borrowed from PloneBoard.