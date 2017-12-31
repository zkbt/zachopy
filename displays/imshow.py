from .Display import *
class imshow(Display):
    '''Display 2D image with imshow.'''
    def __init__(self, image, ax=None, **kwargs):
        '''Initialize an imshow display, using one image to set the scale.'''

        # initialize the inherited display
        Display.__init__(self)
        self.initialize(image, **kwargs)

    @property
    def label(self):
        try:
            assert(self.name != '')
            return self.name.replace(' ','')
        except:
            return 'x{0:.0f}_{1:.0f}_y{2:.0f}_{3:.0f}'.format(self.xlim[0], self.xlim[1], self.ylim[0], self.ylim[1])

    def update(self, image, xlabel='', ylabel='', output=None):
        # try to update the data within the existing plots (faster), otherwise
        zoomed = image[self.ylim[0]:self.ylim[1], self.xlim[0]:self.xlim[1]]
        # readjust things if a log scale is set
        if self.log:
            zoomedtoplot = logify(zoomed)
            imagetoplot = logify(image)
        else:
            zoomedtoplot = zoomed
            imagetoplot = image
        # calculate summed histograms
        xhist = np.sum(zoomed, 0)
        yhist = np.sum(zoomed, 1)

        self.current['image'].set_data(zoomedtoplot)
        self.current['navigator'].set_data(imagetoplot)
        self.current['xhist'].set_ydata(xhist)
        self.current['yhist'].set_xdata(yhist)
        self.speak('replaced existing image with new one')
        self.ax['image'].set_xlabel(xlabel, fontsize=8)
        self.ax['image'].set_ylabel(ylabel, fontsize=8)

        #plt.draw()
        if output is None:
            pass
        else:
            chunks = output.split('/')
            chunks[-1] = self.label + '_'+chunks[-1]
            filename = '/'.join(chunks)
            self.figure.savefig(filename)
            self.speak('saved plot to {0}'.format(filename))

    def initialize(self, image, customize=True, xlim=None, ylim=None, xlabel='', ylabel='', log=True, vmin=None, vmax=None, maxresolution=1280, **kwargs):
        '''Display one image, give user a chance to zoom in, and leave everything set for populating with later images.'''

        if customize | (xlim is None )| (ylim is None):
            self.xlim = [0, image.shape[1]]
            self.ylim = [0, image.shape[0]]
        else:
            self.xlim = xlim
            self.ylim = ylim
        zoomed = image[self.ylim[0]:self.ylim[1], self.xlim[0]:self.xlim[1]]

        # create the figure, using xlim and ylim to determine the scale of the figure
        plt.ion()

        # create an empty dictionary to store the axes objects
        self.ax = {}

        # calculate aspect ratio (y/x)
        self.ysize, self.xsize = self.ylim[1] - self.ylim[0], self.xlim[1] - self.xlim[0]
        aspect = np.float(self.ysize)/self.xsize

        # set up the geometry of the plotting figure, including the desired resolution, histograms, and space for labels
        scale = 7.5
        dpi = maxresolution/np.maximum(scale, scale*aspect)
        margin = 0.07
        histheight = 0.1
        inflate = 2*margin + histheight +1
        self.figure = plt.figure(figsize=(scale*inflate, scale*aspect*inflate), dpi=dpi)
        gs = plt.matplotlib.gridspec.GridSpec(2,2,width_ratios=[1,histheight], height_ratios=[histheight, 1], top=1-margin, bottom=margin, left=margin, right=1-margin, hspace=0, wspace=0)

        # define panes for the image, as well as summed x and y histogram plots
        self.ax['image'] = plt.subplot(gs[1,0])
        self.ax['xhist'] = plt.subplot(gs[0,0], sharex=self.ax['image'] )
        self.ax['yhist'] = plt.subplot(gs[1,1], sharey=self.ax['image'] )
        self.ax['navigator'] = plt.subplot(gs[0,1])

        # clear the axes labels
        for k in self.ax.keys():
            plt.setp(self.ax[k].get_xticklabels(), visible=False)
            plt.setp(self.ax[k].get_yticklabels(), visible=False)

        # set default image display keywords
        self.imagekw = dict(cmap='gray',interpolation='nearest',extent=[0, self.xsize, 0, self.ysize], aspect='equal')

        # replace any of these, as defined through the input keywords
        for k in kwargs.keys():
            self.imagekw[k] = kwargs[k]
        #if customize:
        #    self.imagekw['aspect'] = 'auto'


        # set the default line plotting keywords
        self.linekw = dict(color='black', linewidth=1, alpha=0.5)

        # make sure the min and max values for the color scale are set
        if vmin is None:
            vmin = np.min(image)
        if vmax is None:
            vmax = np.max(image)
        self.vmin, self.vmax = vmin, vmax

        # keep track of whether we're using a log scale
        self.log = log

        # calculate summed histograms
        xhist = np.sum(zoomed, 0)
        yhist = np.sum(zoomed, 1)

        # readjust things if a log scale is set
        if self.log:
            zoomedtoplot = logify(zoomed)
            imagetoplot = logify(image)
            self.imagekw['vmin'] = np.log(np.maximum(vmin, 1))
            self.imagekw['vmax'] = np.log(vmax)
        else:
            zoomedtoplot = zoomed
            imagetoplot = image
            self.imagekw['vmin'] = vmin
            self.imagekw['vmax'] = vmax

        # keep the navigator like the image, but adjust its extent back to the regular
        self.navigatorkw = self.imagekw.copy()
        self.navigatorkw['extent'] = [0,image.shape[1],  0, image.shape[0]]



        # keep track of the data that goes into each plot
        self.current = {}

        # plot the histograms, once zoomed in
        self.current['xhist'] = self.ax['xhist'].plot(np.arange(len(xhist)), xhist, **self.linekw)[0]
        self.current['yhist'] = self.ax['yhist'].plot(yhist, np.arange(len(yhist)), **self.linekw)[0]
        self.ax['xhist'].set_xlim(0, zoomed.shape[1]-1)
        self.ax['xhist'].set_ylim(vmin*zoomed.shape[0], vmax*zoomed.shape[0])
        self.ax['yhist'].set_xlim(vmin*zoomed.shape[1], vmax*zoomed.shape[1])
        self.ax['xhist'].set_yscale('log')
        self.ax['yhist'].set_xscale('log')
        self.ax['yhist'].set_ylim(0, zoomed.shape[0]-1)

        # plot the (zoomed) image
        self.current['image'] = self.ax['image'].imshow(zoomedtoplot, **self.imagekw)
        self.current['navigator'] = self.ax['navigator'].imshow(imagetoplot, **self.navigatorkw)
        self.current['rectangle'] = self.ax['navigator'].add_patch(plt.matplotlib.patches.Rectangle((self.xlim[0], self.ylim[0]), self.xlim[1] - self.xlim[0], self.ylim[1]-self.ylim[0], edgecolor='red', facecolor='none', alpha=0.5, linewidth=5))
        self.speak('created new image and plots')



        if customize:
            self.name = self.input('Please zoom to desired limits, enter a label to identify this window, and press return:')

            xlim, ylim = np.array(self.ax['image'].get_xlim()), np.array(self.ax['image'].get_ylim())
            xlim[0] = np.maximum(xlim[0], 0)
            ylim[0] = np.maximum(ylim[0], 0)
            xlim[1] = np.minimum(xlim[1], self.xsize)
            ylim[1] = np.minimum(ylim[1], self.ysize)
            self.initialize(image, customize=False, xlim=xlim, ylim=ylim, log=log, vmin=vmin, vmax=vmax, maxresolution=maxresolution, **kwargs)
        self.speak('the display has been fully initialized -- ready for new plots!')
