from Products.CMFCore.utils import getToolByName

def purge_url_map(member, event):
    openid_urls = getattr(member, '_openid_urls', [])
    for url in openid_urls:
        uf = getToolByName(member, 'acl_users')
        plugin = uf['RemOpenId']
        url_map = plugin._url_username_map
        if url_map.has_key(url):
            del url_map[url]
