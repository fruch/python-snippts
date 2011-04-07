import threading
import time

class StopableThreadMixing(threading.Thread):
    def __init__(self, loop_time, sleeping_loop=0.01):
        self.loop_time = loop_time
        self.action_time = loop_time / sleeping_loop
        self.sleeping_loop = sleeping_loop
        threading.Thread.__init__(self)
        
    def start(self, ):
        self.running = True
        self.time = 0
        threading.Thread.start(self)

    def loop_run_seconds(self):
        return (self.time%self.action_time) * self.sleeping_loop

    def _increment_time(self):
        self.time+=1
        self.time=self.time%self.action_time

    def run(self):
        while self.running:
            if self.time == 0:
                self.Action()  
            self._increment_time()
            time.sleep(self.sleeping_loop)

    def stop(self):
        print 'stop'
        self.running = False
        self.join()
        self.Cleanup()

        
class BackgroundRecording(StopableThreadMixing):
    name = "A"
    current_recording = None
    record_list = []

    def __init__(self, service, event_duration_sec=60, event_duration_min=None,*argv, **kwarg):
        if event_duration_min: event_duration_sec = event_duration_min * 60.0
        print "== Event Duration is %dsec==" % event_duration_sec
        StopableThreadMixing.__init__(self, event_duration_sec, *argv, **kwarg)
        self.service = service

    def Action(self):
        if self.current_recording:
            print "== Stop Record: %s ==" % self.current_recording
        self.current_recording = "Event%s" % self.name
        self.record_list.append(self.current_recording)
        self.name = chr (ord(self.name) + 1)
        
        print "== Start Record:%s ==" % self.current_recording

    def Cleanup(self):
        print 'cleanup'
        if self.current_recording:
            print "== Stop Record: %s ==" % self.current_recording
        print self.record_list
        print self.loop_run_seconds()

if __name__ == "__main__":
    t = BackgroundRecording("MSL.MSL_MASTER_SRV_19", event_duration_min=0.25)

    t.start()
    time.sleep(45)
    t.stop()