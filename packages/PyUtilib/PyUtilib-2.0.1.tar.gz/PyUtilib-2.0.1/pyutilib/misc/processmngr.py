#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the PyUtilib README.txt file.
#  _________________________________________________________________________

__all__ = ['subprocess', 'SubprocessMngr', 'run_command', 'timer', 'signal_handler']

import GlobalData
import time
import signal
import os
import sys
import tempfile

if sys.version_info[0:2] < (2,4): #pragma:nocover
   print "WARNING: EXACT requires Python 2.4 or newer for robust process control."
   if (sys.platform[0:3] == "win"):
      raise OSError, "ERROR:   Aborting since we're on windows."
   print "WARNING: Using a dummy subprocess mechanism that does not support timelimits."
   import commands
else:
   import subprocess


#
# Note: the DummySubprocess.stdout file handle is closed the next time
# that Popen is called.  This occurs because Popen returns a pointer to 'self'.
#
class DummySubprocess:
    def __init__(self):
        """
        Initialize this object to have data like a subprocess module.
        """
        self.PIPE="pipe"
        self.STDOUT="stdout"
        self.mswindows = (sys.platform[0:3] == "win")
        self.tempfile = None
        self.stdout = None

    def __del__(self):
        """
        Cleanup temporary file descriptor and delete that file.
        """
        self.close()

    def close(self):
        """
        Cleanup temporary file descriptor and delete that file.
        """
        if self.stdout is not None:
           self.stdout.close()
        if self.tempfile is not None:
           os.unlink(self.tempfile)

    def Popen(self, cmd,shell,stdout,stderr,preexec_fn):
        """
        Open a pipe'd stream, and setup self.stdout to be a file descriptor
        for the output pipe.
        """
        if self.tempfile is not None:
           self.close()
        if stdout != "pipe":
           raise IOError, "BUG: need to support other types of stdout"
        (fhandle, self.tempfile) = tempfile.mkstemp(prefix="exact_",dir="/tmp")
        os.close(fhandle)
        (self.status,self.output) = commands.getstatusoutput(cmd.strip() + " > " + self.tempfile + " 2>&1")
        self.stdout = open(self.tempfile,"r")
        return self

    def wait(self, timelimit=None):
        """
        We're using the commands module, so nothing needs to be done in wait().
        """
        return self.status

    def poll(self):
        """
        Return the status returned by getstatusoutput().
        """
        return self.status


if sys.version_info[0:2] < (2,4):
   subprocess = DummySubprocess()

if sys.version_info[0:2] >= (2,5):
   import ctypes

def kill_process(pid, sig=signal.SIGTERM):
    """
    Kill a process given a process ID
    """
    if subprocess.mswindows:
       if sys.version_info[0:2] < (2,5):
         os.system("taskkill /t /f /pid "+`pid`)
       else:
         PROCESS_TERMINATE = 1
         handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
         ctypes.windll.kernel32.TerminateProcess(handle, -1)
         ctypes.windll.kernel32.CloseHandle(handle)
    else:
       #
       # Kill process and all its children
       #
       if GlobalData.debug:
          print "Killing process",pid,"with signal",sig
       os.kill(pid,sig)


GlobalData.current_process=None
GlobalData.signal_handler_busy=False
#
# A signal handler that passes on the signal to the child process.
#
def signal_handler(signum, frame):
        #c = frame.f_code
        #print '  Called from ', c.co_filename, c.co_name, frame.f_lineno
        if GlobalData.signal_handler_busy:
           print ""
           print "  Signal handler is busy.  Aborting."
           sys.exit(-signum)
        if GlobalData.current_process is None:
           print "  Signal",signum,"recieved, but no process queued"
           print "  Exiting now"
           sys.exit(-signum)
        if GlobalData.current_process is not None and\
           GlobalData.current_process.pid is not None and\
           GlobalData.current_process.poll() is None:
           GlobalData.signal_handler_busy=True
           kill_process(GlobalData.current_process.pid, signum)
           print "  Signaled process", GlobalData.current_process.pid,"with signal",signum
           print "  Waiting...",
           endtime = timer()+15.0
           while timer() < endtime:
             status = GlobalData.current_process.poll()
             if status is None:
                break
             time.sleep(0.1)
           GlobalData.current_process.wait()
           status = GlobalData.current_process.poll()
           if status is not None:
              print "Done."
              raise OSError, "Interrupted by signal " + `signum`
           else:
              raise OSError, "Problem terminating process" + `GlobalData.current_process.pid`
        raise OSError, "Interrupted by signal " + `signum`

