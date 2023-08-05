load results0.mat;
ORIENTATION = 5;

for f = 2:NFRAMES,

  theta0 = XTRACK(ORIENTATION,:,f-1);
  % put theta1 within pi/2 of theta0
  theta1 = XTRACK(ORIENTATION,:,f);
  dtheta = mod(theta1-theta0+pi/2,pi)-pi/2;
  theta1 = theta0 + dtheta;
  % put theta1 between -pi and pi
  theta1 = mod(theta1+pi,2*pi)-pi;
  XTRACK(ORIENTATION,:,f) = theta1;

end;

