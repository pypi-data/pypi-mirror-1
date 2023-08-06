## Script (Python) "current_language"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Retreive current portal language for the user
##

request = container.REQUEST
try:
    lang=request['LANGUAGE']
except:
    lang=request['HTTP_ACCEPT_LANG']

if (lang is None) or (lang[:2]=='en'):
    return 'en'
elif lang[:2]=='ru':
    return 'ru'
elif lang[:2] in ['ua', 'uk']:
    return 'uk'
else:
    return 'en'