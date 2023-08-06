## Script (Python) "getFck_basehref.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=pa_meta_types=[]
##title= fck custom config for Plone
##

request=context.REQUEST
if '/portal_factory' in request.URLPATH0 :
    basehref = request.URL4
elif context.meta_type in pa_meta_types or context.isPrincipiaFolderish:
    if 'replaceField/replaceField' in request.URLPATH0 :
       basehref = request.URL2
    else:   
       basehref = request.URL1
# kss templates url are finishing with 'replaceField/replaceField'       
elif 'replaceField/replaceField' in request.URLPATH0 :
    basehref = request.URL3
else : 
    basehref = request.URL2

return basehref
