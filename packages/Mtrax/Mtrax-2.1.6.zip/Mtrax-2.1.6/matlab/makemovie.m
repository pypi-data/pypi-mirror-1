%aviobj = avifile('results0.avi');
%close all;
%figure(1);
%set(1,'visible','off');
%flastread = 0;
for f = 2:NFRAMES,
  if f > flastread | f < ffirstread,
    fprintf('f = %d\n',f);
    ffirstread = f;
    [I,flastread] = read_fmf_chunk(FILENAME,f,NFRAMESPERCHUNK,NFRAMES);
  end;
  drawresults(XTRACK(:,:,max(1,f-100):f),I(:,:,f-ffirstread+1));
  axis off;
  aviobj = addframe(aviobj,1);
end;
aviobj = close(aviobj);