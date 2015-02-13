'''Tools for displaying 2D/3D datasets.'''

from matplotlib import pyplot as plt, numpy as np
import matplotlib.animation as animation
import glob
import astropy.io.fits
import zachopy.utils
from Talker import Talker

try:
    import ds9 as pyds9
except:
    print "Uh-oh! zachopy.display is trying to 'import ds9' and can't seem to do it. Please install it (http://hea-www.harvard.edu/RD/pyds9/)."

import regions

class Display(Talker):
    '''Display 2D or 3D datasets, using a variety of methods.'''
    def __init__(self, **kwargs):
        # decide whether or not this creature is chatty
        Talker.__init__(self, **kwargs)

class Movie(Display):
    '''Display 3D dataset as a movie.'''
    def __init__(self, **kwargs):
        Display.__init__(self, **kwargs)


    def fromFITSfiles(self, pattern, directory=None, stride=1, **kwargs):

        # load the filenames to include
        self.filenames = glob.glob(pattern)[::stride]

        # make sure the output directory exists
        if directory is not None:
            zachopy.utils.mkdir(directory)

        #initialize the plot
        i = 0
        self.speak('opening {0}'.format(self.filenames[i]))
        hdu = astropy.io.fits.open(self.filenames[i])
        self.image = np.transpose(hdu[0].data)
        self.frame = imshow(self.image, **kwargs)

        # initialize the animator
        metadata = dict(title=self.frame.name, artist='Z.K.B.-T.')
        self.writer = animation.FFMpegWriter(fps=30, metadata=metadata, bitrate=1800*5)
        print directory + '/' + self.frame.label + '.mp4'
        with self.writer.saving(self.frame.figure, directory + '/' + self.frame.label + '.mp4', self.frame.figure.get_dpi()):
            # loop over exposures
            for i in range(len(self.filenames)):
                self.speak('opening {0}'.format(self.filenames[i]))
                hdu = astropy.io.fits.open(self.filenames[i])
                self.image = np.transpose(hdu[0].data)

                if directory is not None:
                    output = directory + '/{0:04.0f}.png'.format(i)
                else:
                    output = None
                self.frame.update(self.image, ylabel=self.filenames[i].split('/')[-1], xlabel='/'.join(self.filenames[i].split('/')[0:-1])+'/')
                self.writer.grab_frame()
def logify(im):
    logged = np.log(im)
    logged[np.isfinite(logged) == False] = np.min(logged[np.isfinite(logged)])
    return logged

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

class ds9(Display):
    '''Use [ds9](http://hea-www.harvard.edu/saord/ds9/) to display one or many images in an array.'''
    def __init__(self,name='general', **kwargs):
        Display.__init__(self, **kwargs)
        self.name = name.replace(' ','_')
        try:
            wait = 10
            self.speak( 'trying to open a new ds9 window called "{0}" (will wait up to {1:.0f} seconds)'.format(self.name, wait))
            self.window = pyds9.ds9(self.name,start=True,wait=wait,verify=True)
        except:
            self.speak('failed!'.format(self.name))

    def match(self, what=['frame image', 'scale', 'colorbar']):
        '''Make all the frames match the current one.'''
        for w in what:
            self.window.set('match {0}'.format(w))

    def rgb(self, r, g, b, clobber=True, regions=None):
        '''Display three images as RGB in ds9.'''
        if clobber:
          self.window.set("frame delete all")
        self.window.set("rgb")
        self.window.set("rgb red")
        self.window.set_np2arr(r.astype(np.float))
        self.window.set("rgb green")
        self.window.set_np2arr(g.astype(np.float))
        self.window.set("rgb blue")
        self.window.set_np2arr(b.astype(np.float))
        self.window.set("rgb red")
        self.applyOptionsToFrame(**options)

    def applyOptionsToFrame(self, **options):
        try:
            self.showRegions(options['regions'])
        except:
            pass

        try:
            if options['invert']:
                self.window.set('cmap invert')
        except:
            pass


    def showRegions(self, regions):
        filename = 'temporary.ds9.regions.reg'
        regions.write(filename)
        self.window.set("regions load {0}".format(filename))

    def many(self, inputimages, clobber=True, depth=-1, limit=25, single=True, **options):
        '''Display a bunch of images in ds9, each in its own frame.'''
        images = np.array(inputimages)
        if clobber:
          self.window.set("frame delete all")

        if single:
            self.window.set('single')
        else:
            self.window.set('tile')

        # is the "cube" really just a 1D or 2D image?
        if len(images.shape) <= 2:
          self.one(images, clobber=clobber)
          return

        # loop through the "depth" axis, which is by default the final one
        if len(images.shape) == 3:

            # only display up to a certain number of images
            if images.shape[-1] > limit:
                self.speak("going to display only {0:.0f} images, for impatience's sake".format(limit))

            # display all the images
            for i in range(np.minimum(images.shape[depth], limit)):
                self.window.set("frame {0}".format(i))
                self.window.set_np2arr(images.take(i,axis=depth).astype(np.float))
                self.applyOptionsToFrame(**options)
            return

        self.speak('Uh-oh! Image array seems to have a dimension other than 1, 2, or 3!')

    def one(self, image, clobber=False, regions=None, **options):
        '''Display one image in ds9, with option to empty all grames first.'''
        if clobber:
            self.window.set("frame delete all")
        self.window.set("frame new")
        self.window.set_np2arr(image.astype(np.float).squeeze())
        self.applyOptionsToFrame(**options)

    def scale(self, scale=None, limits=None, mode=None ):
        '''Update the scale of the image.

            scale [linear|log|pow|sqrt|squared|asinh|sinh|histequ]
            [limits <minvalue> <maxvalue>]
            [mode minmax|<value>|zscale|zmax]
        '''
        if scale is not None:
            self.window.set('scale {0}'.format(scale))
        if mode is not None:
            self.window.set('scale mode {0}'.format(mode))
        if limits is not None:
            self.window.set('scale limits {0} {1}'.format(limits[0], limits[1]))


    def tile(self, how=None):
        if how is not None:
            self.window.set('tile {0}'.format(how))
        self.window.set('tile')

    def single(self):
        self.window.set('single')

    def replace(self, image, i):
        '''Replace the image in the a specific ds9 frame with a new one.'''
        self.window.set("frame {0}".format(i+1))
        self.window.set_np2arr(image.astype(np.float).squeeze())

    def update(self, image, clobber=False):
        '''Update the image in this frame with an updated one.'''
        self.window.set_np2arr(image.astype(np.float))

    def saveimage(self, filename):
        self.window.set('raise')
        self.window.set('saveimage {0}'.format(filename))
