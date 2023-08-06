# movies.py
# JAB 5/10/07

import chunk
import numpy as num
import struct
#import threading
import wx
import os
from params import params
from draw import annotate_bmp

import FlyMovieFormat as fmf # kmb's version of FlyMovieFormat
try:
    from FlyMovieFormat import NoMoreFramesException
except ImportError:
    class NoMoreFramesException (Exception): pass

#import imops # part of Motmot

class Movie:
    """Generic interface for all supported movie types.
    Also makes reading movies thread-safe."""
    def __init__( self, filename, interactive ):
        """Figure out file type and initialize reader."""
        self.interactive = interactive

        #self.lock = threading.Lock()

        # read FlyMovieFormat
        (tmp,ext) = os.path.splitext(filename)
        if ext == '.fmf':
            self.type = 'fmf'
            try:
                self.h_mov = fmf.FlyMovie( filename )
            except NameError:
                if self.interactive:
                    wx.MessageBox( "Couldn't open \"%s\"\n(maybe FMF is not installed?)"%(filename), "Error", wx.ICON_ERROR )
                raise
            except IOError:
                if self.interactive:
                    wx.MessageBox( "I/O error opening \"%s\""%(filename), "Error", wx.ICON_ERROR )
                raise
        elif ext == '.sbfmf':
            self.type = 'sbfmf'
            try:
                self.h_mov = fmf.FlyMovie(filename)
            except NameError:
                if self.interactive:                                    
                    wx.MessageBox( "Couldn't open \"%s\"\n(maybe FMF is not installed?)"%(filename), "Error", wx.ICON_ERROR )
                raise
            except IOError:
                if self.interactive:
                    wx.MessageBox( "I/O error opening \"%s\""%(filename), "Error", wx.ICON_ERROR )
                raise
        # read AVI
        elif ext == '.avi':
            self.type = 'avi'
            try:
                self.h_mov = Avi( filename )
            except (TypeError, ValueError, AssertionError):
                if self.interactive:
                    wx.MessageBox( "Failed opening file \"%s\".\nMake sure file is uncompressed 8-bit grayscale."%(filename), "Error", wx.ICON_ERROR )
                raise

        # unknown movie type
        else:
            if self.interactive:
                wx.MessageBox( "Unknown file type %s"%(filename[-4:]), "Error", wx.ICON_ERROR )
            raise TypeError( "unknown file type %s"%(filename[-4:]) )


    def get_frame( self, framenumber ):
        """Return numpy array containing frame data."""
        #self.lock.acquire()
        try:
            try: frame, stamp = self.h_mov.get_frame( framenumber )
            except (IndexError, NoMoreFramesException):
                if self.interactive:
                    wx.MessageBox( "Frame number %d out of range"%(framenumber), "Error", wx.ICON_ERROR )
                raise
            except (ValueError, AssertionError):
                if self.interactive:
                    wx.MessageBox( "Error reading frame %d"%(framenumber), "Error", wx.ICON_ERROR )
                raise
            else:
                return frame, stamp
        finally:
            pass
            #self.lock.release()
            
    def get_n_frames( self ): return self.h_mov.get_n_frames()
    def get_width( self ): return self.h_mov.get_width()
    def get_height( self ): return self.h_mov.get_height()

