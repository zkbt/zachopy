from Display import *

try:
    import pyds9
except ImportError:
    print "Uh-oh! zachopy.display is trying to 'import pyds9' and can't seem to do it. Please install it (http://hea-www.harvard.edu/RD/pyds9/)."
import regions


class ds9(Display):
    '''Use [ds9](http://hea-www.harvard.edu/saord/ds9/)
        to display one or many images in an array.'''

    def __init__(self,
                    name='general',
                    wait=10,
                    minimal=True,
                    xsize=300, ysize=300,
                    rotate=None, **kwargs):
        '''initialize the ds9 display object
            name = an identifier so you can point back to this
                    ds9 display, e.g. to refresh it later
            wait = how many seconds to wait when trying to open ds9
            minimial = hide all the bells and whistles
            rotate = should images be rotated by default
            '''

        # pass kw on to Display
        Display.__init__(self, **kwargs)

        # make sure the name is valid
        self.name = name.replace(' ','_')

        # attempt to open, but don't freak out
        try:
            self.speak('trying to open a new ds9 window called "{0}"'.format(
                self.name))
            self.speak('  (will wait up to {0:.0f} seconds)'.format(wait))
            self.window = pyds9.DS9(self.name,start=True,wait=wait,verify=True)
        except IOError:
            self.speak('  :( failed to open ds9 window "{0}"'.format(self.name))

        if minimal:
            self.sparse()

        self.resize(xsize, ysize)

        self.rotate=rotate

    def sparse(self, toremove=[ 'info',
                                'panner',
                                'magnifier',
                                'buttons']):
        '''hide most of the GUI, to save space.

            toremove = list of features to remove
        '''

        for what in toremove:
            self.window.set('view {0} no'.format(what))

    def unsparse(self, toadd= [ 'info',
                                'panner',
                                'magnifier',
                                'buttons']):
        '''show the usual GUI features.

            toremove = list of features to add
        '''

        for what in toremove:
            self.window.set('view {0} yes'.format(what))

    def resize(self, xsize, ysize):
        self.window.set('width {:.0f}'.format(xsize))
        self.window.set('height {:.0f}'.format(ysize))

    def match(self, what=['frame image', 'scale', 'colorbar']):
        '''Make all the frames match the current one.'''
        for w in what:
            self.window.set('match {0}'.format(w))

    def rgb(self, r, g, b, clobber=True, regions=None, **options):
        '''Display three images as RGB in ds9.'''
        if clobber:
          self.clear()
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
        '''send valid options to the ds9 frame.'''

        # send some regions
        try:
            self.showRegions(options['regions'])
        except KeyError:
            pass

        # invert the cmap
        try:
            if options['invert']:
                self.window.set('cmap invert')
        except KeyError:
            pass

    def showRegions(self, regions):
        '''write a region file and load it to display'''
        filename = 'temporary.ds9.regions.reg'
        regions.write(filename)
        self.window.set("regions load {0}".format(filename))

    def many(self,  inputimages,
                    depth=-1,
                    limit=25,
                    clobber=True,
                    single=True,
                    **options):
        '''display a bunch of images in ds9, each in its own frame.

            inputimages = 3D cube of images to display
            depth = the axis corresponding to independent images
            limit = maximum number of images to display
            clobber = should we erase what's in this display?
            single = show "single" frame (False --> "tile")
            **options = additional options to apply

        '''

        # make sure the images are array (they could have been a list)
        images = np.array(inputimages)

        # clear out other frames
        if clobber:
          self.clear()

        # set the frame display option
        if single:
            self.single()
        else:
            self.tile()

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
                self.replace(images.take(i,axis=depth).astype(np.float), i)
                self.applyOptionsToFrame(**options)
            return

        # if all else fails, freak out!
        raise ValueError("Uh-oh! The shape {0} can't work as an image cube.")

    def clear(self):
        self.window.set("frame delete all")

    def new(self, frame=None):
        '''create a new frame'''
        if frame is None:
            self.window.set("frame new")
        else:
            self.window.set("frame {:.0f}".format(frame))

        if self.rotate is not None:
            self.window.set("rotate to {0}".format(self.rotate))

    def one(self, image, clobber=False, frame=None, **options):
        '''Display one image in ds9.

            image = 2D image to display
            clobber = should we erase what's in this display?
            **options = additional options to apply
        '''

        # clear, if desired
        if clobber:
            self.clear()

        # create a new frame for this image
        self.new(frame=frame)

        # fill it with the data
        self.window.set_np2arr(image.astype(np.float).squeeze())

        # apply the options
        self.applyOptionsToFrame(**options)

    def scale(self, scale=None, limits=None, mode=None ):
        '''Update the scale of the image.

            scale = [linear|log|pow|sqrt|squared|asinh|sinh|histequ]
            limits = [<minvalue> <maxvalue>]
            mode = [minmax|<value>|zscale|zmax]
        '''
        if scale is not None:
            self.window.set('scale {0}'.format(scale))
        if mode is not None:
            self.window.set('scale mode {0}'.format(mode))
        if limits is not None:
            self.window.set('scale limits {0} {1}'.format(limits[0], limits[1]))

    def tile(self, how=None):
        '''tile the current frames'''
        if how is not None:
            self.window.set('tile {0}'.format(how))
        self.window.set('tile')

    def single(self):
        '''show only a single frame at a time'''
        self.window.set('single')

    def zoom(self, how='to fit'):
        '''zoom on the current image'''
        self.window.set('zoom {0}'.format(how))
    def replace(self, image, i):
        '''Replace the image in the a specific ds9 frame with a new one.

            image = the new image to show
            i = which frame to replace with it
                (0-indexed, so i=0 goes to ds9 frame "1")
        '''

        # point at the frame
        self.window.set("frame {0}".format(i+1))

        # set the image in that frame
        self.window.set_np2arr(image.astype(np.float).squeeze())

    def update(self, image):
        '''Update the image in this frame with an updated one.

            image = the new image to show
        '''
        self.window.set_np2arr(image.astype(np.float))

    def saveimage(self, filename):
        '''save out the current ds9 display as an image.

            filename = filename, decides format based on suffix

        '''

        # bring the ds9 window to the front
        self.window.set('raise')

        # save the image
        self.window.set('saveimage {0}'.format(filename))
