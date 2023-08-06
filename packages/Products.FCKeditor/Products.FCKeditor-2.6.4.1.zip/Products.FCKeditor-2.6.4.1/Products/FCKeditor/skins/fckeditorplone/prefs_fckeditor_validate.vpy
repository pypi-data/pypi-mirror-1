## Controller Validator "prefs_fckeditor_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates FCKeditor options
##

from Products.CMFCore.utils import getToolByName
import Products.FCKeditor.utils as fck_utils

portal_url = getToolByName(context, 'portal_url')
portal = portal_url.getPortalObject()

def formData(field_name):
   return context.REQUEST.get(field_name, None)

def sizeValidate(field_name):
   value = formData(field_name)
   if not fck_utils.isValidSize(value):
      state.setError(field_name, 'Invalid size value')
   return

def pathValidate(field_name):
   value = formData(field_name)
   if not fck_utils.isValidPath(portal, value):
      state.setError(field_name, 'Invalid path')
   return

sizeValidate('fck_force_width')
sizeValidate('fck_force_height')


#if not fck_utils.isValidStylesheet(context, formData('fck_area_style')):
#   state.setError('fck_area_style', 'No such object')

if not formData('fck_force_path'):
   pathValidate('fck_force_other_path')

if not formData('fck_force_root'):
   pathValidate('fck_force_other_root')

if state.getErrors():
   # An error has occurred.  Set the status to 'failure'
   # (the default initial status is 'success')
   state.setStatus('failure')
   # Return the state and pass the variable portal_status_message in the REQUEST
   return state.set(portal_status_message='Please correct the indicated errors.')

# No errors.  Always make sure to return the ControllerState object
return state
