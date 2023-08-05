function [x,y,theta] = read_annotation_file(filename)

fid = fopen(filename);
if fid < 0,
  error(['Could not open file ',filename]);
end;

x = {};
y = {};
theta = {};

% skip header
fgetl(fid);

for f = 1:inf
  
  l = fgetl(fid);
  if ~ischar(l), break; end;
  t = sscanf(l,'%f',inf);
  t = reshape(t,[3,length(t)/3]);
  x{f} = t(1,:);
  y{f} = t(2,:);
  theta{f} = t(3,:);
  
end;

fclose(fid);