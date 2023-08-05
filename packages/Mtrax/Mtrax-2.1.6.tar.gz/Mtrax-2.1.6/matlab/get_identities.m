function [fly_ids, id_lengths, movie_len] = get_identities( data )
% [fly_ids, id_lengths, movie_len] = get_identities( data )
%
% DATA is a raw matrix read from a file saved by Mtrax
% (something like "data = load( filename )").
%
% FLY_IDS is cell array in which each element is a structure,
% and each structure has vectors x_pos,y_pos,maj_ax,min_ax,angle
% corresponding to a single fly's trajectory for as long as
% it was tracked.
% ID_LENGTHS is a vector of how long each single-fly trajectory
% is, in frames.
% MOVIE_LEN is the length of the longest possible single-fly
% trajectory, useful for normalizing.
%
% JAB 4/25/07

n_ids = size( data.x_pos, 2 );
fly_ids = cell( 1, n_ids );
for ii = 1:n_ids
    fx = find( data.x_pos(:,ii) >= 0 );
    fy = find( data.y_pos(:,ii) >= 0 );
    if length( fx ) ~= length( fy ), error( 'some weird data' ); end
    
    fly_ids{ii}.x_pos = data.x_pos(fx,ii);
    fly_ids{ii}.y_pos = data.y_pos(fx,ii);
    fly_ids{ii}.maj_ax = data.maj_ax(fx,ii);
    fly_ids{ii}.min_ax = data.min_ax(fx,ii);
    fly_ids{ii}.angle = data.angle(fx,ii);
end

id_lengths = zeros( 1, length( fly_ids ) );
for i = 1:length( fly_ids )
    id_lengths(i) = length( fly_ids{i}.x_pos );
end

movie_len = size( data.x_pos, 1 );
