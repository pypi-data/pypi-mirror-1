function estsize(FILENAME,NFRAMES)

global MINSHAPE MAXSHAPE MEANSHAPE;

% number of frames to estimate size from
NFRAMESSIZE = 500;
NSTDTHRESH = 2.5;

fsize = round(linspace(1,NFRAMES,NFRAMESSIZE));

major = [];
minor = [];
area = [];

AREA = 1;
CENTROIDX = 2;
CENTROIDY = 3;
MAJOR = 4;
MINOR = 5;
ORIENTATION = 6;
ECC = 7;

hwait = waitbar(0,'Reading in frames to estimate target size');
for i = 1:NFRAMESSIZE,
  
  % read in the image
  I = fmf_read(FILENAME,fsize(i),1,1);
  
  % do background subtraction
  [isfore,dfore] = backsub(I);
  
  % extract connected components
  L = bwlabel(isfore,8);
  data = weightedregionprops(L,dfore);
  area = [area,data(AREA,:)];
  major = [major,data(MAJOR,:)];
  minor = [minor,data(MINOR,:)];
  
  if mod(i,5) == 0,
    waitbar(i/NFRAMESSIZE);
  end;
  
end;

ecc = minor ./ major;

% fit Gaussians to the minor, major, eccentricity, and area
mumajor = mean(major);
sigmamajor = std(major,1);
muminor = mean(minor);
sigmaminor = std(minor,1);
muecc = mean(ecc);
sigmaecc = std(ecc,1);
muarea = mean(area);
sigmaarea = std(area,1);


% threshold at NSTDTHRESH standard deviations
MAXSHAPE.major = mumajor + NSTDTHRESH*sigmamajor;
MINSHAPE.major = mumajor - NSTDTHRESH*sigmamajor;
MAXSHAPE.minor = muminor + NSTDTHRESH*sigmaminor;
MINSHAPE.minor = muminor - NSTDTHRESH*sigmaminor;
MAXSHAPE.ecc = muecc + NSTDTHRESH*sigmaecc;
MINSHAPE.ecc = muecc - NSTDTHRESH*sigmaecc;
MAXSHAPE.area = muarea + NSTDTHRESH*sigmaarea;
MINSHAPE.area = muarea - NSTDTHRESH*sigmaarea;
MEANSHAPE.major = mumajor;
MEANSHAPE.minor = muminor;
MEANSHAPE.ecc = muecc;
MEANSHAPE.area = muarea;
