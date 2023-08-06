## Script (Python) "standard_error_message"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kwargs
##title=Dispatches to relevant error view
##

error_type = kwargs.get('error_type', None)

if error_type == 'NotFound':
    path = context.REQUEST['PATH_INFO']
    portal_path = context.portal_url.getPortalPath()
    assert path[:len(portal_path)] == portal_path
    rel_path = path[len(portal_path):].rstrip('/')
    query = [rel_path]
    if rel_path.startswith('/'):
        query.append(rel_path.lstrip('/'))
    else:
        query.append('/'+rel_path)
    results = context.portal_catalog(
        getLocalPath=query, Type='Redirect',
        sort_on='effective', sort_order='descending', sort_limit=1)
    if results:
        return context.REQUEST.response.redirect(
            results[0].getRemoteUrl, status=301, lock=1)

return context.portal_skins.plone_templates.standard_error_message(
    **kwargs)
