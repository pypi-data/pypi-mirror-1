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


# fix basepath for static portlet edition

if '++' in request.URLPATH0 :
    basehref = request.URLPATH0.split('++')[0].rstrip('/')
    

elif '/portal_factory' in request.URLPATH0 :
    basehref = request.URL4

# kss templates url are finishing with 'replaceField/replaceField'       
elif 'replaceField/replaceField' in request.URLPATH0 :
    basehref = request.URL3
else : 
    basehref = request.URL2

return basehref


