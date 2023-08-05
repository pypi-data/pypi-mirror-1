function show_annotation(filename,f,X)

if nargin < 2,
  f = 1;
end

[header_size,version,NR,NC,bytes_per_chunk,NFRAMES,data_format] = ...
  fmf_read_header(filename);  

[x,y,theta] = read_annotation_file([filename,'.ann']);

LINELENGTH = 15;
UPARROW = 30;
DOWNARROW = 31;
ENTER = 13;
isdone = false;
a = [];
maxntargets = 0;
for i = 1:length(x),
  if length(x{i}) > maxntargets, 
    maxntargets = length(x{i});
  end;
end;
cm = jet(maxntargets);
cm = cm(randperm(maxntargets),:);

while 1,
  
  if isdone, break; end;
  
  I = im2double(fmf_read(filename,f+3,1,1));
  clf;
  image(repmat(I,[1,1,3])); axis image; colormap gray;
  hold on;
  
  K = length(x{f});
  x0 = x{f} - LINELENGTH/2*cos(theta{f});
  y0 = y{f} - LINELENGTH/2*sin(theta{f});
  x1 = x{f} + LINELENGTH/2*cos(theta{f});
  y1 = y{f} + LINELENGTH/2*sin(theta{f});
  
  for k = 1:K,
%for k = [2,15],
    h(k) = line([x0(k),x1(k)]+1,[y0(k),y1(k)]+1);
    set(h(k),'color',cm(k,:));
    h(K+k) = plot(x{f}(k)+1,y{f}(k)+1,'.','color',cm(k,:));
  end;
  axis image;
  if ~isempty(a),
    axis(a);
  end;
  
  title(num2str(f));
  
  while 1,
    b = waitforbuttonpress;
    if b == 1,
      c = get(gcf,'currentcharacter');
      if c == ENTER,
        isdone = true;
        break;
      elseif c == UPARROW,
        f = min(f + 1,NFRAMES-2);
        break;
      elseif c == DOWNARROW,
        f = max(f - 1,1);
        break;
      end;
    end;
  end;
  a = axis;
end;