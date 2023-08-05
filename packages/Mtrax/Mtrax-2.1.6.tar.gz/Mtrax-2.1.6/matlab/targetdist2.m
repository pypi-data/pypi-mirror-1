function D = targetdist2(Xpred, Xobs, Sigmapred)

Npred = cols(Xpred);
Nobs = cols(Xobs);
D = rows(Xpred);
Xobs = reshape(Xobs,[D,1,Nobs]);

% compute pairwise difference
d = repmat(Xpred,[1,1,Nobs]) - repmat(Xobs,[1,Npred,1]);

% make sure the angle difference is in [-pi/2,pi/2]
d(5,:) = mod(d(5,:)+pi/2,pi) - pi/2;

% use weights
d = d ./ repmat(Sigmapred,[1,1,Nobs]);

% compute total
D = sum(d.^2,1);
D = reshape(D,[Npred,Nobs]);

