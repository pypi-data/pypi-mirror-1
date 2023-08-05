#!/exec/products/cocoon/bin/python

import os
import urllib2


def set_proxy(url=None):

	if not url:
		return false
	
	# positionnement du proxy pour http
	proxy_support = urllib2.ProxyHandler({"http" : url ,"https":url})
	opener = urllib2.build_opener(proxy_support)
	urllib2.install_opener(opener)
	return True



