"""
Run this script with no arguments, it will attempt to retreive, show, add and
remove mappings in your upnp device

python portmapper.py 2>/dev/null

If somthing goes wrong, please attach the content of the debug in a file
python portmapper.py 2> debug.log

"""
from twisted.internet import reactor

from nattraverso.portmapper import get_port_mapper

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%H:%M:%S')
    
def got_mappings(mappings):
	print '\tExisting mappings:\n\t', mappings

def on_mapping_removed(result, mapper):
	print '\tMapping removed'
	return mapper.get_port_mappings().addCallback(got_mappings).addErrback(error_occured)
		
def remove_mapping(mapper, port):
	print 'Removing mapping for port', port
	return mapper.unmap(port).addCallback(on_mapping_removed, mapper).addErrback(error_occured)
	
def on_mapping_done(result, mapper, port):
	print '\tNew mapping added for:', port
	return mapper.get_port_mappings().addCallback(
		got_mappings).addCallback(lambda x:remove_mapping(mapper, port)).addErrback(error_occured)
	
def add_mapping(mapper):
	print 'Adding new mapping, faking an http server on port 10333 on this host'
	from twisted.web import server, resource as web_resource
	port = reactor.listenTCP(10333, server.Site(resource=web_resource.Resource()))
	return mapper.map(port).addCallback(on_mapping_done, mapper, port).addErrback(error_occured)
	
def got_port_mapper(mapper):
	print "\tGot port mapper:", mapper
	print "Retreiving existing mappings"
	return mapper.get_port_mappings().addCallback(
		got_mappings).addCallback(lambda x:add_mapping(mapper)).addErrback(error_occured)
	
def error_occured(err):
	print "\tError occured:", err


get_port_mapper().addCallbacks(got_port_mapper,error_occured).addCallback(lambda x:reactor.stop())

print 'Attempting to get_port_mapper()'
reactor.run()
