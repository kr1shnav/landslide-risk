import numpy as np
def terrain_derivatives(dem,resolution=(1,1)):
    gy,gx=np.gradient(dem,*resolution); return {'slope':np.degrees(np.arctan(np.hypot(gx,gy))),'aspect':(np.degrees(np.arctan2(-gx,gy))+360)%360,'curvature':np.gradient(gx,axis=1)+np.gradient(gy,axis=0)}
def twi(slope,flow_accumulation): return np.log((flow_accumulation+1)/np.maximum(np.tan(np.radians(slope)),1e-6))
