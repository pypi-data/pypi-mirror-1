## Script (Python) "updateTransition"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=new_state_id
##
title=context.title
description=context.description
trigger_type=context.trigger_type
script_name=context.script_name
after_script_name=context.after_script_name
actbox_name=context.actbox_name
actbox_url=context.actbox_url
actbox_category=context.actbox_category
context.setProperties(title=title,description=description,trigger_type=trigger_type,script_name=script_name,after_script_name=after_script_name,new_state_id=new_state_id,actbox_name=actbox_name,actbox_url=actbox_url,actbox_category=actbox_category)
