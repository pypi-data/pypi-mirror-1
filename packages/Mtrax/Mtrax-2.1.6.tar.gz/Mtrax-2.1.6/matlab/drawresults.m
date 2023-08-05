function drawresults(X,I,cm)

dodelete = all(isnan(X(1,:,:)),3);
X(:,dodelete,:) = [];

hold off;
image(repmat(I,[1,1,3])); axis image;
hold on;
K = cols(X);
if ~exist('cm','var'),
  cm = jet(K);
end;
for k = 1:K,
  if ~any(isnan(X(:,k,end))),
    h = ellipsedraw(X(3,k,end)/2,X(4,k,end)/2,X(1,k,end),X(2,k,end),X(5,k,end));
    set(h,'color',cm(k,:));
  end;
end;
for k = 1:K,
  plot(squeeze(X(1,k,1:end-1)),squeeze(X(2,k,1:end-1)),'-','color',cm(k,:));
end;