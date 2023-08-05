function X = matchidentities(X1,X2,X3)

global MAXDDETECT;

nobservations = cols(X3);

% we will think of each connected component as an observation. some
% observations may correspond to noise, and some targets may not be
% detected. an observation may correspond to two targets currently,
% but two observations do not correspond to one target yet. 

% where do we predict each target will be 
[Xpred,Sigmapred] = cvpred(X1,X2);
istarget = ~isnan(Xpred(1,:));
Xpred(:,~istarget) = [];
Sigmapred(:,~istarget) = [];
ntargetspred = nnz(istarget);

% compute the distance from each observation to each target
% each row corresponds to an observation, each column to a target
D = targetdist2(Xpred,X3,Sigmapred);

% find the nearest obseration to each target
[d,neighbor] = min(D,[],2);

% if the closest distance from a target to its neighbor is too
% large, say the target has disappeared
undetected = d > MAXDDETECT;
if any(undetected),
  neighbor(undetected) = 0;
end;

% check to see if any observation has two targets assigned to it
nassigned = histc(neighbor,1:nobservations);
if any(nassigned > 1),

  % create a dummy observation node for each target and a dummy
  % target node for each observation  
  nnodes = ntargetspred+nobservations;
  % create a weight matrix for minimum perfect bipartite matching
  % let row correspond to target and column observation
  wbip = zeros(nnodes);
  % weight of dummy target to dummy observation node is 0
  % weight of target to observation node is squared distance
  % if squared distance is too large, set weight to infinity
  Dw = D;
  Dw(Dw > MAXDDETECT) = MAXDDETECT+2;
  wbip(1:ntargetspred,1:nobservations) = Dw;
  % weight of real target to dummy observation is MAXDDETECT+epsilon
  wbip(1:ntargetspred,nobservations+1:end) = MAXDDETECT+1;
  % weight of dummy target to real observation is 2*MAXDDETECT
  wbip(ntargetspred+1:end,1:nobservations) = MAXDDETECT+1;
  % use hungarian method to compute matches
  [neighbor,score]=assignmentoptimal(wbip);
  neighbor = neighbor(1:ntargetspred);
  neighbor(neighbor > nobservations) = 0;
  undetected = neighbor == 0;
end;

% choose orientation to match
thetapred = Xpred(ORIENTATION,~undetected);
thetaobs = X3(ORIENTATION,neighbor(~undetected));
doflip = abs(thetapred - thetaobs) > pi/2;
thetaobs(doflip) = thetaobs(doflip) + pi;
thetaobs = mod(thetaobs+pi,2*pi)-pi;
X3(ORIENTATION,neighbor(~undetected)) = thetaobs;

% assign nearest neighbor
X4 = nan(5,ntargetspred);
X4(:,~undetected) = X3(:,neighbor(~undetected));
X = nan(size(X2));
X(:,istarget) = X4;

% observations that are not yet assigned are new targets
isnew = ~ismember(1:nobservations,neighbor);
nnew = nnz(isnew);
if nnew > 0,
  X = [X,nan(5,nnew)];
  X(:,end-nnew+1:end) = X3(:,isnew);
end;