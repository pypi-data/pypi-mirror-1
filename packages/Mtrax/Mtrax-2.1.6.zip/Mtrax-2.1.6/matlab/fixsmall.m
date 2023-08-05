% a small connected component either corresponds to:
% 1) spurious noise
% 2) part of a target, the other part of which is another
% connected component
% 3) part of a target, the other part of which was not detected
% as foreground
% 4) a target which is actually small

% action to take:
% 1) delete connected component
% 2) merge with other connected component
% 3) detect the rest of the target as foreground, and add to
% connected component
% 4) none

% properties:
% 1) the area is smaller than MAXAREADELETE, it is far from other
% connected components that it could be merged with, there are
% no pixels connected to it that are close to foreground in
% appearance and could make it larger than MINSHAPE.area. 
% 2) there is a connected component that is close to it that it
% can be added to. 
% 3) the foreground threshold can be lowered slightly near the
% connected component to increase its size, but 2) does not
% apply. 
% 4) none of the above apply. 

%% determine if the foreground threshold can be lowered slightly to
%% allow the size of the ellipse to increase
trylowerthresh;

%% determine if this connected component can be merged with another
%% connected component
if ~canlowerthresh,
  trymerge;
end;

%% if the area is small, just delete this connected component
candelete = false;
global MAXAREADELETE;
if ~canlowerthresh & ~canmerge,
  % is it very small even if we lower the threshold?
  if datalowerthresh(AREA) < MAXAREADELETE,
    % then just delete it
    candelete = true;
    data(:,l) = nan;
    issmall(l) = 0;
  else,
    % otherwise, grow the region
    data(:,l) = datalowerthresh;
  end;
end;

%% if none of the above apply, then do nothing
if ~canlowerthresh & ~canmerge & ~candelete,
  issmall(l) = false;
end;