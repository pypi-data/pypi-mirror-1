function show_annotation(filename,X,f,foffset)

if nargin < 4,
  foffset = 0;
end;
if nargin < 3,
  f = max(1,1-foffset);;
end

[header_size,version,NR,NC,bytes_per_chunk,NFRAMES,data_format] = ...
  fmf_read_header(filename);  

UPARROW = 30;
DOWNARROW = 31;
ENTER = 13;
isdone = false;
a = [];
maxntargets = 0;
for i = 1:length(X),
  if cols(X{i}) > maxntargets, 
    maxntargets = cols(X{i});
  end;
end;
cm = jet(maxntargets);
cm = cm(randperm(maxntargets),:);

while 1,
  
  if isdone, break; end;
  
  I = fmf_read(filename,f,1,1);
  clf;
  drawresults(X{f+foffset},I,cm);  
  title(num2str(f));
  
  while 1,
    b = waitforbuttonpress;
    if b == 1,
      c = get(gcf,'currentcharacter');
      if c == ENTER,
        isdone = true;
        break;
      elseif c == UPARROW,
        f = min([f+1,NFRAMES,NFRAMES-foffset]);
        break;
      elseif c == DOWNARROW,
        f = max([f-1,1,1-foffset]);
        break;
      end;
    end;
  end;
  a = axis;
end;