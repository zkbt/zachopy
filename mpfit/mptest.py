import mpfit
import numpy as np
import matplotlib.pyplot as plt


def funct(p, x):
	return p[0] + p[1]*x + p[2]*x**2 + p[3]*np.sqrt(x)

def deviates(p, x=None, y=None, err=None,fjac=None):
	status = 0
	return [status,(y - funct(p,x))/err]
plt.cla()
x = np.arange(100)
p0 = np.array([5.7, 2.2, 500., 1.5])
p = p0
err = np.ones_like(x)*500000
y = funct(p,x) + np.random.randn(len(x))*err
plt.scatter(x,y, color='black', alpha=0.3)

fa = {'x':x, 'y':y, 'err':err}
m = mpfit.mpfit(deviates, p0, functkw=fa)
print 'status = ', m.status
if (m.status <= 0): print 'error message = ', m.errmsg
print 'parameters = ', m.params

plt.plot(x, funct(m.params,x), alpha=0.5, linewidth=3)
plt.draw()