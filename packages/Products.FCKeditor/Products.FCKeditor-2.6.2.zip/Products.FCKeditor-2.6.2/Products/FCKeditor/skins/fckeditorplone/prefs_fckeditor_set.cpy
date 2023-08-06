## Controller Python Script "prefs_fckeditor_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=RESPONSE=None
##title=
##

from Products.FCKeditor.utils import fckDefaultToolbar, fckDefaultKeystrokes
request=context.REQUEST

portal = context.portal_url.getPortalObject()

request.set('title', 'FCKeditor properties')



fck_force_root=request.get('fck_force_root',0)
if fck_force_root:
    request.set('fck_force_path', 1)

fck_force_other_root=request.get('fck_force_other_root','')
if fck_force_other_root :
    try :
        browser_root= portal.restrictedTraverse(fck_force_other_root.lstrip('/'))
    except:
        return state.set(status="failure", portal_status_message="The browser root don't exist")
   
   
fck_force_other_path=request.get('fck_force_other_path','')
if fck_force_other_path :
    try :
        browser_path=portal.restrictedTraverse(fck_force_other_path.lstrip('/'))
    except:
        return state.set(status="failure", portal_status_message="Error : The browser opening folder path don't exist")



if fck_force_other_root and not fck_force_other_root in fck_force_other_path:
    request.set('fck_force_other_path', fck_force_other_root)
    
    
fck_toolbar=request.get('fck_toolbar','')

if fck_toolbar=='Custom':
   fck_custom_toolbar=request.get('fck_custom_toolbar','')
else:
   fck_custom_toolbar = fckDefaultToolbar()
   
    
keyboard_keystrokesmode=request.get('keyboard_keystrokesmode','')

if keyboard_keystrokesmode=='Custom':
   keyboard_customkeystrokes=request.get('keyboard_customkeystrokes','')
else:
   keyboard_customkeystrokes = fckDefaultKeystrokes()   

request.set('keyboard_customkeystrokes', keyboard_customkeystrokes)

# raise "REQUEST", str(request)

properties = context.portal_properties.fckeditor_properties
properties.manage_editProperties(request)

return state.set(status='success', portal_status_message='FCK Editor settings updated.')

