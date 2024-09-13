from numpy import random
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math
mu = 100
sigma = 3
x=0
while x<mu:
    x = random.normal(loc=mu, scale=sigma)

print(x)
