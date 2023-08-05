function [I,flastread] = read_fmf_chunk(filename,f,n,maxf)

nread = min(n,maxf-f+1);
I = fmf_read(filename,f,nread,1);
flastread = f + nread - 1;
