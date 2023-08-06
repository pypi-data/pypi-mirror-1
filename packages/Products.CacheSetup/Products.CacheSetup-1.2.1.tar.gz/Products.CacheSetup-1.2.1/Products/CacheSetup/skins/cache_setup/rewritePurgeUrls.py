## Script (Python) "rewritePurgeUrls"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=relative_urls,domains
##title=Custom rewrite of purge url paths

# Rewrite the purge URLs in case the request paths passed to the cache proxy 
# are different than the relative URLs in the Zope virtual host context.
# We put this here to make it easier to adjust this behavior for custom
# cache proxy setups.  Two example rewrite behaviors are provided below.
# 
# Example 1: Legacy CacheFu 1.0 Squid-Apache config
# 
# For those who haven't yet updated their old-style squid-apache configs.
# The old default "squid_behind_apache" setup assumed URLs passed
# to Squid from Apache are of the form:
# [squid_url]/[protocol]/[host]/[port]/[path]
# 
# Example 2: VirtualHostMonster-style URLs in the 'inside-out' configuration
# 
# For those using the special _vh_ option for VHM URLs where the root url of
# the plone site is configured as a subfolder of the domain.  The URLs passed
# to the proxy cache server are of the form:
# [squid_url]/VirtualHostBase/[protocol]/[host]:[port]/[zopepath]  \
#            /VirtualHostRoot/_v_[subfolder]/[path]
# See http://plone.org/documentation/tutorial/plone-apache/vhm for details


# Example 1
def rewrite_legacy(relative_urls, domains):
    prefixes = []
    for d in domains:
        protocol = d[0]
        host = d[1]
        split_host = host.split(':')
        host = split_host[0]
        port = split_host[1]
        prefixes.append('%s/%s/%s/' % (protocol, host, port))
    relative_urls = [prefix+url for prefix in prefixes for url in relative_urls]
    return relative_urls


# Example 2
def rewrite_insideout(relative_urls, domains):
    subfolder = 'folder/subfolder'  # change this to match your config.
    from Products.CMFCore.utils import getToolByName
    url_tool = getToolByName(context, 'portal_url')
    portal_path = '/'.join(url_tool.getPortalObject().getPhysicalPath())
    prefixes = []
    for d in domains:
        protocol = d[0]
        host = d[1]
        split_host = host.split(':')
        host = split_host[0]
        port = split_host[1]
        prefixes.append('VirtualHostBase/%s/%s:%s%s/VirtualHostRoot/_vh_%s' % (protocol, host, port, portal_path, subfolder))
    relative_urls = [prefix+url for prefix in prefixes for url in relative_urls]
    return relative_urls


# The default case is example 1
return rewrite_legacy(relative_urls, domains)


