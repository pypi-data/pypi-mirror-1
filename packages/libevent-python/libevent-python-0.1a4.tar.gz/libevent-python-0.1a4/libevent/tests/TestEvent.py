import unittest
import tempfile
import sys
import os
import time
import signal

import libevent

def passThroughEventCallback(fd, events, eventObj):
    return fd, events, eventObj

def makeEvent(fd=0, events=libevent.EV_WRITE):
    return libevent.createEvent(fd, events, passThroughEventCallback)	

class EventConstructionTests(unittest.TestCase):
    def testValidConstructionWithIntegerFd(self):
        event = makeEvent()

    def testEventsGetDefaultEventBase(self):
        event = makeEvent()
        self.assertEqual(event.eventBase, libevent.DefaultEventBase)
        
    def testSettingCustomEventBase(self):
        event = makeEvent()
        newEventBase = libevent.EventBase()
        event.setEventBase(newEventBase)
        self.assertEqual(event.eventBase, newEventBase)
        
    def testInvalidConstructionNonCallableCallback(self):
        self.assertRaises(libevent.EventError, libevent.Event, sys.stdout, 
                          libevent.EV_WRITE, "i'm not a callable, thats fer shure")
        
    def testValidObjectStructure(self):
        event = makeEvent(sys.stdout)
        self.assertEqual(event.fileno(), sys.stdout.fileno())
        self.assertEqual(event.callback, passThroughEventCallback)
        self.assertEqual(event.events & libevent.EV_WRITE, libevent.EV_WRITE)
        self.assertEqual(event.numCalls, 0)

    def testValidConstructionWithFileLikeObject(self):
        fp = tempfile.TemporaryFile()
        event = libevent.Event(fp, libevent.EV_WRITE, passThroughEventCallback)

    def testCreateTimer(self):
        timer = libevent.createTimer(passThroughEventCallback)

    def testTimerFlags(self):
        timer = libevent.createTimer(passThroughEventCallback)
        timer.addToLoop(1)
        self.assertEqual(timer.pending() & libevent.EV_TIMEOUT, True)
        timer.removeFromLoop()
        self.assertEqual(timer.pending() & libevent.EV_TIMEOUT, False)


class EventPriorityTests(unittest.TestCase):
    def testSettingPriority(self):
        e = makeEvent()
        e.setPriority(2)
        self.assertEqual(e.priority, 2)
        
    def testDefaultPriorityIsMiddle(self):
        e = makeEvent()
        self.assertEqual(e.priority, 1)

    def testSettingCustomPriorityCount(self):
        eventBase = libevent.EventBase(numPriorities=420)
        e = eventBase.createEvent(fd=0, events=libevent.EV_READ, callback=passThroughEventCallback)
        self.assertEqual(e.priority, 210)
        
    def testSettingPriorityAfterLoopAdd(self):
        e = makeEvent()
        e.addToLoop()
        e.setPriority(1)
        
class EventLoopSimpleTests(unittest.TestCase):
    def testSimpleEventCallback(self):
        def _callback(fd, events, eventObj):
            os.write(fd, "test")
            eventObj.removeFromLoop()
            os.close(fd)
        fn = tempfile.mktemp()
        fp = file(fn, 'w')
        event = libevent.createEvent(fp, libevent.EV_WRITE, _callback)
        event.addToLoop()
        libevent.loop(libevent.EVLOOP_ONCE)
        data = file(fn).read()
        self.assertEqual(data, "test")
        os.unlink(fn)
        
    def testSimpleTimerCallback(self):
        t = int(time.time())
        cb = lambda fd, events, obj: self.assertEqual(int(time.time())-t, 2)
        timer = libevent.createTimer(cb)
        timer.addToLoop(timeout=2)
        libevent.loop(libevent.EVLOOP_ONCE)

    def testLoopExit(self):
        cb = lambda fd, events, obj: libevent.loopExit(0)
        timer = libevent.createTimer(cb)
        timer.addToLoop(timeout=2)
        libevent.dispatch()
        
    def testSignalHandler(self):
        signalHandlerCallback = lambda signum, events, obj: obj.removeFromLoop()
        signalHandler = libevent.createSignalHandler(signal.SIGUSR1, signalHandlerCallback)
        signalHandler.addToLoop()
        signalSenderCallback = lambda fd, events, obj: os.kill(os.getpid(), signal.SIGUSR1)
        timer = libevent.createTimer(signalSenderCallback)
        timer.addToLoop(1)
        libevent.dispatch()
        # if we get here, it worked - suboptimal way to test this

if __name__=='__main__':
    unittest.main()
