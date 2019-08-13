import numpy as np
import matplotlib.pyplot as plt
x=np.array([[0,1,2],[0,1,2]])
y=np.array([[0,0,0],[1,1,1]])
plt.plot(x,y,color='red',marker='.',markersize=10,linestyle='')
plt.grid(True)
plt.show()

X,Y,Z=np.meshgrid([1,2,3],[4,5],[6,7,8])
plt.p(X,Y,Z,color='red',marker='.',markersize=10,linestyle='')
plt.grid(True)
plt.show()




