function [isfore,dfore] = backsub(I)

global BACKI BACKTHRESH BACKHBF BACKTRUNC BACKRATIO;

if 1,
  him = im2double(I);
  him = BACKRATIO.*him;
  dfore = abs(him - BACKI) / BACKTHRESH;
  isfore = dfore > 1;
else,
  % compute fourier transform
  FFTlogIm = fft2(log(im2double(I)+.01));
  % apply high pass filter
  him = exp(real(ifft2(FFTlogIm.*BACKHBF)));
  % make sure it is in [0,1]
  him = max(min(him,1),0);
  % truncate
  him = him / BACKTRUNC;
  
  % compute error
  dfore = abs(him - BACKI) / BACKTHRESH;
  isfore = dfore > 1;
end;