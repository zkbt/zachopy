'''Tools for displaying 2D/3D datasets.'''

from matplotlib import pyplot as plt, numpy as np
try:
    import ds9 as pyds9
except:
    print "Uh-oh! zachopy.display is trying to 'import ds9' and can't seem to do it. Please install it (http://hea-www.harvard.edu/RD/pyds9/)."
import regions

class Display(object):
    '''Display 2D or 3D datasets, using a variety of methods.'''
    def __init__(self):
        pass

class ds9(Display):
    '''Use [ds9](http://hea-www.harvard.edu/saord/ds9/) to display one or many images in an array.'''
    def __init__(self,name='general'):
        self.name = name.replace(' ','_')
        self.prefix = '[ds9] '
        try:
            wait = 10
            print self.prefix + 'trying to open a new ds9 window called "{0}"\n     (will wait up to {1:.0f} seconds)'.format(self.name, wait)
            self.window = pyds9.ds9(self.name,start=True,wait=wait,verify=True)
        except:
            print self.prefix + 'failed!'.format(self.name)

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
                print self.prefix + "going to display only {0:.0f} images, for impatience's sake".format(limit)

            # display all the images
            for i in range(np.minimum(images.shape[depth], limit)):
                self.window.set("frame {0}".format(i))
                self.window.set_np2arr(images.take(i,axis=depth).astype(np.float))
                self.applyOptionsToFrame(**options)
            return

        print self.prefix + 'Uh-oh! Image array seems to have a dimension other than 1, 2, or 3!'

    def one(self, image, clobber=False, regions=None):
        '''Display one image in ds9, with option to empty all grames first.'''
        if clobber:
            self.window.set("frame delete all")
        self.window.set("frame new")
        self.window.set_np2arr(image.astype(np.float))
        self.applyOptionsToFrame(**options)


    def replace(self, image, i):
        '''Replace the image in the a specific ds9 frame with a new one.'''
        self.window.set("frame {0}".format(i+1))
        self.window.set_np2arr(image.astype(np.float))

    def update(self, image, clobber=False):
        '''Update the image in this frame with an updated one.'''
        self.window.set_np2arr(image.astype(np.float))

    def saveimage(self, filename):
        self.window.set('raise')
        self.window.set('saveimage {0}'.format(filename))
