from pyproj_numpy import Proj, transform
import numpy as N

# convert awips221 grid to awips218 coordinate system
# (grids defined at http://www.nco.ncep.noaa.gov/pmb/docs/on388/tableb.html)
nx = 614; ny = 428; dx = 12190.58; dy = dx
awips221 = Proj(proj='lcc',R=6371200,lat_1=50,lat_2=50,lon_0=-107)
print 'proj4 library version = ',awips221.proj_version
llcrnrx, llcrnry = awips221(-145.5,1)
awips221 = Proj(proj='lcc',R=6371200,lat_1=50,lat_2=50,lon_0=-107,x_0=-llcrnrx,y_0=-llcrnry)
print awips221(-145.5,1), '(should be close to zero)'
awips218 = Proj(proj='lcc',R=6371200,lat_1=25,lat_2=25,lon_0=-95)
llcrnrx, llcrnry = awips218(-133.459,12.19)
awips218 = Proj(proj='lcc',R=6371200,lat_1=25,lat_2=25,lon_0=-95,x_0=-llcrnrx,y_0=-llcrnry)
print awips218(-133.459,12.19),'(should close to zero)'
x1 = dx*N.indices((ny,nx),'f')[1,:,:]
y1 = dy*N.indices((ny,nx),'f')[0,:,:]
print 'max/min x and y for awips218 grid'
print x1.min(),x1.max()
print y1.min(),y1.max()
x2, y2 = transform(awips218, awips221, x1, y1)
print 'max/min x and y for awips218 grid in awips221 coordinates'
print x2.min(),x2.max()
print y2.min(),y2.max()
x3,y3 = transform(awips221, awips218, x2, y2)
print 'error for reverse transformation back to awips218 coords'
print '(should be close to zero)'
print (x3-x1).min(),(x3-x1).max()
print (y3-y1).min(),(y3-y1).max()
