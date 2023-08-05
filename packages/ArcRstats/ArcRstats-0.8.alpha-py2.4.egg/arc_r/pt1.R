# sppproj -- http://r-spatial.sourceforge.net/R/bin/windows/contrib/2.2/spproj_0.3-4.zip
# package spgwr -- spatial geographically weighted regressionm, spgwr

grid.path = 'G:/projects/ArcRstats/example/data/landcov-3'
grid.path = 'G:/projects/ArcRstats/example/data/landcov'
library(rgdal)  # requires sp
grid.sg = readGDAL(grid.path)
getClass(class(grid.sg))  # inspect slots of class
# ie grid.sg@proj4string@projargs
grid.im = as.image.SpatialGridDataFrame(grid.sg)
#image(grid.im)
n=100
pts.smp = spsample(grid.sg, n, "random", offset=c(0.5,0.5), iter=10)
pts.proj4string = pts.smp@proj4string
getClass(class(pts.smp))
 	# "random", "regular", "stratified", "nonaligned"
pts.xy = coordinates(pts.smp)
pts.df = data.frame(x=pts.xy[,1], y=pts.xy[,2], presence=rep(0,nrow(pts.xy)))
nrow(pts.xy)
pts.smp = SpatialPointsDataFrame(pts.xy, pts.df)
pts.path = 'G:/projects/ArcRstats/example/data/landcov_pts_smp'
library(maptools)  # requires sp
write.pointShape(pts.xy, pts.df, pts.path)


pts.smp = SpatialPointsDataFrame(pt.smp, 
			data=AttributeList(list(presence=rep(0,n))))
points(pts.spsample)

data(pts.spsample)


     balt_orig <- readShapePoints(system.file("shapes/baltim.shp", package="maptools")[1])
     plot(balt_orig)
     balt_cheap <- balt_orig[balt_orig$PRICE < 40,]
     file <- tempfile("")
     write.pointShape(coordinates=coordinates(balt_cheap), df=as(balt_cheap, "data.frame"), file)
     getinfo.shape(paste(file, ".shp", sep=""))
     balt_new <- readShapePoints(paste(file, ".shp", sep=""))
     plot(balt_new, col="red", pch=16, add=TRUE)


readGDAL(grid.pth)$CRS
