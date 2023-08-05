function n2 = angledist2(x, c)

x = x(:);
c = c(:)';
nx = rows(x);
nc = cols(c);

d = mod(repmat(x,[1,nc]) - repmat(c,[nx,1])+pi/2,pi) - pi/2;
n2 = d.^2;
