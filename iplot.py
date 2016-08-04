'''Generate interactive plots, so you can (e.g.) use the location of a mouse-click in code.'''
import matplotlib.pyplot as plt
# turn off default key mappings for matplotlib
for k in plt.rcParams.keys():
    if 'keymap' in k:
        plt.rcParams[k] = ''

import matplotlib.gridspec as gridspec
from zachopy.Talker import Talker
class iplot(Talker):
	def __init__(self, nRows, nCols, verbose=True, **kwargs):
		'''initialize as you would a matplotlib.gridspec.GridSpec,
			but it will be interactive too.'''

		# make sure interactive plotting is turned on
		plt.ion()

		Talker.__init__(self)

		# create a gridspec object
		self.gs = gridspec.GridSpec(nRows,nCols,**kwargs)

		# create an empty dictionary to store axes
		self.axes = {}

	def subplot(self, row=0, col=0,rowspan=1,colspan=1,name=None, **kwargs):
		# create the axis object, using the gridspec language
		#	for example,

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
		'''shortcut for mpl_connect'''
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
