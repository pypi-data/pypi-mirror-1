
dat <- read.table("M:/projects/ArcRstats/ArcRstats/example/model/out_cart_samples.txt", header=TRUE, sep = ",", na.strings = "-9999.0")
mdl <- rpart(obs ~ ., data=dat, method="class")

help(package='rpart')
mdl <- rpart(obs ~ ., data=dat, method="class")
summary(mdl)
print(mdl)
printcp(mdl)
plot(mdl, margin=.05); 
text(mdl, use.n=T)

mdl$frame
mdl$splits

raster.names = c('landcov', 'dem', 'aspect', 'tci')
raster.paths = c('M:/projects/ArcRstats/ArcRstats/example/data/landcov', 'M:/projects/ArcRstats/ArcRstats/example/data/dem', 'M:/projects/ArcRstats/ArcRstats/example/data/aspect', 'M:/projects/ArcRstats/ArcRstats/example/data/tci')

inodes = rownames(mdl$frame[mdl$frame$var=="<leaf>",])
lnodes = length(inodes)
paths = path.rpart(mdl, inodes, print.it=F)
nodes = data.frame(nodeid=numeric(lnodes),
			 expression=I(character(lnodes)))
for (i in 1:lnodes){
	nodes[i,] = c(inodes[i], paste(paths[[i]][-1], collapse=" & "))
}

for (i in 1:lnodes){
	ps = paths[[i]][-1]
	for (j in 1:length(ps)){
		for (k in 1:length(raster.names)){
			ps[j] = sub(raster.names[k],raster.paths[k], ps[j])
		}
	}
	nodes[i,] = c(inodes[i], paste(ps, collapse=" & "))
}



ps = paths[[i]][-1]
or s in le

for (r in 1:length(raster.names)){
		sub(raster.names[r],raster.paths[r], )
	}
}

ivar <- which(mdl$frame$var != "<leaf>")
lvar = length(ivar)
splits = data.frame(var=I(character(lvar)),
			  val=numeric(lvar),
			  iframe=numeric(lvar),
			  isplits=numeric(lvar))
for (i in 1:lvar){
	j = ivar[i]
	if (i==1){ 
		k = 1
	} else {
		k = j - 1 + sum(mdl$frame$ncompete[1:(j-1)]) + sum(mdl$frame$nsurrogate[1:(j-1)])
	}
	splits[i,] = c(levels(mdl$frame$var)[mdl$frame$var[j]], 
			  mdl$splits[k,'index'], j, k)
}
splits$isplits


lnodes = length(inodes)
for (i in 1:lnodes){
	p = path.rpart(mdl, inodes[i], print.it=F)
}




nodes = data.frame(var=I(character(lnodes)),
			 val=numeric(lnodes),
			 iframe=numeric(lnodes),
			 isplits=numeric(lnodes))


p = path.rpart(mdl, splits$isplits[2],print.it=F)


nodes = c(2,12,13,7)