#
# Run a command line
#
def run_command(cmd,outfile=None,cwd=None):
    if cwd is not None:
       oldpwd = os.getcwd()
       os.chdir(cwd)
    if sys.version_info[0:2] < (2,4):
       sys.stdout.flush()
       if outfile is None:
          commands.getoutput(cmd.strip())
       else:
          commands.getoutput(cmd.strip() + " > " + outfile + " 2>&1")
    else:
       #
       # Execute the command as a subprocess that we can send signals to.
       # After this is finished, we can get the output from this command from
       # the process.stdout file descriptor.
       #
       if outfile is not None:
          OUTPUT=open(outfile,"w")
       try:
         if outfile is not None:
            GlobalData.current_process = subprocess.Popen(cmd.strip(),shell=True,stdout=OUTPUT,stderr=subprocess.STDOUT)
         else:
            GlobalData.current_process = subprocess.Popen(cmd.strip(),shell=True)
         GlobalData.current_process.wait()
         GlobalData.current_process = None
       except OSError:
         #
         # Ignore IOErrors, which are caused by interupts
         #
         pass
       if outfile is not None:
          OUTPUT.close()
    if cwd is not None:
       os.chdir(oldpwd)

#
# Setup the timer
#
if subprocess.mswindows:
   timer = time.clock
else:
   timer = time.time

#
# Setup a '/dev/null' file descriptor that can be used to ignore output.
#
if subprocess.mswindows:
   IGNORE = open('NUL:','w')
else:
   IGNORE = open('/dev/null','w')



class SubprocessMngr:
    def __init__(self, cmd, stdout=None, stderr=None, env=None):
        """
        Setup and launch a subprocess
        """
        self.process = None
        #
        # By default, stderr is mapped to stdout
        #
        if stderr is None:
           stderr=subprocess.STDOUT
        #
        # Launch subprocess using a subprocess.Popen object
        #
        if subprocess.mswindows:
           #
           # Launch without console on MSWindows
           #
           startupinfo = subprocess.STARTUPINFO()
           startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
           self.process = subprocess.Popen(cmd.strip(), stdout=stdout, stderr=stderr, startupinfo=startupinfo, env=env)
        else:
           #
           # Launch on *nix
           #
           self.process = subprocess.Popen(cmd.strip(), shell=True, stdout=stdout, stderr=stderr, preexec_fn=os.setsid, env=env)

    def __del__(self):
        """
        Cleanup temporary file descriptor and delete that file.
        """
        if self.process is not None:
           try:
              if self.process.poll() is None:
                 self.kill()
           except OSError:
              #
              # It should be OK to ignore this exception.  Although poll() returns
              # None when the process is still active, there is a race condition
              # here.  Between running poll() and running kill() the process
              # may have terminated.
              #
              pass
        if self.process is not None:
           del self.process

    def wait(self, timelimit=None):
        """
        Wait for the subprocess to terminate.  Terminate if a specified
        timelimit has passed.
        """
        if timelimit is None:
           return self.process.wait()
        else:
           #
           # Wait timelimit seconds and then force a termination
           #
           # Sleep every 1/10th of a second to avoid wasting CPU time
           #
           if timelimit <= 0:
              raise ValueError, "'timeout' must be a positive number"
           endtime = timer()+timelimit
           while timer() < endtime:
             status = self.process.poll()
             if status is not None:
                return status
             time.sleep(0.1)
           #
           # Check one last time before killing the process
           #
           status = self.process.poll()
           if status is not None:
              return status
           #
           # If we're here, then kill the process and return an error
           # returncode.
           #
           try:
             self.kill()
             return -1
           except OSError:
             #
             # The process may have stopped before we called 'kill()'
             # so check the status one last time.
             #
             status = self.process.poll()
             if status is not None:
                return status
             else:
                raise OSError, "Could not kill process " + `self.process.pid`

    def stdout(self):
        return self.process.stdout

    def send_signal(self, sig):
        """
        Send a signal to a subprocess
        """
        os.signal(self.process,sig)
        
    def kill(self, sig=signal.SIGTERM):
        """
        Kill the subprocess and its children
        """
        kill_process(self.process.pid, sig)


if __name__ == "__main__": #pragma:nocover
   if not subprocess.mswindows:
      foo = SubprocessMngr("ls *py")
      foo.wait()
      print ""

      foo = SubprocessMngr("ls *py", stdout=subprocess.PIPE)
      foo.wait()
      for line in foo.process.stdout:
        print line,
      print ""
   else:
      foo = SubprocessMngr("cmd /C \"dir\"")
      foo.wait()
      print ""

   stime = timer()
   foo = SubprocessMngr("python -c \"while True: pass\"")
   foo.wait(10)
   print "Ran for " + `timer()-stime` + " seconds"
