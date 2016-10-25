from Display import *
import zachopy.iplot
import matplotlib.colors as colors
import zachopy.oned
import matplotlib.pyplot as plt

class loupe(Display):
    def __init__(self, **kwargs):
        Display.__init__(self)

        self.options = {}

        self.options['q'] = dict(description='[q]uit without writing',
                            function=self.quit,
                            requiresposition=False)

        self.options['c'] = dict(description='move the [c]rosshair, and plot slicey along it',
                            function=self.moveCrosshair,
                            requiresposition=True)

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
        self.image = image
        xsize = self.imagetoplot.shape[1]
        ysize = self.imagetoplot.shape[0]
        self.extent = [ 0, xsize,
                        0, ysize]
        self.xaxis = np.arange(xsize)
        self.yaxis = np.arange(ysize)

    @property
    def slicey(self):
        '''return y, x of a slice along the spatial direction'''
        i = np.int(np.interp(self.crosshair['x'], self.xaxis, np.arange(len(self.xaxis))))
        return self.image[i,:], self.yaxis

    @property
    def slicex(self):
        '''return x, y of a slice along the wavelength direction'''
        i = np.int(np.interp(self.crosshair['y'], self.yaxis, np.arange(len(self.yaxis))))
        return self.xaxis, self.image[:,i]

    @property
    def imagetoplot(self):
        '''for plotting, the science image'''
        return np.transpose(self.image)

    def one(self, image, **kwargs):
        # for compatibility with ds9
        self.setup(image, **kwargs)

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

        self.setImage(image)
        self.speak('setting up loupe')


        # keep track of where the crosshair is pointing
        self.crosshair = dict(x=initialcrosshairs[0], y=initialcrosshairs[1])

        # set up the figure
        plt.ion()
        self.figure = plt.figure(figsize=figsize, dpi=dpi)
        # create an interactive plot
        self.iplot = zachopy.iplot.iplot(2,2, hspace=hspace, wspace=wspace,
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
                                                  norm=colors.SymLogNorm(linthresh=zachopy.oned.mad(self.imagetoplot), linscale=0.1,
                                                    vmin=self.vmin, vmax=self.vmax))

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


    def run(self,
                    message='', # something to annouce each loop
                    ):

        # keep track of whether we're finished
        self.notconverged = True
        while self.notconverged:


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


            plt.draw()

    def quit(self, *args):
        self.notconverged = False
        plt.close(self.figure)


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

    def moveCrosshair(self, pressed=None, w=None, s=None):
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
            w = pressed.xdata
            s = pressed.ydata

            # update the stored value
            if w is not None:
                self.crosshair['x'] = w
            if s is not None:
                self.crosshair['y'] = s

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
