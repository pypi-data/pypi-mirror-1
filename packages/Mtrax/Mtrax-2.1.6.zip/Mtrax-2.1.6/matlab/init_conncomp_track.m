function X = init_conncomp_track(I)

% get foreground label
isfore = backsub(I);

% find connected components
L = bwlabel(isfore,8);

% get mean, major and minor axis lengths, and orientation for each
% connected component
stats = regionprops(L,'Centroid','MajorAxisLength', ...
                    'MinorAxisLength','Orientation');

% store in X
ntargets = length(stats);
X = reshape(struct2array(stats),[5,ntargets]);
% convert to radians
X(5,:) = -X(5,:) * pi / 180;