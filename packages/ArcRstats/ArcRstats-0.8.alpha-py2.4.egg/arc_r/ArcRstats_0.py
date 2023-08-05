'''
ArcRstats.py (version 0.5, 2005-06-13) - multivariate modeling script for ArcGIS

This script can be used with ArcGIS to produce predictive maps based on
different techniques using the free and robust R statistical package:
    Generalized Linear Model (GLM)
    Generalized Additive Model (GAM)
    Classification and Regression Tree (CART)    

This script can be used within the ESRI ModelBuilder environment.  A basic script interface
is included in the ArcRstats.tbx which can be viewed and used from ArcCatalog.  Dragging the
respective toolbox script (GLM, GAM or CART) into a new model allows you to connect the input
points and rasters as well as defining the output prediction raster and sampling tables.
Example data and model runs are included in the toolbox, which you can run by simply pressing
the play button.

Models are inherently flawed.  You are strongly advised to research the strengths and
weaknesses of these different techniques as well as understanding their outputs, neither of
which are explained with this tool.  The help for each of the R commands should be consulted.
See the out_mdl.r file (where out_mdl is the name of your output prediction raster) to re-create
the R session and try help(glm), help(gam) or help(rpart) after loading the necessary package,
which is library(mgcv) for GAM and library(rpart) for CART.  Also look at the help for the
predict.glm, predict.gam and predict.rpart functions.  A good habitat modeling review paper for
more background on these modeling techniques is:

  Guisan, A., and N.E. Zimmermann. 2000, Predictive Habitat Distribution Models in Ecology: Ecol. Mod. 135 147-186.

Inputs / Outputs:
    in_absence - any point feature class
    in_presence - any point feature class
    in_rasters - on or more rasters
    out_mdl - output predicted raster

Requires:
    ArcGIS version 9 or higher (http://www.esri.com)
        + Spatial Analyst extension
    R version 2 or higher (http://www.r-project.org)
        + COM(D) Server for R (http://cran.r-project.org/contrib/extra/dcom)
    Python 2.1 or higher (http://www.python.org), included with ArcGIS 9 or higher
        + win32com module (http://starship.python.net/crew/mhammond)

Term of Use:
  This program is public domain under the GNU General Public License (www.gnu.org/copyleft/gpl.html).
  We provide this software with absolutely no warranty.  If you use this, please cite with the following:

    Best, B. D., S. Loarie, S. Qian, P. Halpin, D. Urban, 2005.  ArcRstats - multivariate habitat modeling with ArcGIS and R statistical software.
      Available at http://www.nicholas.duke.edu/geospatial/software.

Authors:
    Ben Best <bbest at duke dot edu>
    Scott Loarie <srl6 at duke dot edu>
    Song Qian <song at duke dot edu>
    Patrick Halpin <phalpin at duke dot edu>
    Dean Urban <deanu at duke dot edu>
    
    Duke University Geospatial Analysis Program
    http://www.nicholas.duke.edu/geospatial

Versions :
    0.6 (2005-08-02):
        - fixed factor(obs) for CART and logit function for GLM/GAM
    0.5 (2005-06-13):
        - fixed for use with long path names by converting to short path names (especially for gp.Describe BUG)
        - updated GLM to handle NAs more efficiently
    0.4 (2005-05-23):
        - updated terms of use with citation
    0.3 (2005-05-19):
        - fixed bug during GAM formula creation
        - created basic help pdf doc
    0.2 (2005-05-08):
        - fixed projection of model output grid
        - changed from tempfile grid output to *.asc
        - cleaned up large variables from memory
        - validated _Example models so output not already generated in ModelBuilder
        - supplemented documentation
    0.0.1 (2005-05-04):
        - first beta version

TODO : error check for ArcGIS, ArcGIS Spatial Analyst, R, and RCOM Server
TODO : when feeding data to predict in R, remove unused coefficients from data frame (since NAs are excluded)
TODO : check in_absence/presence for raster or point locations, not just "dataset"
TODO : check for autodelete if exists in gp environment
TODO : add ROC to GLM/GAM...
TODO : work on other basic statistical tests, like T-tests, Moran's I stuff
TODO : failover R, launch R and capture real error using the R package "session"
TODO : check raster name length when creating reprojected (*_r) and integer (*_i) rasters
TODO : handle big grids with map algebra statement for GLM and CART
TODO : output error/deviance grids too
TODO : setup listserve for sending updates to users
TODO: write-up explanation for example dataset
'''

