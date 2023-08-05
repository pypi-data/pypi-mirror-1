%% read in the data

addpath ../../FlyMovieFormat/matlab/
FILENAME = '/common/kristin/walking_arena/movie20070312_140047.fmf';
[header_size,version,NR,NC,bytes_per_chunk,max_n_frames,data_format] = ...
    fmf_read_header( FILENAME );
NFRAMES = max_n_frames;
NFRAMESPERCHUNK = 20;

%% fixed parameters

% weight of each parameter when computing pairwise distance
global SIGMAMOTION;
SIGMAMOTION = [1,1,1,1,inf]';
% dampening of constant velocity
global DAMPEN;
DAMPEN = [.9,.9,.5,.5,.5]';
% currently, we are only looking for the angle mod pi
global MODPI;
MODPI = true;
global MAXDDETECT;
MAXDDETECT = 15^2 + 2^2 + 2^2 + 3^2;

% minimum number of frames a target must be around
MINNFRAMES = 5;

%% allocate
XTRACK = cell(NFRAMES,1);

%% estimate background
global BACKI BACKTHRESH BACKRATIO BACKHBF BACKTRUNC;
global MINBACKTHRESHLOWER;
MINBACKTHRESHLOWER = .75;
load backdata.mat;
%estback(FILENAME,NFRAMES,NR,NC);

%% estimate the size of the targets
global MINSHAPE MAXSHAPE MEANSHAPE;
global MAXAREADELETE;
MAXAREADELETE = 3;
global MAXPENALTYMERGE;
MAXPENALTYMERGE = 4; % number of pixels that must be made foreground
                     % when really background
%estsize(FILENAME,NFRAMES);
load sizedata.mat 
 
% pixel locations
global XPIXELLOC YPIXELLOC;
[XPIXELLOC,YPIXELLOC] = meshgrid(1:NC,1:NR);

%% read in some frames
ffirstread = 1;
flastread = 0;
[I,flastread] = read_fmf_chunk(FILENAME,flastread+1,NFRAMESPERCHUNK,NFRAMES);

%% initialize first frame
XTRACK = init_conncomp_track(I(:,:,1));
XTRACK = cat(3,XTRACK,nan([rows(XTRACK),cols(XTRACK),NFRAMES-1]));
drawresults(XTRACK(:,:,1),I(:,:,1));
title('1');
drawnow;
%input('1');

%% initialize second frame
Xnew = conncomp_track_frame(XTRACK(:,:,1),XTRACK(:,:,1),I(:,:,2));
if cols(Xnew) > cols(XTRACK),
  XTRACK(:,end+1:end+cols(Xnew)-cols(XTRACK),:) = nan;
elseif cols(Xnew) < cols(XTRACK),
  Xnew(:,end+1:end+cols(XTRACK)-cols(Xnew),:) = nan;
end;
XTRACK(:,:,2) = Xnew;
f = 2;
% delete tracks that are only around for MINNFRAMES or less
% frames
deleteshorttracks;
drawresults(XTRACK(:,:,1:2),I(:,:,2));
title('2');
drawnow;
%input('2');

%% track
f = 3;
tic;
for f = f:NFRAMES,

  if f > flastread | f < ffirstread,
    ffirstread = f;
    [I,flastread] = read_fmf_chunk(FILENAME,f,NFRAMESPERCHUNK,NFRAMES);
  end;
  
  Xnew = conncomp_track_frame(XTRACK(:,:,f-2),XTRACK(:,:,f-1),...
    I(:,:,f-ffirstread+1));
  
  if cols(Xnew) > cols(XTRACK),
    %keyboard;
    XTRACK(:,end+1:end+cols(Xnew)-cols(XTRACK),:) = nan;
  elseif cols(Xnew) < cols(XTRACK),
    %keyboard;
    Xnew(:,end+1:end+cols(XTRACK)-cols(Xnew),:) = nan;
  elseif nnz(~isnan(Xnew(1,:))) ~= nnz(~isnan(XTRACK(1,:,f-1))),
    %keyboard;
  end;
  XTRACK(:,:,f) = Xnew;

  % delete tracks that are only around for MINNFRAMES or less
  % frames
  deleteshorttracks;

%  if mod(f,20) == 0,
  drawresults(XTRACK(:,:,max(1,f-100):f),I(:,:,f-ffirstread+1));
  axis image;
  title(num2str(f));
  drawnow;
%  input(num2str(f));
%  end;
  if toc > 600,
    save tmp.mat;
    tic;
  end;
end;

save tmp.mat;

makemovie;
