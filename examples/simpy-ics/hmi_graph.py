import matplotlib.pyplot as plt
import numpy as np

plt.axis([0, 10, 0, 1])
x_pos = []
y_pos = []
for i in range(10):
    y = np.random.random()
    x_pos.append(i)
    y_pos.append(y)
    plt.plot(x_pos,y_pos)
    plt.pause(0.05)

plt.show()
