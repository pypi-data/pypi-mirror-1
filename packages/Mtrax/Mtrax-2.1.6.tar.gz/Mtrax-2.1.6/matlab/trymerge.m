global MAXPENALTYMERGE;

canmerge = false;
cannotmerge = false;

% find connected components whose centers are at most
% MAXDMERGE_CENTER from the target
global XPIXELLOC YPIXELLOC;
MAXDMERGECENTER = MAXSHAPE.major+data(MINOR,l)/2;

% first threshold x distance
otherinds = [1:l-1,l+1:cols(data)];
dy = inf(cols(data)-1,1);
d = inf(cols(data)-1,1);
dx = abs(data(CENTROIDX,otherinds)-data(CENTROIDX,l))';
isclose = dx < MAXDMERGECENTER;
cannotmerge = ~any(isclose);

if ~cannotmerge,
  % then threshold y distance
  dy(isclose) = abs(data(CENTROIDY,otherinds(isclose))-...
    data(CENTROIDY,l));
  isclose(isclose) = dy(isclose) < MAXDMERGECENTER;
  cannotmerge = ~any(isclose);
end;

% then threshold Euclidean distance
if ~cannotmerge,
  d(isclose) = dx(isclose).^2 + dy(isclose).^2;
  isclose(isclose) = d(isclose) < MAXDMERGECENTER^2;
  cannotmerge = ~any(isclose);
end;

if ~cannotmerge,
  indsmerge = otherinds(isclose);
  Ll = L==l;
  mergepenalty = inf(1,length(indsmerge));
  for imerge = 1:length(indsmerge),
    lmerge = indsmerge(imerge);
    % compute the ellipse of the two connected components
    datamerge(:,imerge) = weightedregionprops(double(Ll | L==lmerge),dfore);
    % see if the major, minor, area, are small enough
    if (datamerge(AREA,imerge) < MAXSHAPE.area) && ...
          (datamerge(MAJOR,imerge) < MAXSHAPE.major) && ...
          (datamerge(MINOR,imerge) < MAXSHAPE.minor),
      
      % find the pixels that should be foreground according to
      % the ellipse parameters
      r1 = floor(max(1,datamerge(CENTROIDY,imerge) - ...
        datamerge(MAJOR,imerge)/2));
      r2 = ceil(min(NR,datamerge(CENTROIDY,imerge) + ...
        datamerge(MAJOR,imerge)/2));
      c1 = floor(max(1,datamerge(CENTROIDX,imerge) - ...
        datamerge(MAJOR,imerge)/2));
      c2 = ceil(min(NC,datamerge(CENTROIDX,imerge) + ...
        datamerge(MAJOR,imerge)/2));
      ellipseparams = [CENTROIDX,CENTROIDY,MAJOR,MINOR,ORIENTATION];
      isforel = ellipsepixels(data(ellipseparams,l),[r1,r2,c1,c2]) ...
                | L(r1:r2,c1:c2)==l;
      isforelmerge = ellipsepixels(data(ellipseparams,lmerge),...
                                   [r1,r2,c1,c2]) | L(r1:r2,c1:c2)==lmerge;
      isforellmerge = ...
          ellipsepixels(datamerge(ellipseparams,imerge),...
                        [r1,r2,c1,c2]);
      newforemerge = isforellmerge & ~(isforel | isforelmerge);
      % find the total background score for this new region
      % that must be foreground
      dforemerge = dfore(r1:r2,c1:c2);
      mergepenalty(imerge) = sum(max(1-dforemerge(newforemerge),0));
    end;
  end;
  
  % choose to merge with the connected component with minimum
  % merge penalty, if this penalty is small enough
  [minmergepenalty,bestimerge] = min(mergepenalty);
  if minmergepenalty < MAXPENALTYMERGE,
    canmerge = true;
    canmergewith = indsmerge(bestimerge);
  end;
end;

% if we can merge, adjust data
if canmerge,
  % add to canmergewith
  data(:,canmergewith) = datamerge(:,bestimerge);
  issmall(canmergewith) = data(AREA,canmergewith) < MINSHAPE.area | ...
    data(MAJOR,canmergewith) < MINSHAPE.major | ...
    data(MINOR,canmergewith) < MINSHAPE.minor;
  L(L==l) = canmergewith;
  % delete this connected component
  data(:,l) = nan;
  issmall(l) = 0;
end;