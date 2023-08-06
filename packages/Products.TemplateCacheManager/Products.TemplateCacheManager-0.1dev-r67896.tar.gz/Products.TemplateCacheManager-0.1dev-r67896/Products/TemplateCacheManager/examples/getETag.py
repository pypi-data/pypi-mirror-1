## Script (Python) "getETag"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=max_age=1800
##title=
##

from math import floor
from DateTime import DateTime

def getFloorTime(age):
    step = (age > 1 and age or 2)/2
    return floor(DateTime().timeTime()/step)*step

# REQUEST variables that will be used in the etag
request_vars = ['ACTUAL_URL','QUERY_STRING','LANGUAGE']

request = container.REQUEST
RESPONSE =  request.RESPONSE

# TTL of etag
time_slot = getFloorTime(max_age)

# get username
u = request.get('AUTHENTICATED_USER', None)
user_id = 'Anonymous User'

if u is not None:
   user_id = u.getUserName()

# get last modification time
last_modified = context.modified().timeTime()

# get request vars for the etag 
d={}
for v in request_vars:    
    d[v] = request.get(v,None)

# call external method for md5 hash
md5_hash = context.md5_hexdigest(str(d))

# generate etag
etag = '%s|%s|%s|%s' % (str(user_id), str(last_modified), md5_hash, time_slot)

return etag

