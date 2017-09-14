
# coding: utf-8

# In[1]:


import zachopy.color, zachopy.units as u
import matplotlib.pyplot as plt
import numpy as np, scipy.integrate
import astropy.io.ascii
get_ipython().magic(u'matplotlib inline')
plt.style.use('dark_background')
def gauss(x, x0, sigma):
    return 1.0/np.sqrt(2*np.pi)/sigma*np.exp(-0.5*((x-x0)/sigma)**2)

class Spectrum:
    def __init__(self, name):
        self.name = name
        self.wavelength = np.logspace(1, 7, 1000)

    def normalize(self, power=100):
        total = scipy.integrate.trapz(self.flux, self.wavelength)
        self.power = power
        self.flux = self.flux/total*power

    def plot(self):
        plt.plot(self.wavelength, self.flux, color='white')
        plt.title(self.name)
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Flux (W/m$^2$/nm)')

        plt.ylim(1e-20*max(self.flux), 10*max(self.flux))

        # plot the color comparison
        y = plt.gca().get_ylim()[1]
        for w in np.linspace(300, 800, 100):
            plt.axvline(w, color=zachopy.color.nm2rgb(w))
            #plt.scatter(w, y, color=zachopy.color.nm2rgb(w), marker='|', edgecolor='none', s=400)



        plt.xscale('log')
        plt.yscale('log')
        plt.savefig(self.name.strip(), dpi=300)

class Solar(Spectrum):
    def __init__(self):
        Spectrum.__init__(self, 'The Spectrum of the Sun')
        d = astropy.io.ascii.read('solarspectrum.txt')
        self.wavelength = d['wavelength (nm)'].data
        self.flux = d['irradiance (W/m^2/nm)'].data

class Sodium(Spectrum):
    def __init__(self, power=100):
        # technically this should be more of Lorentzian than this
        Spectrum.__init__(self, 'The Spectrum of a Sodium Lamp')
        self.flux = np.zeros_like(self.wavelength)
        lines = [588.9950, 589.5924]
        for l in lines:
            self.flux += gauss(self.wavelength, x0=l, sigma=2.0)
        self.normalize(power)

class Thermal(Spectrum):
    def __init__(self, temperature=3000, power=100):
        Spectrum.__init__(self, 'The Spectrum of a {}K Thermal Source'.format(temperature))
        self.temperature = temperature

        h = 6.626068e-34
        k = 1.3806503e-23
        c = 299792458.0

        wavelength = self.wavelength/1e9
        self.flux = 2 * h * c**2 / (wavelength**5 * (np.exp(h * c / (wavelength * k * temperature)) - 1))
        self.normalize(power)



# In[2]:


def contrast(albedo = 0.99):
    distance = 10*u.pc/u.m
    semimajor = 1*u.au/u.m
    lsun = u.Lsun/u.watt
    sigma = 5.67e-8
    Teff = 5770



    sun = Thermal(5770)
    sun.normalize(lsun/4/np.pi/distance**2)
    sun.plot()

    flux = lsun/4/np.pi/semimajor**2
    Teq = (flux*(1-albedo)/4/sigma)**0.25
    #reflectedpower =
    emitted = Thermal(Teq)
    emitted.normalize(sun.power/4/np.pi/u.au**2*(1-albedo)*np.pi*u.Rearth**2)

    reflected = Thermal(Teff)
    reflected.normalize(sun.power/4/np.pi/u.au**2*albedo*np.pi*u.Rearth**2)

    for s in [reflected, emitted]:
        if np.isfinite(s.flux).all() == False:
            s.flux = np.zeros_like(s.flux)


    wavelength = sun.wavelength
    sunlight = sun.flux
    plt.plot(wavelength, sun.flux, color='darkgray', linewidth=5, zorder=99)
    plt.plot(wavelength, reflected.flux, linewidth=5, linestyle='--', color='cornflowerblue', zorder=100, alpha=0.5)
    plt.plot(wavelength, emitted.flux, linewidth=5, linestyle='--', color='lightsalmon', zorder=100, alpha=0.5)
    plt.plot(wavelength, emitted.flux + reflected.flux, linewidth=5, color='white', zorder=99,
            label ='albedo = {:.2f}'.format(albedo) )

    plt.ylim(1e-30, 1e-10)
    plt.xlim(1e1, 1e6)
    plt.title('An Earth-size Planet 1AU from a Sun-like Star (at 10pc)')
    plt.legend(frameon=False, fontsize=16, markerscale=0, handlelength=0 )


# In[3]:

if __name__ == '__main__':
    import matplotlib.animation as ani

    wri = ani.FFMpegWriter(fps=15)
    fig = plt.figure()

    with wri.saving(fig, 'planetcontrast.mp4', 200):
        for albedo in np.arange(0,1.001,.01):
            plt.cla()
            contrast(albedo)
            wri.grab_frame()
            print albedo


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:
