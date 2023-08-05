function estback(FILENAME,NFRAMES,NR,NC)

global BACKI BACKTHRESH BACKRATIO BACKHBF BACKTRUNC;

%% parameters
NFRAMESBACK = 100;
HOMOMORPHIC.cutoff = .25;
HOMOMORPHIC.boost = 2;
HOMOMORPHIC.order = 2;
HOMOMORPHIC.uhistogram_cut = 5;
HOMOMORPHIC.nframes_trunc = 10;
HOMOMORPHIC.fskip = 1;
HOMOMORPHIC.maxratio = 3;
HOMOMORPHIC.minratio = 1/3;
NHISTPERFRAME = round(NR*NC/500);
NBINS = 100;
N = NR*NC;

%% create the highboostfilter
BACKHBF = highboostfilter([NR,NC],HOMOMORPHIC.cutoff,...
                      HOMOMORPHIC.order,HOMOMORPHIC.boost);

%% estimate the intensity value at which we will truncate from above

% frames we will estimate from
ftrunc = round(linspace(1,NFRAMES,HOMOMORPHIC.nframes_trunc));

% read in the images
him = zeros(NR,NC,length(ftrunc));
for i = 1:length(ftrunc),
  I = im2double(fmf_read(FILENAME,ftrunc(i),1,1));
  % apply the homomorphic filter
  FFTlogIm = fft2(log(I+.01));
  him(:,:,i) = exp(real(ifft2(FFTlogIm.*BACKHBF)));
end;

% make sure image is still in [0,1]
him = min(max(him,0),1);

% compute the (100 - HOMOMORPHIC.uhistogram_cut) percentile
BACKTRUNC = zeros(1,length(ftrunc));
for i = 1:length(ftrunc),  
  sortv = sort(vectorize(him(:,:,i)));
  sortv = [sortv(1); sortv; sortv(N)];
  x = [0,100*(.5:N-.5)./N,100];
  BACKTRUNC(i) = interp1(x,sortv,100-HOMOMORPHIC.uhistogram_cut);
end;
BACKTRUNC = mean(BACKTRUNC);

%% estimate mean
BACKI = zeros(NR,NC); % mean background with homomorphic filtering
BACKI0 = zeros(NR,NC); % mean background without homomorphic filtering
maxv = zeros(NR,NC);
minv = ones(NR,NC);

% frames we will estimate from
fback = round(linspace(1,NFRAMES-(NFRAMES/NFRAMESBACK),NFRAMESBACK));

hwait = waitbar(0,'Reading in frames to estimate background');
for i = 1:length(fback),

  % read in a frame
  I = im2double(fmf_read(FILENAME,fback(i),1,1));

  % apply homomorphic filtering
  % compute fourier transform
  FFTlogIm = fft2(log(I+.01));
  % apply high pass filter
  him = exp(real(ifft2(FFTlogIm.*BACKHBF)));
  % make sure it is in [0,1]
  him = max(min(him,1),0);
  % truncate
  him = him / BACKTRUNC;

  % incorporate into mean
  BACKI = BACKI + him;
  BACKI0 = BACKI0 + I;
  maxv = max(him,maxv);
  minv = min(him,minv);
  
  if mod(i,10) == 0,
    waitbar(i/length(fback));
  end;
  
end;
  
% normalize mean image
BACKI = BACKI / NFRAMESBACK;
BACKI0 = BACKI0 / NFRAMESBACK;

% compute amount each pixel is brightened/darkenedd
BACKRATIO = BACKI ./ BACKI0;

%% estimate threshold

% choose bincenters. the maximum possible difference from BACKI is the
% difference from 1 or 0 to the minimum or maximum background value
maxbin = max(max( BACKI(:) - minv(:) , maxv(:) - BACKI(:) ));
binlength = maxbin/NBINS;
bincenters = binlength/2:binlength:(maxbin-binlength/2);
binedges = 0:binlength:maxbin;
binedges(end) = maxbin+eps;

bincount = zeros(NBINS,1);

% gather data to cluster
if ishandle(hwait),
  waitbar(0,hwait,'Reading in frames to estimate threshold');
else
  hwait = waitbar(0,'Reading in frames to estimate threshold');
end;

% choose slightly different frames
fback2 = round(linspace(1+NFRAMES/NFRAMESBACK/2,...
  NFRAMES-NFRAMES/NFRAMESBACK/2,NFRAMESBACK));

for i = 1:length(fback2),

  % read in a frame
  I = im2double(fmf_read(FILENAME,fback2(i),1,1));

  % apply homomorphic filtering
  % compute fourier transform
  FFTlogIm = fft2(log(I+.01));
  % apply high pass filter
  him = exp(real(ifft2(FFTlogIm.*BACKHBF)));
  % make sure it is in [0,1]
  him = max(min(him,1),0);
  % truncate
  him = him / BACKTRUNC;

  % compute error
  err = abs(him - BACKI);

  % choose NHISTPERFRAME randomly
  r = ceil(NR*NC*rand(NHISTPERFRAME,1));
  tmp = histc(err(r),binedges);
  bincount = bincount + tmp(1:end-1);
  
  % choose NHISTPERFRAME with highest error
  sortederr = sort(err(:),'descend');
  tmp = histc(sortederr(1:NHISTPERFRAME),binedges);
  bincount = bincount + tmp(1:end-1);
  
  if mod(i,10) == 0,
    waitbar(i/length(fback));
  end;
    
end;

if ishandle(hwait),
  delete(hwait);
end;

% cluster bincountserr into two clusters
[mu,sigma] = histgmm(bincenters,bincount);

% compute crossing point of two gaussians
if abs(1/sigma(1) - 1/sigma(2)) < eps,
  BACKTHRESH = mean(mu);
else
  a = 1./sigma(1) - 1./sigma(2);
  b = - 2 * (mu(1)./sigma(1) - mu(2)./sigma(2));
  c = (mu(1).^2./sigma(1)) + log(sigma(1)) - log(sigma(2));
  d = sqrt(b.^2 - 4*a.*c);
  BACKTHRESH = (-b + d) / (2*a);
  if BACKTHRESH < min(mu) || BACKTHRESH > max(mu),
    BACKTHRESH = (-b - d) ./ (2*a);
  end;
  if BACKTHRESH < min(mu) || BACKTHRESH > max(mu),
    BACKTHRESH = mean(mu);
  end;
end;