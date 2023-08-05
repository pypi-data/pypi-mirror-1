function [X3,Sigmapred] = cvpred(X1,X2)

global DAMPEN;
global SIGMAMOTION;
global MODPI;

N1 = cols(X1);
N2 = cols(X2);
N = min(N1,N2);

X3 = X2;

% x and y position, major, minor axis lengths for 
X3(1:4,1:N) = X2(1:4,1:N) + repmat(DAMPEN(1:4),[1,N]).*...
  (X2(1:4,1:N) - X1(1:4,1:N));

% put angle for X1 in same frame as angle for X2
if MODPI == 1,
  dtheta = mod( X2(5,1:N) - X1(5,1:N) + pi/2, pi) - pi/2;
else,
  dtheta = mod( X2(5,1:N) - X1(5,1:N) + pi, 2*pi) - pi;
end;
X3(5,1:N) = X2(5,1:N) + DAMPEN(5)*dtheta;
X3(5,1:N) = mod( X3(5,1:N) + pi , 2*pi) - pi;

% deal with NaNs 
dofix = any(isnan(X1),1) & ~any(isnan(X2),1);
X3(:,dofix) = X2(:,dofix);

Sigmapred = repmat(SIGMAMOTION,[1,N2]);