# import modules
from win32com.client import Dispatch
import os, sys, re, time, shutil    # removed: tempfile, preferable to use win32api.GetTempFileName anyways
from win32api import GetShortPathName

# debug options
debug = 0   # 1 or 0
if debug:
    fxn         = 'glm' # 'glm' , 'cart' or 'gam'
    prefix      = 'D:/projects/ArcRstats/'
    in_obs      = prefix + 'sp_obs.shp'
    in_rnd      = prefix + 'sp_rnd.shp'
    in_rnames   = ['dem', 'aspect', 'tci', 'landcov']
    sep         = ';' + prefix
    in_rasters  = prefix + sep.join(in_rnames)
    out_mdl     = prefix + 'out_' + fxn
    out_dbf_obs = out_mdl + '_smpl_obs.dbf'
    out_dbf_rnd = out_mdl + '_smpl_rnd.dbf'

class RModel:
    def __init__(self):
        pass

    def msg(self, msg):
        # utility message function
        
        self.gp.AddMessage(msg)          # print to geoprocessor
        print msg                   # print to console
        self.rlog.write('# %s\n' % msg) # append to log file
        
    def rcmd(self, cmd):
        # utility R command function
        
        try:    
            self.r.EvaluateNoReturn(cmd) # run command
        except:
            self.msg('Unexpected error with R command...\n' + str(cmd) + '\n' + str(self.r.GetErrorText()) + '\n' + str(sys.exc_info()[0]))
            raise
            #sys.exit()
        self.rlog.write(cmd+'\n')   # append to log file

    def initialize(self):    
        # initialization calls

        # get input variables
        global fxn
        self.fxn = fxn                                     # input, function to use in modeling
        # comment below to debug
        if debug:
            global in_obs, in_rnd, in_rasters, out_mdl, out_dbf_obs, out_dbf_rnd
            self.in_obs      = in_obs
            self.in_rnd      = in_rnd
            self.in_rasters  = in_rasters
            self.out_mdl     = out_mdl
            self.out_dbf_obs = out_dbf_obs
            self.out_dbf_rnd = out_dbf_rnd
        else:
            self.in_obs      = GetShortPathName(sys.argv[2])   # input, observed points featureclass
            self.in_rnd      = GetShortPathName(sys.argv[3])   # input, random points featureclass
            self.in_rasters  = sys.argv[4]                     # input, multiple rasters
            self.out_mdl     = GetShortPathName(os.path.dirname(sys.argv[5])) + '/' + os.path.basename(sys.argv[5])   # output modeled raster
            self.out_dbf_obs = GetShortPathName(os.path.dirname(sys.argv[6])) + '/' + os.path.basename(sys.argv[6])   # output sampled obs dbf
            self.out_dbf_rnd = GetShortPathName(os.path.dirname(sys.argv[7])) + '/' + os.path.basename(sys.argv[7])   # output sampled rnd dbf
        
        # assign other output filenames
        self.cwd         = GetShortPathName(os.path.dirname(self.out_mdl))
        self.samplesfile = self.out_mdl + '_samples.txt'
        self.rlogfile    = self.out_mdl + '_log.r'

        # open r_log
        self.rlog = open(self.rlogfile, 'w')
        self.rlog.write('# ' + self.fxn.upper() + ' started on ' + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + '\n')

        # initialize geoprocessor
        self.gp = Dispatch("esriGeoprocessing.GpDispatch.1")
        self.gp.CheckOutExtension("Spatial")

        # initialize R stats
        self.r = Dispatch("StatConnectorSrv.StatConnector")
        self.r.Init("R")

        # setup dictionary list variables
        self.msg('  setup variables...')
        self.rasters = {}                    # dictionary of raster paths by raster name
        self.samples = {}                      # dictionary of sample value lists by raster name
        self.samples['obs'] = []               # known response sample value list
        for path in self.in_rasters.split(';'):
            path = path.replace("'","");
            name = os.path.basename(path)
            self.rasters[name] = GetShortPathName(path)
            self.samples[name] = []

    def sample2r(self):
        self.msg('  sample rasters...')

        # check if integer rasters b/c of SAMPLE bug in ArcGIS 9 (supposedly fixed in 9.1)
        self.rasters_int = self.rasters.copy()
        for name, path in self.rasters.items():
            desc = self.gp.Describe(path)
            if not desc.IsInteger:
                path_int = path+'_i'
                self.msg('    raster %s being converted to integer (b/c ArcGIS SAMPLE bug)' % name)
                try:
                    if self.gp.Exists(path_int):
                        self.gp.Delete(path_int)                    
                    self.gp.MultiOutputMapAlgebra_sa(path_int + ' = INT(' + path + ' * 1000)') # multiply 1000
                except:
                    self.msg(gp.GetMessages())
                self.rasters_int[name] = path_int
        sep = ';'
        self.rasters_intstr = sep.join(self.rasters_int.values())

        # initialize geoprocessor
        del self.gp
        self.gp = Dispatch("esriGeoprocessing.GpDispatch.1")
        self.gp.CheckOutExtension("Spatial") 

        # sample across rasters for observed and random locations
        if os.path.exists(self.out_dbf_obs):
            os.unlink(self.out_dbf_obs)
        if os.path.exists(self.out_dbf_rnd):
            os.unlink(self.out_dbf_rnd)
        try:
            self.gp.Sample_sa(self.rasters_intstr, self.in_obs, self.out_dbf_obs, 'NEAREST')
            self.gp.Sample_sa(self.rasters_intstr, self.in_rnd, self.out_dbf_rnd, 'NEAREST')
        except:
            print 'ERROR: ' + self.gp.GetMessages()

        # read in sampled presence (observation) tables
        self.msg('  read in sampled tables...')
        rows = self.gp.SearchCursor(self.out_dbf_obs)
        row = rows.Next()
        while row:
            self.samples['obs'].append(1)           # set to 1 for obs, 0 for rnd
            for col in self.rasters.keys():         # iterate through sampled columns
                # correct for integer conversion b/c of SAMPLE bug in ArcGIS 9 (supposedly fixed in 9.1)
                if self.rasters[col] == self.rasters_int[col]:
                    val = row.GetValue(col)
                else:
                    col_int = os.path.basename(self.rasters_int[col])
                    val = row.GetValue(col_int) / 1000  # divide 1000
                self.samples[col].append(val)
            row = rows.Next()                       # advance to next row

        # read in sampled absence (random) tables
        rows = self.gp.SearchCursor(self.out_dbf_rnd)
        row = rows.Next()
        while row:
            self.samples['obs'].append(0)           # set to 1 for obs, 0 for rnd
            for col in self.rasters.keys():         # iterate through sampled columns
                # correct for integer conversion b/c of SAMPLE bug in ArcGIS 9 (supposedly fixed in 9.1)
                if self.rasters[col] == self.rasters_int[col]:
                    val = row.GetValue(col)
                else:
                    col_int = os.path.basename(self.rasters_int[col])
                    val = row.GetValue(col_int) / 1000  # divide 1000
                self.samples[col].append(val)
            row = rows.Next()                       # advance to next row

        # write out samplesfile.txt
        f=open(self.samplesfile, 'w')
        for i in range(len(self.samples['obs'])):
            rowdata = []
            for k in self.samples.keys():
                if i == 0:                          # header row
                    rowdata.append(str(k))
                else:
                    v = str(self.samples[k][i])
                    rowdata.append(v)
            sep = ','
            f.write(sep.join(rowdata) + '\n')
        f.close()

        # read into R
        self.rcmd('dat <- read.table("' + self.samplesfile.replace('\\','/') + '", header=TRUE, sep = ",", na.strings = "-9999.0")')
        del(self.samples)   # clean up python memory
        
    def grids2r(self):

        # feed grid data to R
        self.msg('  feed grid data to R for predicting with model...')

        # find grid with largest cellsize
        cellwidth = 0
        self.cellsizes = {}
        self.extents = {}
        self.sprefs = {}
        for n,p in self.rasters.items():
            descr = self.gp.Describe(p)
            self.cellsizes[n] = str(descr.MeanCellWidth)
            self.extents[n] = str(descr.Extent)
            self.sprefs[n] = descr.SpatialReference
            if descr.MeanCellWidth > cellwidth:
                # assign as template raster
                self.template = n
        self.msg('    template grid with largest cell size: ' + n)

        # set environment based on cellraster
        self.gp.Workspace = self.cwd
        self.gp.OutputCoordinateSystem = self.sprefs[self.template]
        self.gp.Extent = self.extents[self.template]  # snap grid
        self.msg('    resample other grids, if different cellsize/extent from template...')
        # resample and size, if necessary
        for n,p in self.rasters.items():
            if self.cellsizes[n] <> self.cellsizes[self.template] or self.extents[n] <> self.extents[self.template]:
                try:
                    if self.gp.Exists(p + '_r'):
                        self.gp.Delete(p + '_r')
                    self.gp.Resample(p, p + '_r', self.cellsizes[self.template], 'NEAREST')
                    #gp.Clip(p + '_r', cellextent, p + '_c')
                except:
                    print self.gp.GetMessages()
                # assign resampled/resized raster path to rasters dictionary
                self.rasters[n] = p+'_r'

        # output to ascii, read into R
        self.msg('    output grids to temporary ASCII files and read into R...')
        self.rasters_asc = self.rasters.copy()
        for n,p in self.rasters.items():
            # get temporary ascii output name
            #self.rasters_asc[n] = tempfile.mktemp('.asc').replace('\\','/')
            p_asc = p + '.asc'
            self.rasters_asc[n] = p_asc
            if os.path.exists(p_asc):
                os.unlink(p_asc)
            try:
                self.gp.RasterToASCII_conversion(p, p_asc)
            except:
                self.msg(self.gp.GetMessages())

            # read ascii table into R as a vector for model prediction
            self.rcmd(n + ' <- read.table("' + self.rasters_asc[n].replace('\\','/') + '", sep=" ", na.strings="-9999", skip=6)')
            self.rcmd(n + ' <- as.vector(data.matrix(' + n + '[-length(' + n + ')]))')	# exclude trailing column created by extra space in RasterToASCII output

            # get header information from template for outputting model prediction from R to ASCII ArcGIS Raster format
            self.header = {}
            if n == self.template:
                # read in header info
                f=open(self.rasters_asc[n], 'r')
                self.header['ncols']         = re.match('([\S]+)\s+([\S]+)', f.readline()).groups()[1]
                self.header['nrows']         = re.match('([\S]+)\s+([\S]+)', f.readline()).groups()[1]
                self.header['xllcorner']     = re.match('([\S]+)\s+([\S]+)', f.readline()).groups()[1]
                self.header['yllcorner']     = re.match('([\S]+)\s+([\S]+)', f.readline()).groups()[1]
                self.header['cellsize']      = re.match('([\S]+)\s+([\S]+)', f.readline()).groups()[1]
                self.header['NODATA_value']  = re.match('([\S]+)\s+([\S]+)', f.readline()).groups()[1]
                f.close()

        # write out header info to output model grid ascii file
        self.out_mdl_ascii = self.out_mdl + '.asc'
        f=open(self.out_mdl_ascii, 'w')
        for k, v in self.header.items():
            f.write('%s %s\n' % (k, v))
        f.close()

        # bind to data frame in R
        sep = ', '
        self.rcmd('datpred <- data.frame(cbind(' + sep.join(self.rasters.keys()) + '))')
        # clear old variables from R session memory
        for n in self.rasters.keys():
            self.rcmd('rm('+n+')')

    def pred2gis(self):

        # expects a predict object named 'pred' in R
        self.msg('  convert model prediction to grid...')
        self.rcmd('write.table(pred, file="' + self.out_mdl_ascii.replace('\\','/') + '", append=TRUE, sep=" ", col.names=FALSE, row.names=FALSE, na="-9999")')
        try:
            if self.gp.Exists(self.out_mdl):
                self.gp.Delete(self.out_mdl)
            self.gp.ASCIIToRaster_conversion(self.out_mdl_ascii, self.out_mdl, "FLOAT")
            self.gp.Toolbox = "Management"
            # this should work, but the SpatialReference returns an object, not the expected *.prj file DefineProjection wants
            #self.gp.DefineProjection(self.out_mdl, self.sprefs[template])
        except:
            print self.gp.GetMessages()
        # project model raster by copying prj.adf
        prj = self.rasters[self.template] + '/prj.adf'
        if os.path.exists(prj):
            shutil.copyfile(prj, self.out_mdl + '/prj.adf')

    def plotsamples(self):
        self.rcmd('plotpre <- "' + self.out_mdl.replace('\\','/') + '"')
        self.rcmd('datenv <- dat[,names(dat)!="obs"]')
        self.rcmd('png(paste(sep='', plotpre, "_plotpairs.png"))')
        self.rcmd('pairs(datenv, main="Correlations Between Variables")')
        self.rcmd('dev.off()')
        self.rcmd('''for (c in names(datenv)){
                        denspres <- density(na.exclude(dat[dat[["obs"]]==1, c]))
                        densabs  <- density(na.exclude(dat[dat[["obs"]]==0, c]))
                        xlim <- range(na.exclude(dat[, c]))
                        ylim <- c(0,max(c(denspres$y, densabs$y)))
                        #png(filename=filename, width=600, height=400, pointsize=1, bg="white", res=200)
                        png(paste(sep='', plotpre, '_hist_', c, '.png'))
                        plot(denspres, type='l', main=paste(c,'Distribution'), xlab=c, ylab='Density', ylim=ylim, xlim=xlim)
                        lines(densabs, lty=2)
                        legend(x=xlim[1], y=ylim[2], legend=c('presence', 'absence'), lty=1:2)
                        dev.off()
                    }''')
        
    def finalize(self):
        # clean up temp files
