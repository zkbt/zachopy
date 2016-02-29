from Display import *
import matplotlib.animation as animation
class Movie(Display):
    '''Display 3D dataset as a movie.'''
    def __init__(self, **kwargs):
        Display.__init__(self, **kwargs)

    def fromPDFs(self, pattern, directory=None, stride=1, bitrate=1800*10, fps=30, **kwargs):

        # load the filenames to include
        self.filenames = glob.glob(pattern)[::stride]

        # make sure the output directory exists
        if directory is None:
            directory = 'movie/'

        zachopy.utils.mkdir(directory)

        for i in range(len(self.filenames)):
            input = self.filenames[i]
            png = directory + 'formovie_{0:05.0f}.png'.format(i)#input.replace('/', '_').replace('.pdf', '.png')
            command =  'convert -density 100 {input} {png}'.format(**locals())
            print command
            os.system(command)

        moviecommand = 'convert -delay 10 {directory}*.png  movie.mp4'.format(**locals())
        print moviecommand
        os.system(moviecommand)

    def fromFITSfiles(self, pattern, directory=None, stride=1, bitrate=1800*5, fps=30, **kwargs):

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
        self.writer = animation.FFMpegWriter(fps=fps, metadata=metadata, bitrate=bitrate)
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
