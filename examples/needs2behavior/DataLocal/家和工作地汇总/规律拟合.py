import pickle

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

file = open('hwdis.pkl','rb') 
data = pickle.load(file)

x, y = data
print(sum(y))

def power_function(x, a, b):
    return a * x**b

popt, pcov = curve_fit(power_function, x, y)

plt.scatter(x, y, label='Data')
plt.plot(x, power_function(x, *popt), 'r-', label='Fit: a=%5.3f, b=%5.3f' % tuple(popt))
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.savefig('hwdis_fit.png')
plt.show()


# a=0.142 b=-0.774


