# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: computeRelatedItems.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
from AccessControl import Unauthorized

MAX_RESULTS = None

def append_results(context, docs, new_results):
    for d in new_results:
        if context != d.getObject() and not d.getObject() in docs:
            docs.append(d.getObject())

def find_related(context):
    keywords = context.Subject()
    catalog = context.getCatalogs()[0]
    docs = []
    append_results(context, docs, catalog(SearchableSynonymousText=keywords))
    append_results(context, docs, catalog(SearchableRelatedText=keywords))
    return docs

if hasattr(context, 'getRelatedItems'):
    outgoing = context.getRelatedItems()
    incoming = []
    found = find_related(context)
    # if you want to show up the items which point to this one, too, then use the
    # line below
    #incoming = context.getBRefs('relatesTo') 
    res = []
    mtool = context.portal_membership
    
    in_out = outgoing+incoming+found
    for d in range(len(in_out)):
        try:
            obj = in_out[d]
	except Unauthorized:
            continue
        if obj not in res:
            if mtool.checkPermission('View', obj):
                res.append(obj)
                if len(res) == MAX_RESULTS:
                    break
    
    return res
