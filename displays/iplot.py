'''
Generate interactive plots, so you can (for example)
use the location of a mouse-click in code.

This is basically a wrapper for matplotlib's event handling
capabilities, but it's easier for me to remember it in the
way I have it organized here. You create a multipanel plot
using the basic gridspec specification, and then you can connect
to event tracking within any of those panels.'''

'''
WATCH OUT! On Mac OSX Sierra (at least), the matplotlib 'macosx' backend
doesn't really work properly. You can catch mouse-clicks, but not key-presses,
kind of as though the figure is permanently in the background, relative to
your terminal.

(see https://matplotlib.org/faq/osx_framework.html)

This boils down to running

conda install python.app

and using "pythonw" instead of "python" to run scripts.
'''


'''
Check out matplotlib github issue #9795 (Backend switching)
for discussion
'''
'''
OR WAIT!

Another alternative is to force it to use the 'qt5Agg' backend for making
interactive plots, as is done here.
'''

import matplotlib.pyplot as plt
plt.switch_backend('qt5Agg')

import matplotlib.gridspec as gridspec

from ..Talker import Talker

# turn off default key mappings for matplotlib
# otherwise they may overlap with your custom ones
for k in plt.rcParams.keys():
    if 'keymap' in k:
        plt.rcParams[k] = ''


class iplot(Talker):
	'''an interactive (multipanel) plot, built on gridspec'''

	def __init__(self, nRows, nCols, verbose=True, **kwargs):
		'''initialize as you would a matplotlib.gridspec.GridSpec,
			but it will be interactive too.'''

		Talker.__init__(self)

		# make sure interactive plotting is turned on
		plt.ion()

		# create a gridspec object
		self.gs = gridspec.GridSpec(nRows,nCols,**kwargs)

		# create an empty dictionary to store axes
		self.axes = {}

	def subplot(self, row=0, col=0,rowspan=1,colspan=1, name=None, **kwargs):
		# create the axis object, using the gridspec language

		ax = plt.subplot(self.gs[row:row + rowspan, col:col + colspan], **kwargs)
		self.figure = plt.gcf()
		if name == None:
			name = 'ax{0}'.format(len(self.axes))
		self.axes[name] = ax

		return ax

	def onKeyPress(self, event):
		'''when a keyboard button is pressed, record the event'''
		self.keypressed = event
		if self.whenpressed is not None:
			self.whenpressed(self.keypressed)
		self.stop()

	def onKeyRelease(self, event):
		'''when a keyboard button is released, stop the loop'''
		self.keyreleased = event
		self.stop()

	def onEnterAxes(self, event):
		#print 'enter_axes', event.inaxes
		event.inaxes.patch.set_facecolor('yellow')
		event.canvas.draw()

	def onLeaveAxes(self, event):
		#print 'leave_axes', event.inaxes
		event.inaxes.patch.set_facecolor('white')
		event.canvas.draw()

	def onClick(self, event):
		if event.xdata is None:
			self.speak("Hmmm, that wasn't a very nice click. Could you please try again?")
			return
		self.lastMouseClick = event


		self.mouseClicks.append(event)
		self.remainingClicks -= 1
		if self.remainingClicks <= 0:
			self.stop()

	def getMouseClicks(self, n=2):
		# say what's happening
		self.speak("waiting for {0} mouse clicks.".format(n))

		# set the countdown for the number of clicks
		self.remainingClicks = n
		self.mouseClicks = []

		# start the event handling loop for mouse button releases
		self.cids = [self.watchfor('button_release_event', self.onClick)]
		self.startloop()

		# return a list of mouse clicks, which the loop should have generated
		return self.mouseClicks

	def getKeyboard(self, whenpressed=None):
		'''wait for a keyboard press and release.

			whenpressed can be a function that will be called on
			the key press (before the key release); it must be
			able to take a KeyEvent as an argument'''

		# warn what's happening
		self.speak('waiting for a key to be pressed and released')
		# start the loop
		self.cids = [self.watchfor('key_press_event', self.onKeyPress)]

		# this function will be called when the key is pressed
		self.whenpressed = whenpressed

		# start the loop (it'll end when key is pressed)
		self.startloop()
		self.speak('"{}" pressed at {}, {}'.format(self.keypressed.key, self.keypressed.xdata, self.keypressed.ydata))

		# return the key that was pressed
		return self.keypressed

	def watchfor(self, *args):
		'''This is a shortcut for mpl_connect.

            For example,
                self.watchfor('key_press_event', self.onKeyPress)
            will set up a connection that will cause the function
            self.onKeyPress to be called (and passed a KeyEvent) when
            a key_press_event occurs.'''
		return self.figure.canvas.mpl_connect(*args)

	def stopwatching(self, cids):
		'''shortcut to stop watching for particular events'''
		for cid in cids:
			self.figure.canvas.mpl_disconnect(cid)

	def startloop(self):
		'''start the event loop'''
		self.figure.canvas.start_event_loop(0)

	def stoploop(self):
		'''stop the event loop'''
		self.figure.canvas.stop_event_loop()

	def stop(self):
		'''stop the loop, and disconnect watchers'''
		self.stoploop()
		self.stopwatching(self.cids)

def test():
    import numpy as np
    i = iplot(1,1)
    i.subplot(0,0)
    a = i.axes['ax0']
    a.plot(np.random.normal(0,1,10))
    plt.draw()
    key = i.getKeyboard()
    print(key)
    return key
#print(i.getKeyboard(2))
