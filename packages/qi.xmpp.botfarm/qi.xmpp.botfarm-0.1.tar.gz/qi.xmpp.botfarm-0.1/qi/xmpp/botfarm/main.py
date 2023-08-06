
from twisted.application import service
from twisted.web import server
from twisted.internet import reactor
import twisted.python.log as log
from sys import stdout, argv

import qi.xmpp.botfarm.config as config
from qi.xmpp.botfarm.xmlConfig import loadConfigFile
from qi.xmpp.botfarm.xmlrpc import XMLRPCServer
from sessionManager import SessionManager


class App:
	def __init__(self):
		"""
		"""
			
		#f = open("helpdesk.log","w")
		
		log.startLogging(stdout)
		
		sessionManager = SessionManager()
		sessionManager.loadAdminSession()

		#Load xmlrpc server
		xrs = XMLRPCServer(sessionManager)
		reactor.listenTCP(config.xmlrpc_port, server.Site(xrs))
		reactor.addSystemEventTrigger('before', 'shutdown', sessionManager.unloadSessions)

def main():
	"""
	"""
	if len(argv)!=2:
		print "You need to specify the configuration file."
		return
	loadConfigFile(argv[1])
	app = App()
	reactor.run()

if __name__ == "__main__":
	main()

