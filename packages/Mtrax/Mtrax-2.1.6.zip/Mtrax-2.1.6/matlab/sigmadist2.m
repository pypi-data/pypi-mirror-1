function D = sigmadist2(a,b,sigma)

[nd,na] = size(a);
[nd,nb] = size(b);
b = reshape(b,[nd,1,nb]);

d = (repmat(a,[1,1,nb]) - repmat(b,[1,na,1])) ./ repmat(sigma,[1,1,nb]);
D = reshape(sum(d.^2,1),[na,nb]);