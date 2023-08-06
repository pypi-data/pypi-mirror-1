qi.LiveChat Package Readme
=========================

Overview
--------

qi.LiveChat is a simple ajax chat product for plone.

It requires an external utility that handles message keeping. At the moment only an xmlrpc server is provided. However it is very easy to add other implementations in order to use sql or use a logging facility.

Installation
------------
If you use buildout add qi.LiveChat to your eggs and zcml sections. Installation will also add a script called "livechat_server" to your buildout's bin directory (see "Usage")
This package is an egg, if you don't use buildout put it in INSTANCE/lib/python and add a file named qi.LiveChat-configure.zcml in INSTANCE/etc/package-includes with the following line:

<include package="qi.LiveChat" file="configure.zcml" />

Go to portal quick installer and install qi.LiveChat.
Add a chat room and chat away!

Usage
-----
In order to use the provided xmlrpc message keeper you have to run the qi.LiveChat/qi/LiveChat/server/xmlrpcServer.py script. If you used buildout, there is a link named livechat_server provided for convenience inside your buildout's bin folder.


Written by G. Gozadinos  http://qiweb.net
Smiley support code borrowed from PloneBoard.