class Avi:
    """Read uncompressed AVI movies."""
    def __init__( self, filename ):
        self.file = open( filename, 'r' )
        self.read_header()

    def __del__( self ):
        """Existence possibly unnecessary, if Python does this cleanup for us."""
        if hasattr( self, 'file' ):
            self.file.close()

    def read_header( self ):
        # RIFF header
        file_type, riff_size = struct.unpack( '4sI', self.file.read( 8 ) )
        assert file_type == 'RIFF'
        stream_type = self.file.read( 4 )
        assert stream_type == 'AVI '
        header_list, header_listsize, header_listtype = \
                     struct.unpack( '4sI4s', self.file.read( 12 ) )
        assert header_list == 'LIST' and header_listtype == 'hdrl'
        #size 4588 (fmf 1222)
        avi_str, avi_note = struct.unpack( '4sI', self.file.read( 8 ) )
        assert avi_str == 'avih'

        # AVI header
        avi_header = self.file.read( 56 )
        self.frame_delay_us, \
                          AVI_data_rate, \
                          padding_size, \
                          AVI_flags, \
                          self.n_frames, \
                          n_preview_streams, \
                          n_data_streams, \
                          avi_buf_size, \
                          self.width, \
                          self.height, \
                          self.time_scale, \
                          self.data_rate, \
                          self.start_time, \
                          self.AVI_chunk_size \
                          = struct.unpack( '14I', avi_header )
        #10000 100000000 0 16 100 0 1 1310720 1280 1024 100 10000 0 99
        if n_data_streams != 1:
            raise TypeError( "file must contain only one data stream" )
        if avi_buf_size != 0: self.buf_size = avi_buf_size

        # stream header
        stream_list, stream_listsize, stream_listtype = \
                     struct.unpack( '4sI4s', self.file.read( 12 ) )
        assert stream_list == 'LIST' and stream_listtype == 'strl'
        #size 4244 (fmf 1146)
        stream_str, stream_note = struct.unpack( '4sI', self.file.read( 8 ) )
        assert stream_str == 'strh'
        
        stream_header = self.file.read( 56 )
        fccType, \
                 fccHandler, \
                 stream_flags, \
                 priority, \
                 frames_interleave, \
                 stream_scale, \
                 stream_rate, \
                 stream_start, \
                 stream_length, \
                 stream_buf_size, \
                 stream_quality, \
                 stream_sample_size, \
                 x,y,w,h \
                 = struct.unpack( '4s4s10I4H', stream_header )
        #vids DIB  0 0 0 100 10000 0 99 1310720 100 0 0 0 1280 1024
        #vids DIB  0 0 0 1 50 0 301 235200 0 0 0 0 560 420
        if fccType != 'vids':
            raise TypeError( "stream type must be video" )
        if fccHandler != 'DIB ':
            raise TypeError( "video must be uncompressed" )
        if stream_buf_size != 0:
            if hasattr( self, 'buf_size' ):
                assert self.buf_size == stream_buf_size
            else:
                self.buf_size = stream_buf_size

        # bitmap header
        bmp_str, bmp_note = struct.unpack( '4sI', self.file.read( 8 ) )
        assert bmp_str == 'strf'

        bmp_header = self.file.read( 40 )
        self.bmp_size, \
                       bmp_width, \
                       bmp_height, \
                       bmp_planes, \
                       bmp_bitcount, \
                       crap, \
                       bmp_buf_size, \
                       xpels_per_meter, \
                       ypels_per_meter, \
                       color_used, \
                       color_important \
                       = struct.unpack( 'I2i2H6i', bmp_header )
        #40 1280 1024 1 8 0 1310720 0 0 256 0
        assert bmp_width == self.width and bmp_height == self.height
        if bmp_buf_size != 0:
            if hasattr( self, 'buf_size' ):
                assert self.buf_size == bmp_buf_size
            else:
                self.buf_size == stream_buf_size
        if not hasattr( self, 'buf_size' ):
            # just a guess -- should be OK if 8-bit grayscale
            self.buf_size = self.height * self.width

        # skip extra header crap
        movie_list = ''
        movie_listtype = ''
        while movie_list != 'LIST':
            s = ''
            EOF_flag = False
            while s.find( 'movi' ) < 0 and not EOF_flag:
                p = self.file.tell()
                s = self.file.read( 128 )
                if s == '': EOF_flag = True
            if EOF_flag: break
            self.file.seek( p )
            self.file.read( s.find( 'movi' ) - 8 )
            movie_list, movie_listsize, movie_listtype = \
                        struct.unpack( '4sI4s', self.file.read( 12 ) )
        assert movie_list == 'LIST' and movie_listtype == 'movi'

        # beginning of data blocks
        self.data_start = self.file.tell()

    def get_frame( self, framenumber ):
        """Read frame from file and return as NumPy array."""
        if framenumber < 0: raise IndexError
        if framenumber >= self.n_frames: raise NoMoreFramesException
        
        # read frame from file
        self.file.seek( self.data_start + (self.buf_size+8)*framenumber )
        this_frame_id, frame_size = struct.unpack( '4sI', self.file.read( 8 ) )
        if frame_size != self.buf_size:
            raise ValueError( "movie must be uncompressed" )
        if not hasattr( self, 'frame_id' ):
            self.frame_id = this_frame_id
        elif this_frame_id != self.frame_id:
            raise ValueError( "error seeking frame start: unknown data header" )
        frame_data = self.file.read( frame_size )

        # make frame into numpy array
        frame = num.fromstring( frame_data, num.uint8 )
        if frame.size == self.width*self.height:
            frame.resize( (self.height, self.width) )
        elif frame.size == self.width*self.height*3:
            #frame.resize( (self.height, self.width, 3) )
            #frame = imops.to_mono8( 'RGB8', frame )
            raise TypeError( "movie must be grayscale" )
        else:
            raise ValueError( "frame size %d doesn't make sense: movie must be 8-bit grayscale"%(frame.size) )

        # make up a timestamp based on the file's stated framerate
        if self.frame_delay_us != 0:
            stamp = framenumber * self.frame_delay_us / 1e6
        elif self.time_scale != 0:
            stamp = framenumber * self.data_rate / float(self.time_scale)
        else:
            stamp = framenumber / 24
            # should raise warning or error here?
            # this might screw up playback, at least

        return frame, stamp
    
    def get_n_frames( self ): return self.n_frames
    def get_width( self ): return self.width    
    def get_height( self ): return self.height

