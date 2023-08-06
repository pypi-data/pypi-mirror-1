import re

from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
import quintagroup.plonegooglesitemaps.config as config

ADD_ZOPE = re.compile('^/')
ADD_PLONE = re.compile('^[^http://|https://|\\\]')
OPERATIONS_PARSE = re.compile(r"(.?[^\\])/(.*[^\\]|)/(.*[^\\]|)/")

def searchAndReplace(string, what, with):
    """Emulate sed command s/"""
    res = re.sub(what,with,string)
    return res
OPERATORS = {'s': searchAndReplace,}

def applyOperations(objects, operations):
    """Parse Operations """
    operations=[OPERATIONS_PARSE.match(op).groups() for op in operations]
    result = {}
    for ob in objects:
        if ob.has_key('canonical_path'):
            url = ob.canonical_path
        else:
            url = '/'+'/'.join(ob.getPath().split('/')[2:])
        for operator, what, with in operations:
            url = OPERATORS[operator](url, what, with.replace("\\", ""))
        #TODO: Remove or replace following condition
        #it is senseless in the case we need intelligent
        #result set. Better condition would be to place
        #freshest brain into result
        if url in result.keys():
            continue
        #TODO: replace brain with only data necessary to 
        #generate sitemap
        result[url]=ob
    return result

def additionalURLs(context):
    """Add URLs to sitemap that arn't objects"""
    res = []

    plone_home = getToolByName(context, 'portal_url')()
    root = context.getPhysicalRoot().absolute_url()
    URLs =  context.getUrls()

    for url in URLs:
        if ADD_ZOPE.match(url):
            res.append(root+url)
        elif ADD_PLONE.match(url):
            res.append(plone_home+'/'+url)
        else:
            res.append(url)
    return res