##        if not debug:
##            for n,p in self.rasters_asc.items():
##                os.unlink(p)

        # close r
        self.r.Close()        
        self.rlog.close()

        # close gp
        del(self.gp)
        
class GLM(RModel):
    def __init__(self):
        # initialize
        self.initialize()

        # sample data
        self.sample2r()
        self.plotsamples()

        # build model
        self.msg('  generate GLM in R...')
        self.rcmd('dat$obs <- factor(dat$obs)')
        self.rcmd('dat <- na.exclude(dat)')
        self.rcmd('mdlall <- glm(obs ~ ., data=dat, family=binomial(link="logit"))')
        self.msg('  find best GLM model by AIC...')
        self.rcmd('library(MASS)')
        self.rcmd('mdl <- stepAIC(mdlall, trace=F)')

        # save model summaries
        self.rcmd('sink("' + self.out_mdl.replace('\\','/') + '_summary.txt")')
        self.rcmd('cat("\nGLM all..\n\n")')
        self.rcmd('print(summary(mdlall))')
        self.rcmd('cat("\nGLM best model, with step-wise AIC selection of coefficients...\n\n")')
        self.rcmd('print(summary(mdl))')
        self.rcmd('sink()')

        # grid data
        self.grids2r()

        # predict with model
        self.msg('  predict GLM in R...')
        #self.rcmd('rowsna <- sort(unique(which(is.na(datpred), arr.ind=TRUE)[,1]))')
        #self.rcmd('datpred <- na.exclude(datpred)')
        self.rcmd('pred <- predict(mdl, newdata=datpred, na.action=na.pass, type="response")')
        #self.rcmd('''for (row in rowsna){
        #                pred <- append(pred, NA, row-1)
        #            }''')
        self.rcmd('dim(pred) <- c(' + self.header['nrows'] + ', ' + self.header['ncols'] + ')')        

        # save model and data
        self.rcmd('save(dat, mdlall, mdl, datpred, pred, file = "' + self.out_mdl.replace('\\','/') + '.rdata")')

        # prediction to grid
        self.pred2gis()
        self.finalize()

