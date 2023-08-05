function [MAXSIZE,MINSIZE,MEANSIZE] = estsize(FILENAME,NFRAMES)

% number of frames to estimate size from
NFRAMESSIZE = 500;
NSTDTHRESH = 2.5;

fsize = round(linspace(1,NFRAMES,NFRAMESSIZE));

major = [];
minor = [];
area = [];

hwait = waitbar(0,'Reading in frames to estimate target size');
for i = 1:NFRAMESSIZE,
  
  % read in the image
  I = fmf_read(FILENAME,fsize(i),1,1);
  
  % do background subtraction
  isfore = backsub(I);
  
  % extract connected components
  L = bwlabel(isfore,8);
  
  % get axis lengths
  stats = regionprops(L,'Area','MajorAxisLength','MinorAxisLength');
  n = length(stats);
  stats = reshape(struct2array(stats),[3,n]);
  area(end+1:end+n) = stats(1,:);
  major(end+1:end+n) = stats(2,:);
  minor(end+1:end+n) = stats(3,:);
  
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
MAXSIZE.major = mumajor + NSTDTHRESH*sigmamajor;
MINSIZE.major = mumajor - NSTDTHRESH*sigmamajor;
MAXSIZE.minor = muminor + NSTDTHRESH*sigmaminor;
MINSIZE.minor = muminor - NSTDTHRESH*sigmaminor;
MAXSIZE.ecc = muecc + NSTDTHRESH*sigmaecc;
MINSIZE.ecc = muecc - NSTDTHRESH*sigmaecc;
MAXSIZE.area = muarea + NSTDTHRESH*sigmaarea;
MINSIZE.area = muarea - NSTDTHRESH*sigmaarea;

MEANSIZE.major = mumajor;
MEANSIZE.minor = muminor;
MEANSIZE.ecc = muecc;
MEANSIZE.area = muarea;
