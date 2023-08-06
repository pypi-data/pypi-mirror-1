import elementtree.ElementTree as ET

import sys, os
import qi.xmpp.botfarm.config as config
def loadConfigFile(configFile):
	# Check the file exists
	if not os.path.isfile(configFile):
		print "Configuration file not found. You need to call botfarm with an xml config file."
		sys.exit(1)

#	global server
	# Get ourself a DOM
	
	try:
		xml = ET.parse(configFile)
		tags = ['server','admin_id','admin_pass','defaultAvatar']
		for tag in tags:
			val =  xml.findtext(tag).strip()
			setattr(config,tag,val)
		setattr(config,"debugLevel",int(xml.findtext("debugLevel")))
		setattr(config,"xmlrpc_port",int(xml.findtext("xmlrpc_port")))
		setattr(config,"connection_timeout",int(xml.findtext("connection_timeout")))
		setattr(config,"filesize_limit",int(xml.findtext("filesize_limit")))
		config.filesize_limit = config.filesize_limit * 1024		
		config.xmlrpc_admin_accept_ips = [elem.text for elem in xml.findall("//xmlrpc_admin_accept_ips/ip")]
	except Exception, e:
		print "Error parsing configuration file: %s" %str(e)
		sys.exit(1)

	