class GAM(RModel):
    def __init__(self):
        # initialize
        self.initialize()

        # sample data
        self.sample2r()
        self.plotsamples()

        # construct formula
        self.msg('  generate GAM formula...')
        terms = []
        for k in self.rasters.keys():
            terms.append('s(' + k + ', bs="ts")')
        sep = ' + '
        formula = 'obs ~ ' + sep.join(terms)

        # build model
        self.msg('  generate GAM in R...')        
        self.rcmd('dat$obs <- factor(dat$obs)')
        self.rcmd('library(mgcv)')
        self.rcmd('mdl <- gam(' + formula + ', data=dat, family=binomial(link="logit"))')

        # save model summary and graphics
        self.rcmd('sink("' + self.out_mdl.replace('\\','/') + '_summary.txt")')
        self.rcmd('cat("\nGAM..\n\n")')
        self.rcmd('print(summary(mdl))')
        self.rcmd('sink()')
        self.rcmd('png("' + self.out_mdl.replace('\\','/') + '_plot.png")')
        self.rcmd('plot(mdl,pages=1,residuals=TRUE,all.terms=TRUE,shade=TRUE,shade.col="gray")')
        self.rcmd('dev.off()')

        # grid data   
        self.grids2r()

        # predict with model
        self.msg('  predict with GAM in R...')
        self.rcmd('rowsna <- sort(unique(which(is.na(datpred), arr.ind=TRUE)[,1]))')
        self.rcmd('datpred <- na.exclude(datpred)')
        self.rcmd('pred <- predict(mdl, newdata=datpred, type="response", block.size=0.5, newdata.guaranteed=FALSE)')
        self.rcmd('''for (row in rowsna){
                        pred <- append(pred, NA, row-1)
                    }''')
        self.rcmd('dim(pred) <- c(' + self.header['nrows'] + ', ' + self.header['ncols'] + ')')

        # save model and data
        self.rcmd('save(dat, mdl, datpred, pred, file = "' + self.out_mdl.replace('\\','/') + '.rdata")')

        # prediction to grid
        self.pred2gis()
        self.finalize()

