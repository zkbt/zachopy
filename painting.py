import matplotlib.pyplot as plt, numpy as np

def ink_errorbar(x, y, yerr=None, xerr=None,
                colors=None, grayscale=False, alpha=1.0, zorder=0, **kwargs):
    # populate the plotting keywrods
    kw = {}
    for k in kwargs.keys():
        kw[k] = kwargs[k]

    # loop over data points
    for i in range(len(x)):

        # pick this data point's color
        color = np.array(colors[i]) + 0.0
        assert(len(color) == 4)

        # make more transparent, if alpha is <1
        try:
            color[-1] *= alpha[i]
        except TypeError:
            color[-1] *= alpha

        # convert to grayscale, if desired
        if grayscale:
            color[0:3] = np.mean(color[0:3])

        rgba = (color[0], color[1], color[2], color[3])
        # set the color of every part of the point to be plotted
        kw['color'] = rgba
        kw['ecolor'] = rgba
        kw['markeredgecolor'] = rgba
        kw['markerfacecolor'] = rgba

        try:
            assert(len(zorder) > 1)
            assert(len(zorder) == len(x))
            kw['zorder'] = zorder[i]
        except:
            kw['zorder'] = zorder

        # reshape the errors as needed (for asymmetric errors)
        if yerr is not None:
            if len(yerr.shape) == 1:
                yerrtoplot = yerr[i]
            if len(yerr.shape) == 2:
                yerrtoplot = np.array(yerr[:,i]).reshape(2,1)
        else:
            yerrtoplot = None

        if xerr is not None:
            if len(xerr.shape) == 1:
                xerrtoplot = xerr[i]
            if len(xerr.shape) == 2:
                xerrtoplot = np.array(xerr[:,i]).reshape(2,1)
        else:
            xerrtoplot = None


        #print x[i], y[i], xerrtoplot, yerrtoplot
        #print xerrtoplot.shape, yerrtoplot.shape
        # plot the point
        plt.errorbar(x[i], y[i], xerr=xerrtoplot, yerr=yerrtoplot, **kw)
