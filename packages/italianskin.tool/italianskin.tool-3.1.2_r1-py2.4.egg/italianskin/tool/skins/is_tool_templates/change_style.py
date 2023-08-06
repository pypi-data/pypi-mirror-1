## Script (Python) "change_style"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=style
##title=
##
request = container.REQUEST
response =  request.RESPONSE
response.setCookie("fontsize", style)
return response.redirect(request.HTTP_REFERER)