class CART(RModel):
    def __init__(self):
        # initialize
        self.initialize()

        # sample data
        self.sample2r()
        self.plotsamples()

        # build model
        self.msg('  generate CART in R...')
        self.rcmd('dat$obs <- factor(dat$obs)')
        self.rcmd('library(rpart)')
        self.rcmd('mdlall <- rpart(obs ~ ., data=dat, control=rpart.control(cp=0), method="class")')
        self.rcmd('mdlall.cp <- mdlall$cptable[mdlall$cptable[,4] == min(mdlall$cptable[,4]), 1]')
        self.msg('  trim CART (complexity parameter with minimum cross-validation error)...')
        self.rcmd('mdl <- rpart(obs ~ ., data=dat, control=rpart.control(cp=mdlall.cp), na.action=na.pass, method="class")')

        # save model summary and graphics
        self.msg('  plot CART tree from R...')
        self.rcmd('png("' + self.out_mdl.replace('\\','/') + '_tree.png")')
        self.rcmd('plot(mdl)')
        self.rcmd('text(mdl, use.n=TRUE)')
        self.rcmd('dev.off()')
        self.rcmd('sink("' + self.out_mdl.replace('\\','/') + '_summary.txt")')
        self.rcmd('cat("\nFull CART (cp=0)...\n\n")')
        self.rcmd('print(summary(mdlall))')
        self.rcmd('cat("\n\nModified CART (using",str(mdlall.cp),"as complexity parameter from Full CART)...\n\n")')
        self.rcmd('print(summary(mdl))')
        self.rcmd('sink()')

        # grid data   
        self.grids2r()

        # predict with model
        self.msg('  predict CART in R...')
        self.rcmd('pred <- predict(mdl, newdata=datpred, na.action=na.pass, type="prob")[,2]')  # the probability of it being the second answer ( = 1 = presence)
        self.rcmd('dim(pred) <- c(' + self.header['nrows'] + ', ' + self.header['ncols'] + ')')

        # save model and data
        self.rcmd('save(dat, mdl, datpred, pred, file = "' + self.out_mdl.replace('\\','/') + '.rdata")')

        # prediction to grid
        self.pred2gis()
        self.finalize()

if __name__ == "__main__":
    # main call

    if not debug:
        fxn      = sys.argv[1]   # function switch as first argument

    if fxn == 'glm':
        GLM()
    elif fxn == 'gam':
        GAM()
    elif fxn == 'cart':
        CART()                
