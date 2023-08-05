function X = conncomp_track_frame(X1,X2,I)

%% get foreground label
[isfore,dfore] = backsub(I);

%% estimate positions of targets
X = estconncomps(isfore,dfore);

%% match up identities with previous frame
X = matchidentities(X1,X2,X);