def write_results_to_avi(movie,tracks,filename,f0=None,f1=None):

    nframes = len(tracks)
    if f0 is None:
        f0 = params.start_frame
    if f1 is None:
        f1 = nframes + params.start_frame - 1

    f0 -= params.start_frame
    f1 -= params.start_frame
    f0 = max(0,min(nframes-1,f0))
    f1 = max(0,min(nframes-1,f1))
    nframes_write = f1-f0+1

    # open the file for output
    outstream = open(filename,'wb')
    
    # write the header
    write_avi_header(movie,tracks,filename,outstream,f0,f1)

    # get the current location
    movilistloc = outstream.tell()

    # write the frames
    offsets = num.zeros(nframes_write)
    for i in range(f0,f1+1):
        if (i % 100) == 0:
            print 'Frame %d / %d'%(i,nframes_write)
        
        offsets[i-f0] = write_avi_frame(movie,tracks,i,outstream)

    # get offset relative to movilist
    offsets -= movilistloc + 4

    # write the index
    write_avi_index(movie,tracks,offsets,outstream,f0,f1)

    # close
    outstream.close()

def write_avi_index(movie,tracks,offsets,outstream,f0,f1):

    nframes = f1-f0+1
    idx1size = 8 + 16*nframes
    BYTESPERPIXEL = 3
    bytesperframe = movie.get_width()*movie.get_height()*BYTESPERPIXEL

    write_chunk_header('idx1',idx1size,outstream)

    for i in range(len(offsets)):
        outstream.write(struct.pack('4s','00db'))
        outstream.write(struct.pack('I',16))
        outstream.write(struct.pack('I',offsets[i]))
        outstream.write(struct.pack('I',bytesperframe))

def write_avi_frame(movie,tracks,i,outstream):

    height = movie.get_height()
    width = movie.get_width()
    BYTESPERPIXEL = 3
    bytesperframe = width*height*BYTESPERPIXEL

    if tracks is None:
        return
    if i >= len(tracks):
        return

    # global frame index
    j = params.start_frame + i

    # read in the video frame
    try:
        frame, last_timestamp = movie.get_frame(j)
    except (IndexError,NoMoreFramesException):
        return

    # get the current tracks
    ellipses = tracks[i]

    # get tails
    old_pts = []
    early_frame = int(max(0,i-params.tail_length))
    for dataframe in tracks[early_frame:i+1]:
        these_pts = []
        for ellipse in dataframe.itervalues():
            these_pts.append( (ellipse.center.x,ellipse.center.y,
                               ellipse.identity) )
        old_pts.append(these_pts)

    # draw on image
    bitmap,resize,img_size = annotate_bmp(frame,ellipses,old_pts,
                                            params.ellipse_thickness,
                                            [height,width])
    img = bitmap.ConvertToImage()
    # the image is flipped
    img = img.Mirror(True)
    img = img.GetData()

    # write chunktype
    outstream.write(struct.pack('4s','00db'))
    # write size of frame
    outstream.write(struct.pack('I',bytesperframe))

    # write frame
    offset = outstream.tell()
    outstream.write(img[::-1])
    pad = bytesperframe%2
    if pad == 1:
        outstream.write(struct.pack('B',0))
    return offset

