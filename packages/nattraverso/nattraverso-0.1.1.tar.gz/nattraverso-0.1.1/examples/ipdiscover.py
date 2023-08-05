"""
Run this script with no arguments, it will attempt to discover your ip address.

python ipdiscover.py 2>/dev/null

If somthing goes wrong, please attach the content of the debug in a file
python ipdiscover.py 2> debug.log

"""
from twisted.internet import defer, reactor

from nattraverso.ipdiscover import get_local_ip, get_external_ip

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%H:%M:%S')
                    
def got_local_ip(result):
	(local_ok, local_result), (external_ok, external_result) = result
	
	if local_ok:
		print 'Result of get_local_ip', local_result
		local, ip = local_result
		if local:
			print "\tLAN IP address:", ip
		else:
			print "\tWAN IP address:", ip
	else:
		print 'Failed to get_local_ip', local_result

	if external_ok:
		print 'Result of get_external_ip', external_result
		wan, ip = external_result
		if wan == None:
			print "\tLocalhost IP address:", ip
		elif not wan:
			print "\tLAN IP address:", ip
		else:
			print "\tWAN IP address:", ip
	else:
		print 'Failed to get_external_ip', external_result
		
list = defer.DeferredList([get_local_ip(), get_external_ip()])
list.addCallback(got_local_ip).addBoth(lambda x:reactor.stop())

print 'Attempting to use get_local_ip() and get_external_ip()'
reactor.run()

