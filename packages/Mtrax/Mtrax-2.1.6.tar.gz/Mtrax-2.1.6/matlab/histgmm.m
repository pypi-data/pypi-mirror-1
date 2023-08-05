function [mu,sigma,prior] = histgmm(x,w,varargin)

[n,m] = size(w);
w = w ./ repmat(sum(w,1),[n,1]);
x = repmat(x(:),[1,m]);

[maxiters,minchange,minsigma] = myparse(varargin,'maxiters',100,'minchange',(x(end)-x(1))/n/2,...
                                        'minsigma',(x(end)-x(1))/n/2);

%% initialize

% first initialization scheme
mu0 = zeros(2,m);
mu0(1,:) = x(1,:);
mu0(2,:) = x(end,:);
sigma0 = (x(end)-x(1))/4*ones(2,m);
gamma = .5*ones(n,m);
prior = .5*ones(2,m);

[mu,sigma,prior,score1] = main(mu0,sigma0,gamma,prior,w,x,maxiters,minchange,minsigma,n,m);

% second initialization scheme
c = [zeros(1,m);cumsum(w,1)];
gamma = double(c(1:end-1,:) < .5);
mu0 = zeros(2,m);
sigma0 = zeros(2,m);
tmp = w.*gamma;
prior(1,:) = sum(tmp,1);
isprior = prior(1,:) > 0;
mu0(1,isprior) = sum(tmp(:,isprior).*x(:,isprior),1)./prior(1,isprior);
sigma0(1,isprior) = ...
    sqrt(sum( tmp(:,isprior).*(x(:,isprior)-repmat(mu0(1,isprior),[n,1])).^2 , 1)./...
         prior(1,isprior));
tmp = w.*(1-gamma);
prior(2,:) = sum(tmp,1);
isprior = prior(2,:) > 0;
mu0(2,isprior) = sum(tmp(:,isprior).*x(:,isprior),1)./prior(2,isprior);
sigma0(2,isprior) = ...
    sqrt(sum( tmp(:,isprior).*(x(:,isprior)-repmat(mu0(2,isprior),[n,1])).^2 , 1)./...
         prior(2,isprior));
sigma0 = max(sigma0,minsigma);

[mu2,sigma2,prior2,score2] = main(mu0,sigma0,gamma,prior,w,x,maxiters,minchange,minsigma,n,m);  

inds2 = score2 > score1;
if any(inds2),
  mu(:,inds2) = mu2(:,inds2);
  sigma(:,inds2) = sigma2(:,inds2);
  prior(:,inds2) = prior2(:,inds2);
end;

noprior = prior(1,:) < eps;
mu(1,noprior) = mu(2,noprior);
sigma(1,noprior) = sigma(2,noprior);
noprior = prior(2,:) < eps;
mu(2,noprior) = mu(1,noprior);
sigma(2,noprior) = sigma(1,noprior);


function [mu,sigma,prior,score] = main(mu0,sigma0,gamma,prior,w,x,maxiters,minchange,minsigma,n,m)

ischange = true(1,m);

for iter = 1:maxiters,
  
  % compute probability for each
  p1 = normpdf( vectorize(x(:,ischange))', ...
                vectorize(repmat(mu0(1,ischange),[n,1]))', ...
                vectorize(repmat(sigma0(1,ischange),[n,1]))' ) ...
       .* vectorize(repmat(prior(1,ischange),[n,1]))';
  p2 = normpdf( vectorize(x(:,ischange))', ...
                vectorize(repmat(mu0(2,ischange),[n,1]))', ...
                vectorize(repmat(sigma0(2,ischange),[n,1]))' ) ...
       .* vectorize(repmat(prior(2,ischange),[n,1]))';
  tmp = p1 + p2;
  p1(tmp<eps) = .5;
  p2(tmp<eps) = .5;
  tmp(tmp<eps) = 1;
  gamma(:,ischange) = reshape(p1./tmp,[n,nnz(ischange)]);
  
  % update the mean, variance, and prior
  tmp = w(:,ischange).*gamma(:,ischange);
  prior(1,ischange) = sum(tmp,1);
  tmp = tmp(:,prior(1,ischange)>0);
  isprior = prior(1,:) > 0;
  mu(1,ischange&isprior) = sum(tmp.*x(:,ischange&isprior),1)./prior(1,ischange&isprior);
  sigma(1,ischange&isprior) = ...
      sqrt(sum( tmp.*(x(:,ischange&isprior)-...
                      repmat(mu(1,ischange&isprior),[n,1])).^2 , 1)./...
           prior(1,ischange&isprior));
  tmp = w(:,ischange).*(1-gamma(:,ischange));
  prior(2,ischange) = sum(tmp,1);
  tmp = tmp(:,prior(2,ischange)>0);
  isprior = prior(2,:) > 0;
  mu(2,ischange&isprior) = sum(tmp.*x(:,ischange&isprior),1)./prior(2,ischange&isprior);
  sigma(2,ischange&isprior) = ...
      sqrt(sum( tmp.*(x(:,ischange&isprior)-...
                      repmat(mu(2,ischange&isprior),[n,1])).^2 , 1)./...
           prior(2,ischange&isprior));
  sigma = max(sigma,minsigma);
  
  % see if there is a change
  ischange = any((abs(mu - mu0) >= minchange) | ...
                 (abs(sigma - sigma0) >= minchange),1);
  
  if ~any(ischange), break; end;
  
  mu0 = mu;
  sigma0 = sigma;
  
end;

p1 = normpdf( vectorize(x)', ...
              vectorize(repmat(mu(1,:),[n,1]))', ...
              vectorize(repmat(sigma(1,:),[n,1]))' ) ...
     .* vectorize(repmat(prior(1,:),[n,1]))';
p2 = normpdf( vectorize(x)', ...
              vectorize(repmat(mu(2,:),[n,1]))', ...
              vectorize(repmat(sigma(2,:),[n,1]))' ) ...
     .* vectorize(repmat(prior(2,:),[n,1]))';
p1 = reshape(p1,[n,m]);
p2 = reshape(p2,[n,m]);
score = sum(w .* (gamma.*p1 + (1-gamma).*p2),1);

