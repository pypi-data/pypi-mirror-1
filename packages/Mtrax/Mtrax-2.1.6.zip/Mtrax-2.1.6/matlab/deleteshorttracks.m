if f > 1,
  % tracks that are around for <MINNFRAMES and haven't been deleted
  % yet must have started in the last MINNFRAMES-1 frames,
  % i.e. they were nan in some frame i-1 and are not nan in frame i
  if f <= MINNFRAMES,
    startedrecently = true(1,cols(XTRACK));
  else,
    startedrecently = ...
        any(isnan(XTRACK(1,:,min(NFRAMES,f-MINNFRAMES:f-2))) & ...
            ~isnan(XTRACK(1,:,min(NFRAMES,f-MINNFRAMES+1:f-1))),3);
  end;
  endednow = ~isnan(XTRACK(1,:,f-1)) & isnan(XTRACK(1,:,f));
  dodelete = startedrecently & endednow;
  XTRACK(:,dodelete,:) = [];
end;