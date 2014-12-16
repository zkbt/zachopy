'''Tools for displaying 2D/3D datasets.'''

from matplotlib import pyplot as plt, numpy as np
try:
    import ds9 as pyds9
except:
    print "Uh-oh! zachopy.display is trying to 'import ds9' and can't seem to do it. Please install it (http://hea-www.harvard.edu/RD/pyds9/)."

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

    def rgb(self, r, g, b, clobber=True):
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

    def many(self, inputimages, clobber=True):
        '''Display a bunch of images in ds9, each in its own frame.'''
        images = np.array(inputimages)
        if clobber:
          self.window.set("frame delete all")

        if len(images.shape) <= 2:
          self.windowone(images, clobber=clobber)
          return

        for i in range(images.shape[0]):
          self.window.set("frame {0}".format(i))
          self.window.set_np2arr(images[i].astype(np.float))

    def one(self, image, clobber=False):
        '''Display one image in ds9, with option to empty all grames first.'''
        if clobber:
            self.window.set("frame delete all")
        self.window.set("frame new")
        self.window.set_np2arr(image.astype(np.float))

    def replace(self, image, i):
        '''Replace the image in the a specific ds9 frame with a new one.'''
        self.window.set("frame {0}".format(i+1))
        self.window.set_np2arr(image.astype(np.float))

    def update(self, image, clobber=False):
        '''Update the image in this frame with an updated one.'''
        self.window.set_np2arr(image.astype(np.float))
