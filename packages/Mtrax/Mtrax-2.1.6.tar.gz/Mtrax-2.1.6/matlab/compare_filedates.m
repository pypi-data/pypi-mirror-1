function rtn = compare_filedates( file1, file2 )
% compare_filedates( file1, file2 )
%
% returns 1 if file1 was modified later than file2, else 0
%
% JAB 6/3/05

rtn = 0;
f1 = dir( file1 );
if isempty( f1 ), error( 'file %s does not exist', file1 ); end
f1_date = datevec( f1.date );
f2 = dir( file2 );
if isempty( f2 ), error( 'file %s does not exist', file2 ); end
f2_date = datevec( f2.date );
comp = f1_date - f2_date;
for i=comp
	if i < 0, break;
	elseif i > 0, rtn = 1; break;
	end
end
