# AsynCluster: Master
# A cluster management server based on Twisted's Perspective Broker. Dispatches
# cluster jobs and regulates when and how much each user can use his account on
# any of the cluster node workstations.
#
# Copyright (C) 2006-2008 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
An all-powerful Controller object and a UNIX socket PB interface to it.
"""

from twisted.python.failure import Failure
from twisted.python.reflect import namedObject
from twisted.internet import defer, reactor, task
from twisted.spread import pb

from asynqueue import jobs
import database


UNRESTRICTED_LOGIN_HOURS = 10.0


def log(msgProto, nodeID, *args):
    """
    Logs a message based on the supplied message prototype about some
    particular node and, if specified as a third argument, some particular
    user. Any arguments beyond the first three are applied to string
    substitution of the message prototype.
    """
    msg = "N%04d" % nodeID
    if args:
        msg = "%s (%s): %s" % (msg, args[0], msgProto)
        if len(args) > 1:
            msg = msg % args[1:]
    else:
        msg = "%s: %s" % (msg, msgProto)
    print msg


class RemoteCallError(Exception):
    """
    A remote call raised an exception.
    """


class SessionManager(pb.Viewable):
    """
    This viewable permits a node client to begin and end user access sessions.
    
    @ivar t: An L{AccessBroker} object that manages user session data.
    
    """
    updateInterval = 30.0
    updateFirstDelay = 1.0
    
    def __init__(self, ctl):
        self.ctl = ctl
        self.sessionMap = {}
        url = self.ctl.config['server']['database']
        self.t = database.UserDataTransactor(url)
        self.looper = task.LoopingCall(self._update)
        self.d = self.looper.start(self.updateInterval, now=True)

    def _update(self):
        dList = []
        # We use 'keys' rather than 'iterkeys' because we may be modifying the
        # sessionMap dict from within the loop.
        for ID in self.sessionMap.keys():
            userID, hoursLeft = self.sessionMap[ID]
            hoursLeft -= float(self.updateInterval) / 3600.0
            self.sessionMap[ID][1] = hoursLeft
            log("%f hours now left", ID, userID, hoursLeft)
            if hoursLeft >= 0.0:
                d = self.ctl.nodeRemote(ID, 'setTimeLeft', hoursLeft)
            else:
                d = self.end(ID)
            d.addCallback(
                lambda _:
                log("Done updating client", ID, userID))
            dList.append(d)
        return defer.DeferredList(dList)
    
    def view_begin(self, node, userID, password):
        """
        Begins a user access session for the specified I{node} perspective and
        the specified I{userID} and I{password}.

        @return: A (possibly deferred) boolean indicating whether the
          session is authorized and was started.
        
        """
        def gotAuthorizationResult(authorized):
            if not authorized:
                log("Unauthorized session attempt", node.ID, userID)
                return False
            if ID is None:
                d = defer.succeed(None)
            else:
                log("Replacing session with one on N%02d", ID, userID, node.ID)
                d = defer.maybeDeferred(self.end, ID)
            d.addCallback(lambda _: self.t.restricted(userID))
            d.addCallback(gotRestrictionResult)
            return d
        
        def gotRestrictionResult(restricted):
            if not restricted:
                log("Unrestricted session started", node.ID, userID)
                self.sessionMap[node.ID] = [userID, UNRESTRICTED_LOGIN_HOURS]
                return True
            d = self.t.sessionStart(userID)
            d.addCallback(gotHoursAvailable)
            return d

        def gotHoursAvailable(hours):
            if hours <= 0.0:
                log("No usage time available", node.ID, userID)
                return False
            self.sessionMap[node.ID] = [userID, hours]
            log("Session started, %f hours left", node.ID, userID, hours)
            self.t.recordSessionStartTime(userID)
            return True
        
        for ID, info in self.sessionMap.iteritems():
            if info[0] == userID:
                break
        else:
            ID = None
        d = self.t.sessionAuthorized(userID, password)
        d.addCallback(gotAuthorizationResult)
        return d

    def view_timeLeft(self, node):
        """
        """
        if node.ID in self.sessionMap:
            userID, hoursLeft = self.sessionMap[node.ID]
            log("%f hours left", node.ID, userID, hoursLeft)
            return hoursLeft
        return 0.0
    
    def view_end(self, node):
        """
        Ends the current user access session for the specified I{node}
        perspective.

        See L{end}.
        """
        return self.end(node.ID, callClient=False)

    def end(self, ID, callClient=True):
        """
        Ends the current user access session for the specified node I{ID}.
        """
        if ID not in self.sessionMap:
            d = defer.succeed(None)
        else:
            userID, hoursLeft = self.sessionMap.pop(ID)
            log("Ending session with %f hours left", ID,  userID, hoursLeft)
            d = self.t.sessionEnd(userID)
            if callClient:
                d.addCallback(
                    lambda _: self.ctl.nodeRemote(ID, 'setTimeLeft', 0.0))
        return d


class Controller(object):
    """
    I control everything, I{heh heh heh...}

    @ivar nodes: A dict of tuples, keyed by node client ID, where each tuple
      contains the local perspective instance and remote root reference for one
      node client.
    
    """
    def __init__(self, config):
        self.config = config
        self.counter = 0
        self.nodes = {}
        self.jobber = jobs.JobManager()

    def getSessionManager(self):
        """
        Returns references to a single instance of the L{SessionManager}
        viewable.
        """
        if not hasattr(self, 'sessionManager'):
            self.sessionManager = SessionManager(self)
        return self.sessionManager

    def attachNode(self, nodePerspective, nodeRoot):
        """
        Call when another mutually authenticated node client has
        connected. Attaches its root referenceable to my map of node roots
        under a new integer ID, then has the node spawn as many child worker
        clients as needed to keep all of its cores occupied.

        Returns a deferred that fires with the node ID when all the spawning is
        done.
        """
        self.counter += 1
        # Use a local copy of counter so it is unchanged when the callback
        # fires
        counter = self.counter
        self.nodes[counter] = nodePerspective, nodeRoot
        d = nodeRoot.callRemote('spawnWorkers')
        return d.addCallback(lambda _: counter)

    def detachNode(self, ID):
        """
        A node client has disconnected, so detach its root referenceable from
        my map of node roots.
        """
        self.nodes.pop(ID, None)
        if hasattr(self, 'sessionManager'):
            return self.sessionManager.end(ID, callClient=False)

    def attachWorker(self, nodeRoot):
        """
        Call when another mutually authenticated worker client has
        connected. Attaches its root referenceable to my jobber and returns a
        deferred that fires with a new integer ID as assigned by the jobber.
        """
        N = int(self.config['server']['jobs'])
        return self.jobber.attachChild(nodeRoot, N)

    def detachWorker(self, ID):
        """
        A worker client has disconnected, so detach it from the jobber.
        """
        return self.jobber.detachChild(ID)
    
    def _remoteError(self, failure, ID):
        if failure.check(pb.DeadReferenceError, pb.PBConnectionLost):
            return self.sessionManager.end(ID, callClient=False)
        return failure
    
    def nodeRemote(self, nodeID, called, *args, **kw):
        """
        Runs a remote call to the object specified by the string I{called} on
        the node identified by the integer I{nodeID}, supplying any provided
        arguments or keywords.

        Returns a deferred that fires with the result of the remote call.
        """
        if nodeID not in self.nodes:
            return defer.fail(Failure(
                RemoteCallError("Invalid node '%s'" % nodeID)))
        nodeRoot = self.nodes[nodeID][1]
        d = nodeRoot.callRemote(called, *args, **kw)
        d.addErrback(self._remoteError, nodeID)
        return d
    
    def userRemote(self, userID, called, *args, **kw):
        """
        Calls the object specified by the string I{called} on the node on which
        the user identified by the string I{userID} has an active session,
        supplying any provided arguments or keywords.

        Returns a deferred that fires with the result of the remote call.
        """
        for ID, nodeStuff in self.nodes.iteritems():
            nodePerspective, nodeRoot = nodeStuff
            if getattr(nodePerspective, 'userID', None) == userID:
                d = nodeRoot.callRemote(called, *args, **kw)
                d.addErrback(self._remoteError, ID)
                return d
        return defer.fail(Failure(
            RemoteCallError("Invalid user '%s'" % userID)))

    def allRemote(self, called, *args, **kw):
        """
        Runs a remote call to the object specified by the string I{called} on
        all connected nodes, supplying any provided arguments or keywords.

        Returns a deferred that fires with a list of results of the remote
        calls, in no particular node order.
        """
        dList = []
        for ID, nodeStuff in self.nodes.iteritems():
            d = nodeStuff[1].callRemote(called, *args, **kw)
            d.addErrback(self._remoteError, ID)
            dList.append(d)
        return defer.gatherResults(dList)


class Root(pb.Root):
    """
    I am the root object that each control client receives upon making its UNIX
    socket connection to the master control server.

    All of the heavy lifting is done by an instance of L{Controller}, a
    reference to which is supplied to my constructor.
    """
    def __init__(self, ctl):
        self.ctl = ctl

    def remote_userAction(self, userID, action, actionArg=None):
        """
        Carries out the specified I{action} concerning the user account
        I{userID}. If the action requires an argument, it is supplied as the
        I{actionArg} option.

        The actions are as follows:
            - B{password}: use the supplied string as the password
            - B{disable}: disable the account
            - B{disable}: enable the account
            - B{msg}: send the supplied string to the user as a pop-up message
            - B{kick}: kick the user off the system, disabling his account
            
        """
        t = self.ctl.getSessionManager().t
        if action == 'password':
            d = t.password(userID, actionArg)
        elif action == 'disable':
            d = t.enabled(userID, False)
        elif action == 'enable':
            d = t.enabled(userID, True)
        elif action == 'restrict':
            d = t.restricted(userID, True)
        elif action == 'unrestrict':
            d = t.restricted(userID, False)
        elif action == 'msg':
            d = self.ctl.userRemote(userID, 'message', actionArg)
        elif action == 'kick':
            d = self.ctl.userRemote(userID, 'kick')
        else:
            return "INVALID COMMAND '%s'" % action
        d.addCallbacks(lambda _: "OK", lambda _: "FAIL")
        return d

    def remote_registerClasses(self, *args):
        """
        Instructs my broker to register the classes specified by the
        argument(s) as self-unjellyable and allowable past PB security, and
        instructs the jobber to have all current and future nodes do the same
        with their brokers.
        
        The classes are specified by their string representations::
        
            <package(s).module.class>

        Use judiciously!
        """
        for stringRep in args:
            cls = namedObject(stringRep)
            pb.setUnjellyableForClass(stringRep, cls)
        return self.ctl.jobber.registerClasses(*args)

    def remote_newJob(self, jobCode, niceness=0):
        """
        Registers a new computing job with the supplied I{jobCode}, returning a
        deferred to an integer jobID identifying the job.

        See L{jobs.JobManager.new}.
        """
        return self.ctl.jobber.new(jobCode, niceness)

    def remote_updateJob(self, jobID, callName, *args, **kw):
        """
        Updates the job specified by I{jobID} by arranging to dispatch a call
        to the callable object specified in the job's namespace on each node
        before it runs another call for that job.
        """
        return self.ctl.jobber.update(jobID, callName, *args, **kw)

    def remote_runJob(self, jobID, callName, *args, **kw):
        """
        Queues up a call to the callable object specified in the namespace of
        the specified I{jobID}. The call will be dispatched to the next node
        that is qualified and becomes available to run it.

        See L{jobs.JobManager.run}.

        @param jobID: An image identifying the namespace of a job previously
            registered on one or more of the nodes.

        @param callName: A string identifying a callable object in the job
            namespace.

        @*args: Any arguments to pass to the callable object.

        @**kw: Any keywords to pass to the callable object.

        @return: A deferred to the eventual result of the dispatch when it
            eventually runs on a qualified node.

        """
        return self.ctl.jobber.run(jobID, callName, *args, **kw)

    def remote_cancelJob(self, jobID):
        """
        Cancels the job specified by I{jobID}.
        """
        return self.ctl.jobber.cancel(jobID)

    def remote_resetup(self, sourcePath):
        """
        Instructs each connected node to do a new python setup in the specified
        I{sourcePath} and respawn its coeterie of child worker process.

        Terminates upon encountering any problems with the setup runs.

        Returns a deferred that fires with C{True} if all went well, C{False}
        if there were any problems.
        """
        def next(successCodes):
            for success in successCodes:
                if not success:
                    return False
            d = self.ctl.allRemote('spawnWorkers', True)
            d.addCallbacks(lambda _: True, lambda _: False)
            return d
        
        d = self.ctl.allRemote('bash', "cd %s; python setup.py install")
        return d.addCallback(next)
        
        
