# read RIFF then riffsize
RIFF, riff_size, AVI = struct.unpack( '4sI4s', file.read( 12 ) )



# read hdrl
LIST, hdrl_size, hdrl = \
    struct.unpack( '4sI4s', file.read( 12 ) )


# read avih 
avih, avih_size = struct.unpack( '4sI', file.read( 8 ) )

avihchunkstart = file.tell()

# read microsecperframe
microsecperframe, = struct.unpack('I',file.read(4))
framespersec = 1000000./float(microsecperframe)

# skip to nframes
file.seek(3*4,1)
nframes, = struct.unpack('I',file.read(4))

# skip to width
file.seek(3*4,1)
width,height = struct.unpack('2I',file.read(8))

# skip the rest of the aviheader
file.seek(avihchunkstart+avih_size,0)

LIST, stream_listsize, strl = \
    struct.unpack( '4sI4s', file.read( 12 ) )



strh, strh_size = struct.unpack( '4sI', file.read( 8 ) )


strhstart = file.tell()

# read stream type, fcc handler
vids, fcc = struct.unpack( '4s4s', file.read( 8 ) )
# check for vidstream

# check fcc


# skip the rest of the stream header
file.seek(strhstart+strh_size,0)

