% fix large connected components
% if a connected component is large, then:
% 1) the connected component corresponds to two targets
% 2) it corresponds to 1 target, but is large because of noise

global MINBACKTHRESHLOWER;
NREPLICATESSPLIT = 10;
MAXITERSSPLIT = 20;

%% try to split the connected component

% data points
[r,c] = find(L==l);
xsplit = [c(:),r(:)]';
w = dfore(L==l)';
w = w / mean(w);
% number of data points
ndata = length(r);
% log-lik for one cluster
S0 = axes2cov(data(MAJOR,l)/2,data(MINOR,l)/2,data(ORIENTATION,l));
mu0 = data([CENTROIDX,CENTROIDY],l);
loglik = sum(w.*normpdfln(xsplit,mu0,chol(S0)));
% BIC for one cluster; note 5 is the number of parameters per Gaussian
BIC = -2*loglik + log(ndata)*5*1;                          

for ncomponents = 2:inf,

  % cluster; in the future, this should really be a weighted gmm
  [mu,S,priors] = mygmm(xsplit',ncomponents,'Replicates',NREPLICATESSPLIT,...
    'MaxIters',MAXITERSSPLIT,'display',-1);
  % choose a cluster for each pixel
  % compute distance to each cluster
  dsplit = zeros(ncomponents,ndata);
  Schol = zeros(size(S));
  for icomponent = 1:ncomponents,
    Schol(:,:,icomponent) = chol(S(:,:,icomponent));
    dsplit(icomponent,:) = mahdist(xsplit,mu(icomponent,:)',...
                                   Schol(:,:,icomponent));
  end;
  % choose smallest 
  [dsplitmin,idx] = min(dsplit,[],1);
  % compute weighted means and variances
  for icomponent = 1:ncomponents,
    wnorm = w(idx==icomponent)';
    wnorm = wnorm / sum(wnorm);
    mu(icomponent,1) = sum(wnorm.*c(idx==icomponent));
    mu(icomponent,1) = sum(wnorm.*c(idx==icomponent));
    dx = c(idx==icomponent)-mu(icomponent,1);
    dy = r(idx==icomponent)-mu(icomponent,2);
    S(1,1,icomponent) = sum(wnorm.*dx.^2);
    S(2,2,icomponent) = sum(wnorm.*dy.^2);
    S(1,2,icomponent) = sum(wnorm.*dx.*dy);
    S(2,1,icomponent) = S(1,2,icomponent);
  end;

  % log-lik for ncomponents clusters
  lik = zeros(1,ndata);
  for icomponent = 1:ncomponents,
    lik = lik + normpdf(xsplit,mu(icomponent,:)',chol(S(:,:,icomponent)));
  end;
  lik = lik / ncomponents;
  loglik(ncomponents) = sum(w.*log(lik));
  
  % compute the BIC for ncomponents clusters
  BIC(ncomponents) = -2*loglik(ncomponents) + log(ndata)*5*ncomponents;
  if BIC(ncomponents) >= BIC(ncomponents-1),
    break;
  end;
  mu0 = mu; S0 = S; idx0 = idx;
end;
ncomponents = ncomponents - 1;

if ncomponents > 1,
  % reset the lth connected component
  data([CENTROIDX,CENTROIDY],l) = mu0(1,:);
  [data(MAJOR,l),data(MINOR,l),data(ORIENTATION,l)] = cov2ell(S0(:,:,1));
  data(MAJOR,l) = 2*data(MAJOR,l);
  data(MINOR,l) = 2*data(MINOR,l);

  % add ncomponents - 1
  inds = sub2ind(size(L),r,c);
  for isplit = 2:ncomponents,
    data([CENTROIDX,CENTROIDY],end+1) = mu0(isplit,:);
    [data(MAJOR,end),data(MINOR,end),data(ORIENTATION,end)] = ...
        cov2ell(S0(:,:,isplit));
    data(MAJOR,cols(data)) = 2*data(MAJOR,cols(data));
    data(MINOR,cols(data)) = 2*data(MINOR,cols(data));
    L(inds(idx0==isplit)) = cols(data);
  end;
end;