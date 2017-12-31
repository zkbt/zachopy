import glob, numpy as np, matplotlib.pyplot as plt, astropy.io.fits
from matplotlib import animation
def movie(pattern, output='movie', stride=1, bitrate=1800*5, fps=30, vmin=None, vmax=None, **kwargs):

    # load the filenames to include
    filenames = glob.glob(pattern)[::stride]

    #initialize the plot
    i = 0
    print('opening {0}'.format(filenames[i]))

    # open the fits files
    hdu = astropy.io.fits.open(filenames[i])
    image = np.log10(hdu[0].data)

    scale = np.max(image.shape).astype(np.float)
    figure = plt.figure(figsize=np.array(image.shape)/scale, dpi=scale*3)
    ax = plt.subplot()#figure.add_axes([0, 1, 0, 1])
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    if vmin is not None:
        vmin = np.percentile(image, 2)
    if vmax is not None:
        vmax = np.percentile(image, 98)
    imshow = ax.imshow(image, interpolation='nearest', cmap='gray', vmin=vmin, vmax=vmax, **kwargs)
    plt.show()
    # initialize the animator
    metadata = dict()
    writer = animation.FFMpegWriter(fps=fps, metadata=metadata, bitrate=bitrate)

    output_filename = output + '.mp4'
    with writer.saving(figure, output_filename, figure.get_dpi()):

        # loop over exposures
        for i in range(len(filenames)):
            print('opening {0}'.format(filenames[i]))
            hdu = astropy.io.fits.open(filenames[i])
            image = np.log10(hdu[0].data)

            imshow.set_data(image)
            figure.savefig('test.png')
            writer.grab_frame()
            print(image)
