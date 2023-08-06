Introduction
============

CacheFu speeds up Plone sites transparently using a combination 
of memory, proxy, and browser caching. Can be used by itself or 
with Squid, Varnish, and/or Apache. Once installed, your site
should run much faster (~10x faster by itself, ~50x faster with squid).

CacheFu is a collection of products and recipes.  The central 
product is Products.CacheSetup which when installed via easy_install
or buildout takes care of pulling in the rest of the products from
the bundle.

The full bundle includes:

 * Products.CacheSetup

 * Products.CMFSquidTool

 * Products.PageCacheManager

 * Products.PolicyHTTPCacheManager

Additional optional components include some Squid, Varnish, and
Apache configuration helpers.  See the installation instructions
for more info about these.

The latest information about releases can be found at 
http://plone.org/products/cachefu

CacheFu has been tested with Plone 2.5+ and Plone 3.0.
For earlier Plone versions, try the CacheFu 1.0.3 bundle 
instead.

