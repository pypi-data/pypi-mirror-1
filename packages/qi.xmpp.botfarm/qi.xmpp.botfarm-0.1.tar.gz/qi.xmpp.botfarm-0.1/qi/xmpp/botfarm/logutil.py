from twisted.python import log
from twisted.words.protocols.jabber import component

import sys, time

import qi.xmpp.botfarm.config as config
class INFO : pass
class WARN : pass
class ERROR: pass
log.discardLogs()
class LogEvent:
	def __init__(self, category=INFO, ident="", msg="", log=True):
		self.category, self.ident, self.msg = category, ident, msg
		frame = sys._getframe(1)
		# Get the class name
		s = str(frame.f_locals.get("self", frame.f_code.co_filename))
		self.klass = s[s.find(".")+1:s.find(" ")]
		self.method = frame.f_code.co_name
		self.args = frame.f_locals
		if log:
			if category == INFO and config.debugLevel < 3:
				return
			if category == WARN and config.debugLevel < 2:
				return
			if category == ERROR and config.debugLevel < 1:
				return
			self.log()
	
	def __str__(self):
		args = {}
		for key in self.args.keys():
			if key == "self":
				args["self"] = "instance"
				continue
			val = self.args[key]
			args[key] = val
			try:
				if len(val) > 128:
					args[key] = "Oversize arg"
			except:
				# If its not an object with length, assume that it can't be too big. Hope that's a good assumption.
				pass
		category = str(self.category).split(".")[1]
		#return "%s :: %s :: %s :: %s :: %s :: %s" % (category, str(self.ident), self.msg, self.method, str(self.klass), str(args))
		return "%s :: %s :: %s\n" % (category, str(self.ident), self.msg)
	def log(self):
		log.msg(self)

