function X = estconncomps(isfore,dfore,Xpred)

global MINSHAPE MAXSHAPE MEANSHAPE

L = bwlabel(isfore,8);

% get mean, major and minor axis lengths, and orientation for each
% connected component
AREA = 1;
CENTROIDX = 2;
CENTROIDY = 3;
MAJOR = 4;
MINOR = 5;
ORIENTATION = 6;
ECC = 7;
data = weightedregionprops(L,dfore);

% find those with out-of-bounds minor axis length, major axis
% length, eccentricity, and area
nobservations = cols(data);

% try to fix connected components
issmall = data(AREA,:) < MINSHAPE.area | ...
  data(MAJOR,:) < MINSHAPE.major | ...
  data(MINOR,:) < MINSHAPE.minor;
while any(issmall);
  l = find(issmall,1);
  fixsmall;
end;
%islarge = (data(AREA,:) > MAXSHAPE.area) | ...
%          (data(MAJOR,:) > MAXSHAPE.major) | ...
%          (data(MINOR,:) > MAXSHAPE.minor);
islarge = data(AREA,:) > MAXSHAPE.area;
if any(islarge),
  indslarge = find(islarge);
  for l = indslarge,
    fixlarge;
  end;
end;

% delete
isdeleted = isnan(data(1,:));
data(:,isdeleted) = [];

% store in X
X = data([CENTROIDX,CENTROIDY,MAJOR,MINOR,ORIENTATION],:);


