import scheduler
import datetime
import time
import logging

# TODO: move to a debug util
def DebugON(name):
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
DebugON("secheduler")

import code
import readline
import atexit
import os
	
Channels = {
	"Clear Ch.1": { "num": 110, "desc":"5 min event, no audio" },
	"Clear Ch.2": { "num": 120, "desc":"5 min event, no audio" },
	"Scrambled Ch.1": { "num": 130, "desc":"5 min event, no audio" },
	"Scrambled Ch.2": { "num": 140, "desc":"5 min event, no audio" },
}

class ActionList(object):
	
	def __init__(self):
		self.my_scheduler = scheduler.Scheduler()
		self.action_list = []
		self.receipt_list = []
		self.timeout = 100
	def AddAction(self, action):
		self.action_list.append(action)
	def setStartTime(self, time):
		self.start_time = time
		
	def DoActions(self):
		#todo order action by time.
		for act in self.action_list:
			foo_task = scheduler.Task(act.name ,
							  self.start_time + datetime.timedelta(seconds=act.time_offset) , 
							  lambda x: None, 
							  scheduler.RunOnce(act.Run))
			self.receipt_list.append( self.my_scheduler.schedule_task(foo_task) )
		self.my_scheduler.start()
		print "started"
		#self.my_scheduler.join()
		#print "after join"
	def isFinished(self):
		return not self.my_scheduler.isAlive()
		 
	def __str__(self):
		ret = ""
		for a in self.action_list:
			ret += "%s -%s - %s - %s\n" % (a.name, a.params ,self.start_time + datetime.timedelta(seconds=a.time_offset), a.done)
		return ret 
		
Actions = ActionList()

class Action(object):
	loop = 0
	
	def __init__(self, name, func, params, offset=None):
		self.name = name
		self.params = params
		self.time_offset = offset
		self.func = func
		self.done = False
	def Run(self):
		stat = self.func(*self.params)
		self.done = True
		self.ret_val = stat
	def __unicode__(self):
		print self.name

class Anchor(object):
    def __init__(self, name):
        self.name = name
        
class AnchorList(list):
    pass
Anchors = AnchorList()

class PVR_api(object):
	
	@staticmethod
	def StartLive(channel):
		print channel
		print datetime.datetime.now()
	def BookEvent(self, channel, offset=None, time=None):
		print channel, offset
		print datetime.datetime.now()
		
PVR = PVR_api()

class Testing_api(object):
	current_time = 0
	current_test = ""
	def Init(self, name):
		#set current test name
		self.current_test = name
		
	def Do(self, action, params, time):
		self.current_time += time
		Actions.AddAction(  Action(action.__name__, action, params, self.current_time) )		
	
	def DoList(self, action, params, time):
		self.current_time += time
		Actions.AddAction(  Action(action.__name__, action, params, self.current_time) )		

	def DoAt(self, action, params, time):
		self.current_time += time
		Actions.AddAction(  Action(action.__name__, action, params, time) )
	def getNextRoundTime(self, num=5):
		curr = datetime.datetime.now()
		x = curr.minute % int(num)
		if x > 0:
			ad = num - x
		else:
			ad = num
		return curr.replace(second=0, microsecond=001000) + datetime.timedelta(minutes=ad)
	def Run(self):
		print "Running:\n %s" % (self.current_test,)
		Actions.setStartTime( self.getNextRoundTime() )
		print Actions
		Actions.DoActions()
	
TEST = Testing_api()
Test_List = ["Test_01","Test_02","Test_03",]  
Command_List = ["stat", "quit"] 
def completer(text, state):
	l = []
	for i in Test_List+Command_List:
		if text in i:
			l.append(i)
	return l[int(state)]
	
def Test_01():

	TEST.Init("Test 01 - Start live based on time")
	
	TEST.Do( PVR.StartLive, ("Clear Ch.1", ), 5 )
	
	TEST.Do( PVR.StartLive, ("Clear Ch.2", ), 15 )
	
	TEST.DoAt( PVR.BookEvent, ("Clear Ch.4", 2) , 20 )

con = code.InteractiveConsole()
readline.parse_and_bind("tab: complete")
readline.set_completer(completer)
Test_01()
TEST.Run()
fini = False
while not Actions.isFinished(): 
    input = con.raw_input()
    if input in Test_List:
        exec(input)
        TEST.Run()
    if input == "stat":
        print Actions
    if input == "quit":
        break