function X = matchidentitiesgreedy(X1,X2,X3)

global MAXDDETECT;

nobservations = cols(X3);

% we will think of each connected component as an observation. some
% observations may correspond to noise, and some targets may not be
% detected. an observation may correspond to two targets currently,
% but two observations do not correspond to one target yet. 

% where do we predict each target will be 
[Xpred,Sigmapred] = cvpred(X1,X2);

% compute the distance from each observation to each target
% each row corresponds to an observation, each column to a target
D = targetdist2(Xpred,X3,Sigmapred);

% find the nearest obseration to each target
[d,neighbor] = min(D,[],2);

% if the closest distance from a target to its neighbor is too
% large, say the target has disappeared
undetected = d > MAXDDETECT | isnan(d);
if any(undetected),
  neighbor(undetected) = 0;
end;

% assign nearest neighbor
X = nan(size(X2));
X(:,~undetected) = X3(:,neighbor(~undetected));

% observations that are not yet assigned are new targets
isnew = ~ismember(1:nobservations,neighbor);
nnew = nnz(isnew);
if nnew > 0,
  X = [X,nan(5,nnew)];
  X(:,end-nnew+1:end) = X3(:,isnew);
end;