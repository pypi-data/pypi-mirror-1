function data = weightedregionprops(L,dfore)

global MINBACKTHRESHLOWER
AREA = 1;
CENTROIDX = 2;
CENTROIDY = 3;
MAJOR = 4;
MINOR = 5;
ORIENTATION = 6;
ECC = 7;

nobservations = max(L(:));
data = zeros(7,nobservations);
for j = 1:nobservations,
  % compute mean
  w = dfore(L==j);
  wnorm = w ./ sum(w);
  [r,c] = find(L==j);
  data(CENTROIDX,j) = sum(c.*wnorm);
  data(CENTROIDY,j) = sum(r.*wnorm);
  % compute variance
  r = r - data(CENTROIDY,j);
  c = c - data(CENTROIDX,j);
  S(1,1) = sum(c.^2.*wnorm);
  S(2,2) = sum(r.^2.*wnorm);
  S(1,2) = sum(r.*c.*wnorm);
  S(2,1) = S(1,2);
  % compute major axis lengths from covariance
  [data(MAJOR,j),data(MINOR,j),data(ORIENTATION,j)] = cov2ell(S);
  % cov2ell returns semimajor and semiminor axis lengths, so
  % multiply be 2
  data(MAJOR,j) = 2*data(MAJOR,j); data(MINOR,j) = 2*data(MINOR,j);
  % compute weighted area
  data(AREA,j) = sum(w/max(max(w),MINBACKTHRESHLOWER));
  % compute eccentricity
  if data(MAJOR,j) == 0,
    data(ECC,j) = 0;
  else,
    data(ECC,j) = data(MINOR,j)/data(MAJOR,j);
  end;
end;
