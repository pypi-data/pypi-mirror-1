function quals = parameterize_mtrax( dirname )
% quals = parameterize_mtrax( dirname )
%
% Reads all tracking data from the directory DIRNAME and
% constructs identity-length histograms (using id_hist.m)
% to quantify the quality of the tracking data. Tracking
% parameters are read from the filenames, and tracking
% quality (QUALS) is plotted in terms of these parameters.
%
% JAB 4/25/07

savefile = 'mtrax_parms.mat';

%% read file list and parse filenames for parameters %%
if exist( savefile, 'file' ), read_flag = 0;
else,
    fprintf( 1, 'savefile not found... analyzing\n' )
    read_flag = 1;
end

dir_list = dir( dirname );
cutoffs = [];
boosts = [];
orders = [];
threshs = [];
filenames = cell( 1 );
files = 0;
for dd = 1:length( dir_list )
    if ~dir_list(dd).isdir & findstr( 'movie', dir_list(dd).name ) == 1 & ...
            findstr( '.fmf_', dir_list(dd).name ) > 0 & ...
            findstr( '.mat', dir_list(dd).name ) == length( dir_list(dd).name ) - length( '.mat' ) + 1
        files = files + 1; % found a legitimate mat-file
        filenames{files} = dir_list(dd).name;
        if exist( savefile, 'file' ) & compare_filedates( [dirname '/' dir_list(dd).name], savefile )
            read_flag = 1;
        end
        
        % parse through filename for parameters
        startc = findstr( '.fmf_', dir_list(dd).name ) + length( '.fmf_' );
        endc = findstr( '_', dir_list(dd).name(startc:end) ) + startc - 1;
        cutoff = str2num( dir_list(dd).name(startc:endc(1)-1) );
        cutoffs = [cutoffs cutoff];
        boost = str2num( dir_list(dd).name(endc(1)+1:endc(2)-1) );
        boosts = [boosts boost];
        order = str2num( dir_list(dd).name(endc(2)+1:endc(3)-1) );
        orders = [orders order];
        endt = findstr( '.mat', dir_list(dd).name(endc(3):end) ) + endc(3) - 1;
        thresh = str2num( dir_list(dd).name(endc(3)+1:endt(1)-1) );
        threshs = [threshs thresh];
        if length( orders ) ~= length( cutoffs ), keyboard
        elseif length( orders ) ~= length( boosts ), keyboard
        elseif length( orders ) ~= length( threshs ), keyboard; end
    end
end

%% make parameter quality matrix and fill %%
if read_flag
    bins = linspace( -4, 0, 100 );

    % these are the values corresponding to the indices along the 4 axes
    uc = unique( cutoffs );
    ub = unique( boosts );
    uo = unique( orders );
    ut = unique( threshs );
    quals = zeros( length( uc ), length( ub ), length( uo ), length( ut ) ) + bins(1);

    for ff = 1:length( filenames )
        fprintf( 1, 'working on %s\n', filenames{ff} )
        [ids, lengths, movie_len] = get_identities( load( [dirname '/' filenames{ff}] ) );
        if isempty( lengths ), continue; end

        % each trace should be represented proportionally to its length
        % therefore, we will add L additional values to LENGTHS for each trace
        % where L is the value of LENGTHS for that trace (the length of the trace itself)
        ln = length( lengths );
        for ll = 1:ln
           new_vals = ones( 1, lengths(ll) ) .* lengths(ll);
           lengths = [lengths new_vals];
        end % for each length value
        
        lengths = lengths ./ movie_len; % normalize by movie length

        if 0 % plot
            n = hist( log10( lengths ), bins );
            fn = find( n );
            if ~isempty( fn )
                figure(ff); clf; hold on
                bar( bins(fn), log10( n(fn) ) )
                title( filenames{ff} )
                xlabel( 'log_1_0 identity trace length (frames)' )
                ylabel( 'log_1_0 occurrences' )
                ax = axis;
                axis( [bins(1) bins(end) ax(3) ax(4)] )
            end
        end

        ic = find( uc == cutoffs(ff) );
        ib = find( ub == boosts(ff) );
        io = find( uo == orders(ff) );
        it = find( ut == threshs(ff) );
        quals(ic,ib,io,it) = median( log10( lengths ) );
    end % for each datafile

    save( savefile, 'filenames','cutoffs','boosts','orders','threshs','quals','uc','ub','uo','ut','bins' )
else
    fprintf( 1, 'loading data from disk\n' )
    load( savefile )
end
fprintf( 1, 'done grabbing\n' )

%% make plots of each pair of parameters... or something %%
if length( size( quals ) ) > 3
    % collapse threshold data
    quals_ct = log10( mean( 10.^quals, 4 ) );
else
    quals_ct = quals;
end

% collapse order data
quals_co = log10( mean( 10.^quals_ct, 3 ) );
figure(1001); clf; hold on
imshow( quals_co, [], 'initialmagnification', 'fit' )
axis on
set( gca, 'xtick', 1:length( ub ) )
set( gca, 'xticklabel', num2str( ub' ) )
xlabel( 'boost' )
set( gca, 'ytick', 1:length( uc ) )
set( gca, 'yticklabel', num2str( uc' ) )
ylabel( 'cutoff' )
colorbar

% collapse boost data
quals_cb = log10( mean( 10.^quals_ct, 2 ) );
quals_cb = reshape( quals_cb, size( quals, 1 ), size( quals, 3 ) );
figure( 1002 ); clf; hold on
imshow( quals_cb, [], 'initialmagnification', 'fit' )
axis on
set( gca, 'xtick', 1:length( uo ) )
set( gca, 'xticklabel', num2str( uo' ) )
xlabel( 'order' )
set( gca, 'ytick', 1:length( uc ) )
set( gca, 'yticklabel', num2str( uc' ) )
ylabel( 'cutoff' )
colorbar

% collapse cutoff data
quals_cc = log10( mean( 10.^quals_ct, 1 ) );
quals_cc = reshape( quals_cc, size( quals, 2 ), size( quals, 3 ) );
figure( 1003 ); clf; hold on
imshow( quals_cc, [], 'initialmagnification', 'fit' )
axis on
set( gca, 'xtick', 1:length( uo ) )
set( gca, 'xticklabel', num2str( uo' ) )
xlabel( 'order' )
set( gca, 'ytick', 1:length( ub ) )
set( gca, 'yticklabel', num2str( ub' ) )
ylabel( 'boost' )
colobar
