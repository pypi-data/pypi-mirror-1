# python modules
import signal


def Startup(event):

	# needed for calling external applications via sys.popen
	signal.signal(signal.SIGCHLD, signal.SIG_DFL)