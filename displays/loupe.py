from .Display import *
from .iplot import iplot
import matplotlib.colors as colors
import zachopy.oned
import matplotlib.pyplot as plt

class loupe(Display):
    '''
    loupe is an interactive matplotlib imshow,
    for looking at images and clicking points,
    in a matplotlib-like plot.

    It reproduces *a few* of the features
    available from using IRAF display,
    imexam, and ds9 to look at images interactively.
    '''


    def __init__(self, **kwargs):
        '''Initialize the loupe object.'''

        Display.__init__(self)

        # populate a dictionary of available actions
        # each option has a key to press,
        #   a description of what it will do
        #   a function to be called when that key is pressed
        #   and whether the function needs to know the current mouse position
        self.options = {}

        # qui
        self.options['q'] = dict(description='[q]uit',
                            function=self.quit,
                            requiresposition=False)

        # a crosshair will plot vertical and horizontal plots at that location
        self.options['c'] = dict(description='move the [c]rosshair, and plot slicey along it',
                            function=self.moveCrosshair,
                            requiresposition=True)

        # once the crosshair is set, you can movie it up and down
        self.options['up'] = dict(description='nudge the crosshair [up]',
                            function=self.moveCrosshair,
                            requiresposition=False)
        self.options['down'] = dict(description='nudge the crosshair [down]',
                            function=self.moveCrosshair,
                            requiresposition=False)
        self.options['left'] = dict(description='nudge the crosshair [left]',
                            function=self.moveCrosshair,
                            requiresposition=False)
        self.options['right'] = dict(description='nudge the crosshair [right]',
                            function=self.moveCrosshair,
                            requiresposition=False)

    def setImage(self, image):
        '''
        Change the image that's being shown.
        '''

        # set the image
        self.image = image

        # set its x and y limits, extent, and axes
        xsize = self.imagetoplot.shape[1]
        ysize = self.imagetoplot.shape[0]
        self.extent = [ 0, xsize,
                        0, ysize]
        self.xaxis = np.arange(xsize)
        self.yaxis = np.arange(ysize)


    @property
    def slicey(self):
        '''return y, x of a slice along the spatial direction'''

        # figure out the column of the image associated with the crosshair's x
        i = np.int(np.interp(self.crosshair['x'], self.xaxis, np.arange(len(self.xaxis))))
        return self.image[i,:], self.yaxis

    @property
    def slicex(self):
        '''return x, y of a slice along the wavelength direction'''

        # figure out the column of the image associated with the crosshair's y
        i = np.int(np.interp(self.crosshair['y'], self.yaxis, np.arange(len(self.yaxis))))
        return self.xaxis, self.image[:,i]

    @property
    def imagetoplot(self):
        '''for plotting, the science image'''

        # show the transpose of the image in imshow
        return np.transpose(self.image)

    def one(self, image, **kwargs):
        # for compatibility with ds9
        self.setup(image, **kwargs)

    def updateImage(self, image, **kwargs):
        '''
        Once the loupe has been set up,
        modify the image being shown
        (ideally without changing anything else.)
        '''

        #
        try:
            # have we already created a loupe here?
            self.plotted['2d']
        except AttributeError:
            # if not, set it up!
            self.setup(image, **kwargs)

        # update the data being imshowed
        self.plotted['2d'].set_data(self.imagetoplot)

        # update the plots for the slices along each axis
        x, y = self.crosshair['x'], self.crosshair['y']
        self.moveCrosshair(x=x, y=y)

        # force a redraw of the plot
        plt.draw()

    def setup(self, image,
                    title='', # title to go over the top of the plot
                    figsize=(8,4), # kwargs for figure,
                    dpi=100,
                    hspace=0, wspace=0, # kwargs for gridspec
                    left=0.05, right=0.95,
                    bottom=0.05, top=0.95,
                    width_ratios=[1.0, 0.1],
                    height_ratios=[0.1, 1.0],
                    initialcrosshairs=[0.0, 0.0], # where the crosshairs should start
                    aspect='equal', # kwargs for imshow
                    **kwargs):
        '''
        Initialize the loupe
        (this has a pretty big overhead,
        so use "setImage" if you can to update
        the data being displayed)
        '''

        # set the image
        self.setImage(image)
        self.speak('setting up loupe')


        # keep track of where the crosshair is pointing
        self.crosshair = dict(x=initialcrosshairs[0], y=initialcrosshairs[1])

        # set up the figure
        plt.ion()
        self.figure = plt.figure(figsize=figsize, dpi=dpi)
        # create an interactive plot
        self.iplot = iplot(2,2, hspace=hspace, wspace=wspace,
                              left=left, right=right,
                              bottom=bottom, top=top,
                              width_ratios=width_ratios,
                              height_ratios=height_ratios)

        # a dictionary to store the axes objects
        self.ax = {}

        # for displaying the 2D image
        labelkw = dict(fontsize = 5)
        self.ax['2d'] = self.iplot.subplot(1,0)
        plt.setp(self.ax['2d'].get_xticklabels(), **labelkw)
        plt.setp(self.ax['2d'].get_yticklabels(), **labelkw)

        # for displaying cuts along the dispersion direction
        self.ax['slicex'] = self.iplot.subplot(0,0,sharex=self.ax['2d'])
        self.ax['slicex'].set_title(title, fontsize=8)
        plt.setp(self.ax['slicex'].get_xticklabels(), visible=False)
        plt.setp(self.ax['slicex'].get_yticklabels(), **labelkw)

        # for display cuts along the cross-dispersion direction
        self.ax['slicey'] = self.iplot.subplot(1,1,sharey=self.ax['2d'])
        self.ax['slicey'].xaxis.tick_top()
        plt.setp(self.ax['slicey'].get_xticklabels(), rotation=270, **labelkw)
        plt.setp(self.ax['slicey'].get_yticklabels(), visible=False)

        # set the limits of the plot
        ok = np.isfinite(self.imagetoplot)
        self.vmin, self.vmax = np.percentile(self.imagetoplot[ok], [0,100])

        self.plotted = {}
        # plot the image
        self.plotted['2d'] = self.ax['2d'].imshow(self.imagetoplot,
                                                  cmap='gray',
                                                  extent=self.extent,
                                                  interpolation='nearest',
                                                  aspect=aspect,
                                                  zorder=0,
                                                  origin='lower',
                                                  norm=colors.SymLogNorm(
                                                                        linthresh=zachopy.oned.mad(self.imagetoplot),
                                                                        linscale=0.1,
                                                                        vmin=self.vmin,
                                                                        vmax=self.vmax))

        # set the x and y limits
        self.ax['2d'].set_xlim(self.extent[0:2])
        self.ax['2d'].set_ylim(self.extent[2:4])

        # add crosshair
        crosskw = dict(alpha=0.5, color='darkorange', linewidth=1)
        self.plotted['crossy'] = self.ax['2d'].axvline(self.crosshair['x'],
                                                        **crosskw)
        self.plotted['crossyextend'] = self.ax['slicex'].axvline(
                                                        self.crosshair['x'],
                                                        linestyle='--',
                                                        **crosskw)
        self.plotted['crossx'] = self.ax['2d'].axhline(self.crosshair['y'],
                                                        **crosskw)
        self.plotted['crossxextend'] = self.ax['slicey'].axhline(
                                                        self.crosshair['y'],
                                                        linestyle='--',
                                                        **crosskw)
        # plot slicey
        slicekw = dict(color='darkorange', linewidth=1, alpha=1)
        self.plotted['slicey'] = self.ax['slicey'].plot(*self.slicey,
                                                        **slicekw)[0]
        self.plotted['slicex'] = self.ax['slicex'].plot(*self.slicex,
                                                        **slicekw)[0]

        plt.draw()

    def run(self,
            message='', # something to annouce each loop
            ):

        # update the plot
        plt.draw()

        # keep track of whether we're finished
        self.notconverged = True
        while self.notconverged:

            # say the message at the start of each loop
            self.speak(message)

            # print the self.options
            self.speak('your self.options include:')
            for v in self.options.values():
                self.speak('   ' + v['description'])

            # get the keyboard input
            pressed = self.iplot.getKeyboard()
            self.speak('"{}" was pressed'.format(pressed.key))
            # process the keyboard input
            try:
                # figure out which option we're on
                thing = self.options[pressed.key.lower()]
                # check that it's a valid position, if need be
                if thing['requiresposition']:
                    assert(pressed.inaxes is not None)
                # execute the function associated with this option
                thing['function'](pressed)
            except KeyError:
                self.speak("nothing yet defined for [{}]".format(pressed.key))
            except AssertionError:
                self.speak("that didn't seem to be at a valid position!")

            # update the plot
            plt.draw()

    def quit(self, *args):
        '''
        If a [q] is pressed, quit the plot.
        '''
        self.notconverged = False
        plt.close(self.figure)

    """
    ### FIX ME -- I think this belongs with mosasaurus, but got copied here. ###
    def setScale(self, pressed=None, default=False):
        '''prompt the user to select range of aperture sizes for extraction'''
        if default:
            self.narrowest = self.obs.narrowest
            self.widest = self.obs.widest
            self.numberofapertures = self.obs.numberofapertures
        else:
            self.speak('Please redefine the aperture sizes.')
            self.speak(' (The old aperture sizes were {}.)'.format(self.extractionwidths))
            self.speak(' ["d" for any of these for defaults]')

            try:
                self.narrowest = np.float(self.input("What is the narrowest aperture?"))
            except ValueError:
                self.narrowest = self.obs.narrowest

            try:
                self.widest = np.float(self.input("What is the widest aperture?"))
            except ValueError:
                self.widest = self.obs.widest

            try:
                self.numberofapertures = np.int(self.input('How many apertures do you want?'))
            except ValueError:
                self.numberofapertures = self.obs.numberofapertures

        self.extractionwidths = np.linspace(self.narrowest, self.widest, self.numberofapertures)
        self.speak(' The current aperture sizes are {}.'.format(self.extractionwidths))

        # update the plotting, to reflect the new extraction apertures
        try:
            self.updateMasks()
        except AttributeError:
            pass
    """

    def moveCrosshair(self, pressed=None, x=None, y=None):
        '''use new values of w and s to move the crosshair and replot'''

        # pull the values from the mouse click
        if pressed.key == 'up':
            self.crosshair['y'] += 1
        elif pressed.key == 'down':
            self.crosshair['y'] -= 1
        elif pressed.key == 'left':
            self.crosshair['x'] -= 1
        elif pressed.key == 'right':
            self.crosshair['x'] += 1
        elif pressed is not None:
            x = pressed.xdata
            y = pressed.ydata

            # update the stored value
            if x is not None:
                self.crosshair['x'] = x
            if y is not None:
                self.crosshair['y'] = y

        # update the position on the 2D plot
        self.plotted['crossy'].set_xdata(self.crosshair['x'])
        self.plotted['crossyextend'].set_xdata(self.crosshair['x'])
        self.plotted['crossx'].set_ydata(self.crosshair['y'])
        self.plotted['crossxextend'].set_ydata(self.crosshair['y'])

        # update the slicey in the 1D plots
        self.plotted['slicey'].set_data(*self.slicey)
        self.ax['slicey'].set_xlim(0, self.slicey[0].max())
        self.plotted['slicex'].set_data(*self.slicex)
        self.ax['slicex'].set_ylim(0, self.slicex[1].max())

def test():
    fake = createTestImage()
    l = loupe()
    l.setup(fake)
    l.run()
    return fake, l
