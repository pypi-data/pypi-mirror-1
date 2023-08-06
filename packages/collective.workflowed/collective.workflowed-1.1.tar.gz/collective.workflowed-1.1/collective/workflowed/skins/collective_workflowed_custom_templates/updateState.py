## Script (Python) "updateState"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=transitions=[]
##
title=context.title
description=context.description
context.setProperties(title=title,transitions=transitions,description=description)
