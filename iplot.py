'''Generate interactive plots, so you can (e.g.) use the location of a mouse-click in code.'''
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

class iplot():
	def __init__(self, nRows, nCols, verbose=True, **kwargs):
		# input number of rows and number of columns
		# keep track of messages
		self.verbose = verbose
		self.prefix = '   [i] '
		if self.verbose:
			print self.prefix + 'creating an interactive figure' 
			self.indent()

		# create a gridspec object
		self.gs = gridspec.GridSpec(nRows,nCols,**kwargs)
		self.figure = plt.gcf()
		
		# create an empty dictionary to store axes
		self.axes = {}
		
		plt.show(block=False)

	def indent(self):
		self.prefix = ' ' + self.prefix

	def unindent(self):
		self.prefix = self.prefix[1:]
		
	def subplot(self, row=0, col=0,rowspan=1,colspan=1,name=None, **kwargs):
		# create the axis object, using the gridspec language
		#	for example, 
		
		ax = plt.subplot(self.gs[row:row + rowspan, col:col + colspan], **kwargs)	
		if name == None:
			name = 'ax{0}'.format(len(self.axes))
		self.axes[name] = ax
		if self.verbose:
			print self.prefix + 'added axes at rows {0}-{1} and columns {2}-{3}, named {4}'.format(row,row + rowspan, col,col + colspan,name)
		return ax
	
	def connect(self):
		# connect all the event-handling functions
		#self.figure.canvas.mpl_connect('axes_enter_event', self.onEnterAxes)
		#self.figure.canvas.mpl_connect('axes_leave_event', self.onLeaveAxes)	
		self.cids = []
		self.cids.append(self.figure.canvas.mpl_connect('button_release_event', self.onClick))	

	def onEnterAxes(self, event):
		print 'enter_axes', event.inaxes
		event.inaxes.patch.set_facecolor('yellow')
		event.canvas.draw()
	
	def onLeaveAxes(self, event):
		print 'leave_axes', event.inaxes
		event.inaxes.patch.set_facecolor('white')
		event.canvas.draw()
		
	def onClick(self, event):
		if event.xdata is None:
			print self.prefix + " that wasn't a very nice click. Could you please try again?"
			return
		if self.verbose:
			print self.prefix + ' clicked at {0}, {1}'.format(event.xdata, event.ydata)
		self.lastMouseClick = event

			
		self.mouseClicks.append(event)
		self.remainingClicks -= 1
		if self.remainingClicks <= 0:
			self.stop()
	
	def getMouseClicks(self, n=2):
		# say what's happening
		if self.verbose:	
			print self.prefix + "waiting for {0} mouse clicks.".format(n)
			self.indent()

		# set the countdown for the number of clicks
		self.remainingClicks = n
		self.mouseClicks = []
		
		# start the event handling loop
		self.start()

		self.unindent()
		# return a list of mouse clicks, which the loop should have generated
		return self.mouseClicks
		
	def start(self):
		self.connect()
		plt.draw()
		self.figure.canvas.start_event_loop(0)

	def stop(self):
		self.figure.canvas.stop_event_loop()
		for cid in self.cids:
			self.figure.canvas.mpl_disconnect(cid)	


	