def write_avi_header(movie,tracks,filename,outstream,f0,f1):

    # movie size
    BYTESPERPIXEL = 3
    nframes = f1-f0+1
    width = movie.get_width()
    height = movie.get_height()
    bytesperframe = width*height*BYTESPERPIXEL

    # chunk sizes if 0 frames
    avihsize = 64
    #strnsize = 8 + len(filename) + 1
    strllistsize = 116
    strhsize = 56
    strfsize = 48
    hdrllistsize = avihsize + strllistsize + 12
    movilistsize = 12
    idx1size = 8
    riffsize = hdrllistsize + movilistsize + idx1size
    # add in frames
    movilistsize += nframes * (4+4+bytesperframe+(bytesperframe%2))
    idx1size += nframes * (4*4)
    riffsize +=  nframes * (4+4+bytesperframe + 4*4 + (bytesperframe%2))
    ## add in strnsize
    #addon = strnsize + (strnsize%2)
    #riffsize += addon
    #hdrllistsize += addon
    #strllistsize += addon

    # write the RIFF chunk header
    write_chunk_header('RIFF',riffsize,outstream)
    # write AVI fourcc
    outstream.write(struct.pack('4s','AVI '))
    # write hdrl LIST
    write_list_header('hdrl',hdrllistsize-8,outstream)
    # write avih chunk
    write_chunk_header('avih',avihsize-8,outstream)

    ## write main avi header
    # microseconds per frame
    if hasattr(movie,'frame_delay_us'):
        microsecperframe = movie.frame_delay_us
    else:
        microsecperframe = estimate_frame_delay_us(movie.h_mov)
    outstream.write(struct.pack('I',int(round(microsecperframe))))
    # maximum bytes per second
    framespersec = 1e6/microsecperframe
    bytespersec = framespersec*bytesperframe
    outstream.write(struct.pack('I',int(num.ceil(bytespersec))))
    # reserved
    outstream.write(struct.pack('I',0))    
    # flags
    outstream.write(struct.pack('I',16))
    # number of frames
    outstream.write(struct.pack('I',nframes))
    # initial frame
    outstream.write(struct.pack('I',0))
    # number of streams
    outstream.write(struct.pack('I',1))
    # suggested buffer size
    outstream.write(struct.pack('I',bytesperframe))
    # width
    outstream.write(struct.pack('I',width))
    # height
    outstream.write(struct.pack('I',height))
    # frame rate
    outstream.write(struct.pack('2I',100,100*framespersec))
    # not sure -- start, length
    outstream.write(struct.pack('2I',0,0))

    # strl list
    write_list_header('strl',strllistsize-8,outstream)
    # strh chunk
    write_chunk_header('strh',strhsize-8,outstream)

    ## write stream header
    # FCC type
    outstream.write(struct.pack('4s','vids'))
    # FCC handler -- 'DIBS '
    outstream.write(struct.pack('I',0))
    # Flags
    outstream.write(struct.pack('I',0))
    # Reserved
    outstream.write(struct.pack('I',0))
    # Initial Frame
    outstream.write(struct.pack('I',0))
    # Frame rate
    outstream.write(struct.pack('2I',100,100*framespersec))
    # not sure -- start, length
    outstream.write(struct.pack('2I',0,0))
    # suggested buffer size
    outstream.write(struct.pack('I',bytesperframe))
    # quality
    outstream.write(struct.pack('I',7500))
    # not sure -- sample size
    outstream.write(struct.pack('I',0))

    # Write strf chunk
    write_chunk_header('strf',strfsize-8,outstream)

    ## Write bitmap header
    # Size
    outstream.write(struct.pack('I',40))
    # width
    outstream.write(struct.pack('I',width))
    # height
    outstream.write(struct.pack('I',height))
    # planes
    outstream.write(struct.pack('H',1))
    # bits per pixel
    outstream.write(struct.pack('H',24))
    # FourCC: DIBS
    outstream.write(struct.pack('I',0))
    # image size
    outstream.write(struct.pack('I',bytesperframe))
    # not sure
    outstream.write(struct.pack('4I',0,0,0,0))

    ## Write stream name chunk and data
    #write_chunk_header('strn',strnsize-8,outstream)
    #outstream.write(filename)
    #outstream.write(struct.pack('B',0))
    #if (len(filename)%2) == 1:
    #    outstream.write(struct.pack('B',0))

    # movi list
    write_list_header('movi',movilistsize,outstream)
    
def write_chunk_header(chunktype,chunksize,outstream):

    outstream.write(struct.pack('4sI',chunktype,chunksize))

def write_list_header(listtype,listsize,outstream):

    outstream.write(struct.pack('4sI4s','LIST',listsize,listtype))

def estimate_frame_delay_us(mov):

    if not hasattr(mov,'chunk_start'):
        return 0

    # go to beginning of first frame
    if mov.issbfmf:
        return .05*1e6
    else:
        mov.file.seek(mov.chunk_start)
        # read the first timestamp
        stamp0 = mov.get_next_timestamp()
        # go to the last frame
        mov.file.seek(mov.chunk_start+mov.bytes_per_chunk*(mov.n_frames-1))
        # read the last timestamp
        stamp1 = mov.get_next_timestamp()

    
        frame_delay_us = float(stamp1-stamp0)/float(mov.n_frames-1)*1e6
        return frame_delay_us
    
