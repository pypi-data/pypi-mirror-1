canlowerthresh = false;

% lower threshold around the connected component
global MINBACKTHRESHLOWER;
[NR,NC] = size(isfore);
r1 = floor(max(1,data(CENTROIDY,l)-MAXSHAPE.major/2));
r2 = ceil(min(NR,data(CENTROIDY,l)+MAXSHAPE.major/2));
c1 = floor(max(1,data(CENTROIDX,l)-MAXSHAPE.major/2));
c2 = ceil(min(NC,data(CENTROIDX,l)+MAXSHAPE.major/2));
Ilowerthresh = dfore(r1:r2,c1:c2);
isforelowerthresh = Ilowerthresh >= MINBACKTHRESHLOWER;

% get the new connected component
Llowerthresh = bwlabel(isforelowerthresh);
llowerthresh = Llowerthresh(round(data(CENTROIDY,l)-r1+1),...
  round(data(CENTROIDX,l)-c1+1));
if llowerthresh == 0,
  xlowerthresh = XPIXELLOC(r1:r2,c1:c2);
  ylowerthresh = YPIXELLOC(r1:r2,c1:c2);
  xlowerthresh = xlowerthresh(isforelowerthresh);
  ylowerthresh = ylowerthresh(isforelowerthresh);
  ilowerthresh = argmin((xlowerthresh-data(CENTROIDX,l)).^2+...
    (ylowerthresh-data(CENTROIDY,l)));
  tmp = Llowerthresh(isforelowerthresh);
  llowerthresh = tmp(ilowerthresh);
end;

% get properties of this connected component

datalowerthresh = weightedregionprops(double(Llowerthresh==llowerthresh),Ilowerthresh);
datalowerthresh([CENTROIDX,CENTROIDY]) = ...
    datalowerthresh([CENTROIDX,CENTROIDY]) + [c1-1,r1-1]';

% see if it has been merged with other connected components
Lcrop = L(r1:r2,c1:c2);
tmp = Lcrop(Llowerthresh==llowerthresh);
if any(tmp(:) ~= 0 & tmp(:) ~= l),
  canlowerthresh = false;
  datalowerthresh = data(:,l);
end;

if canlowerthresh,
  % see if it is now big enough
  canlowerthresh = datalowerthresh(MAJOR) >= MINSHAPE.major & ...
      datalowerthresh(MINOR) >= MINSHAPE.minor & ...
      datalowerthresh(AREA) >= MINSHAPE.area;
end;

% if we've determined that just lowering the threshold is the key, then adjust
% the data
if canlowerthresh,
  data(:,l) = datalowerthresh;
  issmall(l) = false;
end;
