#!/usr/bin/env python
# mtrax.py
# KMB 09/07/07

import os
import sys
import time
import wx
from wx import xrc
import numpy as num

from version import __version__, DEBUG
import annfiles as annot
import batch
import bg
import algorithm
import draw
import imagesk
import movies
import ellipsesk as ell

from params import params

try:
#    from wx import AboutDialogInfo
#    from wx import AboutBox
    raise ImportError # because the built-in versions have not been tested
except ImportError:
    # forward compatibility for AboutDialogInfo and AboutBox, added in wx 2.7.1.1
    # (currently 2.6.3.2 is packaged for Ubuntu Feisty)
    class AboutDialogInfo:
        def __init__( self ):
            self.name=self.description=self.version=self.copyright=""
        def SetName( self, name ): self.name = name
        def SetDescription( self, desc ): self.description = desc
        def SetVersion( self, version ): self.version = version
        def SetCopyright( self, cprt ): self.copyright = cprt
    def AboutBox( info ):
        wx.MessageBox( u"%s version %s\n\n%s\n\ncopyright \u00A9%s"%(info.name, info.version, info.description, info.copyright), "About %s"%info.name, wx.ICON_INFORMATION )

class GUIConstants:
    def __init__( self ):
        self.info = AboutDialogInfo()
        self.info.SetName( "Mtrax" )
        self.info.SetVersion( __version__ )
        self.info.SetCopyright( "2007, Caltech ethomics project" )
        self.info.SetDescription( """Multiple fly tracker.

http://www.dickinson.caltech.edu/Research/Mtrax

Distributed under the GNU General Public License
(http://www.gnu.org/licenses/gpl.html) with
ABSOLUTELY NO WARRANTY.

This project is supported by grant R01 DA022777-01 from
the National Institute on Drug Abuse at the US NIH.""" )
        
        self.TRACK_START = "Start Tracking"
        self.TRACK_STOP = "Stop Tracking"
        self.TRACK_PLAY = "Start Playback"
        self.TRACK_PAUSE = "Stop Playback"

        params.version = __version__
# rather than global variables for each of these...
const = GUIConstants()
    
class MtraxApp( algorithm.MtraxAlgorithm ): # eventually inherits from wx.App
    def OnInit( self ):

        known_args = ["-ni"] # special arguments, exclusive of sending movie name via command line
        
        self.InitGUI() # in mtrax_settings

        # non-interactive mode? default True, set in InitGUI()
        if "-ni" in sys.argv:
            self.interactive = False
        
        # draw GUI
        self.frame.Show()
        self.alive = True

        # open movie from command line
        self.filename = None
        self.ann_filename = None
        self.ann_file = None
        self.batch_executing = False
        try:
            if sys.argv[1] in known_args: raise RuntimeError
            self.filename = sys.argv[1]
            try:
                self.dir, self.file = self.filename.rsplit( '/', 1 ) # Linux only
            except ValueError:
                self.file = self.filename
            
            if len(sys.argv) > 2 and sys.argv[2] not in known_args:
                self.start_frame = int(sys.argv[2])
                self.slider.SetThumbPosition( self.start_frame )
            else: self.start_frame = 0
            
            self.OpenMovie()
            if self.start_frame > self.n_frames: self.start_frame = self.n_frames-1
            self.UpdateStatusMovie()

        except IndexError: # no movie filename sent from command line
            self.OnOpen( None )
        except RuntimeError: # first argument was a known argument
            self.n_frames = 0

        # initialize state values
        self.tracking = False
        self.batch = None
        self.batch_data = None
        self.bg_window_open = False

        self.OnResize( None )
        if len(sys.argv) == 2:
            self.framenumber_text.SetValue( "Frame: %05d"%(self.n_frames) )

        return True
        
    def CheckAnnotation( self ):
        """Test if annotation file exists for current movie. Set self.ann_file.
        Read annotation data if user desires."""
        try:
            # read file
            self.ann_file = annot.AnnotationFile( self.ann_filename, __version__ )
        except:
            self.ann_file = None
            self.ann_data = None
            return False

        #try:
        if self.interactive and not self.batch_executing and \
               wx.MessageBox( "Read old annotation data?\n(This may take awhile)", "Read?", wx.YES_NO ) == wx.YES:
            self.ReadAnnotationData()
            # enable controls
            self.menu.Enable( xrc.XRCID("menu_playback_show_ann"), True )
            self.menu.Enable( xrc.XRCID("menu_file_export"), True )
            self.menu.Enable( xrc.XRCID("menu_file_save_avi"), True )
            self.menu.Enable( xrc.XRCID("menu_choose_orientations"), True )        
            return True
        #except: pass
            
        self.ann_data = None
            
        # disable controls
        self.menu.Check( xrc.XRCID("menu_playback_show_ann"), False )
        self.menu.Enable( xrc.XRCID("menu_playback_show_ann"), False )
        self.menu.Enable( xrc.XRCID("menu_file_export"), False )
        self.menu.Enable( xrc.XRCID("menu_file_save_avi"), False )
        self.menu.Enable( xrc.XRCID("menu_choose_orientations"), False )
        return False

    def ReadAnnotationData( self ):
        """Read all annotation data from current ann_file."""
        start_color = self.status.GetBackgroundColour()
        self.status.SetBackgroundColour( params.status_blue )
        self.status.SetStatusText( "reading annotation data from file",
                                   params.status_box )
        wx.BeginBusyCursor()
        wx.Yield()

        # this block should be replaced by the try statement below
        self.ann_data = self.ann_file.GetAnnotation( self.interactive, self.bg_imgs )
        self.status.SetBackgroundColour( start_color )
        self.status.SetStatusText( "", params.status_box )
        wx.EndBusyCursor()
        wx.Yield()
        # end block
        
        #try:
        #    self.ann_data = self.ann_file.GetAnnotation( self.interactive )
        #finally:
        #    self.status.SetBackgroundColour( start_color )
        #    self.status.SetStatusText( "", params.status_box )
        #    wx.EndBusyCursor()
        #    wx.Yield()

    def LoadSettings( self ):
        try:
            tmpannfile = annot.AnnotationFile(self.settingsfilename,__version__,False)
        except:
            print 'error reading annotation file'
            return        
        tmpannfile.file = open( tmpannfile.filename, mode="rb" )
        tmpannfile.ReadSettings()
        tmpannfile.file.close()

    def OpenMovie( self ):
        """Attempt to open a movie given the current filename."""
        try:
            # open movie file
            self.movie = movies.Movie( self.filename, self.interactive )
        except:
            # error messages should be handled by the movie object
            self.movie = None
            self.start_frame = 0
            self.filename = ""
            self.n_frames = 0
            self.menu.Enable( xrc.XRCID("menu_track_start"), False )
            self.menu.Enable( xrc.XRCID("menu_track_resume"), False )
            self.menu.Enable( xrc.XRCID("menu_load_settings"), False )
            self.menu.Enable( xrc.XRCID("menu_track_play"), False )
            self.menu.Enable( xrc.XRCID("menu_settings_bg"), False )
            self.menu.Enable( xrc.XRCID("menu_settings_bg_model"), False )
            self.menu.Enable( xrc.XRCID("menu_settings_tracking"), False )
            self.menu.Enable( xrc.XRCID("menu_compute_background"), False )
            self.menu.Enable( xrc.XRCID("menu_compute_shape"), False )
            self.slider.Enable( False )
        else:
            self.movie.filename = self.filename
            params.movie_name = self.filename
            self.n_frames = self.movie.get_n_frames()
            # setup background-subtraction pieces
            self.bg_imgs = bg.BackgroundCalculator( self.movie )

            # enable commands
            self.menu.Enable( xrc.XRCID("menu_load_settings"), True )
            self.menu.Enable( xrc.XRCID("menu_track_start"), True )
            self.menu.Enable( xrc.XRCID("menu_track_play"), True )
            self.menu.Enable( xrc.XRCID("menu_settings_bg"), True )
            self.menu.Enable( xrc.XRCID("menu_settings_bg_model"), True )
            self.menu.Enable( xrc.XRCID("menu_settings_tracking"), True )
            self.menu.Enable( xrc.XRCID("menu_compute_background"), True )
            self.menu.Enable( xrc.XRCID("menu_compute_shape"), True )
            self.slider.Enable( True )

            # attempt to open annotation file
            #self.ann_filename = self.filename + '.ann'
            if self.CheckAnnotation():
                self.menu.Check( xrc.XRCID("menu_playback_show_ann"), True )
                if (self.ann_data is not None) and (len(self.ann_data) > 0):
                    self.menu.Enable(xrc.XRCID("menu_track_resume"), True )
        
            self.ShowCurrentFrame()

        self.slider.SetThumbPosition( self.start_frame )
        self.slider.SetScrollbar( self.start_frame,1,self.n_frames-1,100 )
        self.framenumber_text.SetValue( "Frame: %05d"%(self.n_frames) )

    def OnOpen( self, evt ):
        """Movie file selection dialog."""
        dlg = wx.FileDialog( self.frame, "Open movie", self.dir, "", "FlyMovieFormat files (*.fmf)|*.fmf|audio-video interleave files (*.avi)|*.avi", wx.OPEN )

        didchoose = dlg.ShowModal() == wx.ID_OK
        
        if didchoose:
            if self.menu.GetLabel( xrc.XRCID("menu_track_start") ) == const.TRACK_STOP:
                self.OnStopTracking( None ) # quit in mid-operation
            self.play_break = True # stop playback, if in progress
            self.file = dlg.GetFilename()
            self.dir = dlg.GetDirectory()
            self.filename = os.path.join( self.dir, self.file )
            self.start_frame = 0

        dlg.Destroy()

        if didchoose:

            # choose an annotation file
            defaultDir = self.dir
            defaultFile = self.filename + '.ann'
            dlg = wx.FileDialog( self.frame, "Annotation File", defaultDir, defaultFile, "Annotation files (*.ann)|*.ann", wx.OPEN )

            if dlg.ShowModal() == wx.ID_OK:
                ann_file = dlg.GetFilename()
                ann_dir = dlg.GetDirectory()
            else:
                ann_file = defaultFile
                ann_dir = defaultDir
            self.ann_filename = os.path.join( ann_dir, ann_file )

            # open movie
            self.OpenMovie()
            # show movie name in status bar
            self.UpdateStatusMovie()

    def OnLoadSettings( self, evt ):
        defaultDir = self.dir
        defaultFile = self.filename + '.ann'
        dlg = wx.FileDialog( self.frame, "Load Settings from File", defaultDir, defaultFile, "Annotation files (*.ann)|*.ann", wx.OPEN )
        
        if dlg.ShowModal() == wx.ID_OK:
            if self.menu.GetLabel( xrc.XRCID("menu_track_start") ) == const.TRACK_STOP:
                self.OnStopTracking( None ) # quit in mid-operation
            self.play_break = True # stop playback, if in progress
            self.settingsfile = dlg.GetFilename()
            self.settingsdir = dlg.GetDirectory()
            self.settingsfilename = os.path.join( self.settingsdir, self.settingsfile )
            self.start_frame = 0
            self.LoadSettings()

        dlg.Destroy()


    def UpdateStatusMovie( self ):
        """Update status bar with movie filename."""
        try:
            if len(self.filename) == 0:
                self.status.SetStatusText( "[no file loaded]",
                                           params.file_box )
            elif len(self.filename) < params.file_box_max_width:
                self.status.SetStatusText( self.filename, params.file_box )
            else:
                self.status.SetStatusText( ".../"+self.file,
                                           params.file_box ) # Linux only
        except (TypeError, AttributeError): pass
            
    def OnSave( self, evt ):
        """Choose filename to save annotation data as MAT-file."""
        if self.ann_data is None:
            if self.interactive:
                wx.MessageBox( "No valid annotation\nexists for this movie\nor no movie is loaded.",
                               "Error", wx.ICON_ERROR )
            else:
                print "not saving -- no data"
            return

        defaultDir = self.save_dir
        i = max(self.file.rfind('.fmf'),self.file.rfind('.avi'))
        defaultFile = self.file[:i] + '.mat'
        dlg = wx.FileDialog( self.frame, "Save as MAT-file", defaultDir, defaultFile, "*.mat", wx.SAVE )

        if dlg.ShowModal() == wx.ID_OK:
            this_file = dlg.GetFilename()
            self.save_dir = dlg.GetDirectory()
            filename = os.path.join( self.save_dir, this_file )
            
            start_color = self.status.GetBackgroundColour()
            self.status.SetBackgroundColour( params.status_blue )
            self.status.SetStatusText( "writing annotation data to file",
                                       params.status_box )
            wx.BeginBusyCursor()
            wx.Yield()

            self.ann_file.WriteMAT( filename, self.ann_data )

            self.status.SetBackgroundColour( start_color )
            self.status.SetStatusText( "", params.status_box )
            wx.EndBusyCursor()
            wx.Yield()

        dlg.Destroy()

    def OnSaveAvi( self, evt ):
        """Choose filename to save tracks as AVI-file."""
        if self.ann_data is None:
            if self.interactive:
                wx.MessageBox( "No valid annotation\nexists for this movie\nor no movie is loaded.",
                               "Error", wx.ICON_ERROR )
            else:
                print "not saving -- no data"
            return

        dlg = wx.TextEntryDialog(self.frame,"Frames to output to AVI file: (startframe:endframe): ","Save as AVI-file","%d:%d"%(params.start_frame,params.start_frame+len(self.ann_data)-1))
        isgood = False
        while isgood == False:
            if dlg.ShowModal() == wx.ID_OK:
                isgood = True
                s = dlg.GetValue()
                s = s.rsplit(':')
            else:
                break
            if len(s) == 2:
                if s[0].isdigit() and s[1].isdigit():
                    framestart = int(s[0])
                    frameend = int(s[1])
                else:
                    isgood = False
                    continue
            else:
                isgood = False
                continue

        dlg.Destroy()

        if isgood == False:
            return

        defaultDir = self.save_dir
        i = max(self.file.rfind('.fmf'),self.file.rfind('.avi'))
        defaultFile = self.file[:i] + '.avi'
        dlg = wx.FileDialog( self.frame, "Save as AVI-file", defaultDir, defaultFile, "*.avi", wx.SAVE )

        if dlg.ShowModal() == wx.ID_OK:
            this_file = dlg.GetFilename()
            self.save_dir = dlg.GetDirectory()
            filename = os.path.join( self.save_dir, this_file )
            
            start_color = self.status.GetBackgroundColour()
            self.status.SetBackgroundColour( params.status_blue )
            self.status.SetStatusText( "writing movie of results",
                                       params.status_box )
            wx.BeginBusyCursor()
            wx.Yield()

            movies.write_results_to_avi(self.movie,self.ann_data,filename,framestart,frameend)

            self.status.SetBackgroundColour( start_color )
            self.status.SetStatusText( "", params.status_box )
            wx.EndBusyCursor()
            wx.Yield()

        dlg.Destroy()

    def ShowCurrentFrame( self, framenumber=None ):
        """Grab current frame, draw on it, and display in GUI.
        Also update zoom-ellipse windows, if present."""
        if not self.alive: return
        if not hasattr( self, 'movie' ) or self.movie is None: return
        if self.start_frame < 0: return

        # get frame
        if framenumber is None:
            framenumber = self.start_frame

        try:
            frame, self.last_timestamp = self.movie.get_frame( framenumber )
            if num.isnan(self.last_timestamp):
                self.last_timestamp = float(framenumber) / float(params.DEFAULT_FRAME_RATE)
        except (IndexError, movies.NoMoreFramesException): # framenumber out of range
            return
        self.framenumber_text.SetValue( "Frame: %05d"%(self.start_frame) )
        if self.ann_data is not None and self.ann_file is not None and (framenumber >= 0):
            draw_frame = framenumber - params.start_frame
            if draw_frame >= len(self.ann_data): draw_frame = -1
        else:
            draw_frame = -1

        #print 'showing frame: %d, plotting frame %d out of ann_data'%(framenumber,draw_frame)

        # update small ellipse windows
        if self.menu.IsChecked( xrc.XRCID("menu_settings_zoom") ) and draw_frame >= 0:
            self.zoom_window.SetData(self.ann_data[draw_frame],frame)
            self.zoom_window.Redraw()

        # dim frame
        if self.menu.IsChecked( xrc.XRCID("menu_playback_dim") ):
            frame = frame / 2
        
        # annotate image
        windowsize = [self.img_panel.GetRect().GetHeight(),self.img_panel.GetRect().GetWidth()]

        if self.menu.IsChecked( xrc.XRCID("menu_playback_show_ann") ) and draw_frame >= 0:
            ellipses = self.ann_data[draw_frame]
            old_pts = []
            early_frame = int(max( 0,draw_frame - params.tail_length ))
            for dataframe in self.ann_data[early_frame:draw_frame+1]:
                these_pts = []
                for ellipse in dataframe.itervalues():
                    these_pts.append( (ellipse.center.x, ellipse.center.y, ellipse.identity) )
                old_pts.append( these_pts )

            # draw on image
            (self.img_wind.bitmap,self.resize,self.img_size) = \
                       draw.annotate_image( frame, ellipses, old_pts,
                                            self.ellipse_thickness, windowsize )
            self.num_flies_text.SetValue( "N. Flies: %02d"%len(ellipses) )
            # scale image and display
            #frame = frame[::int(self.scale_factor)+1,::int(self.scale_factor)+1,:]
            #self.img_wind.update_image_and_drawings( "frame", frame, 'RGB8' )
        else:
            self.num_flies_text.SetValue( "" )

            # scale image and display
            (self.img_wind.bitmap,resize,img_size) = imagesk.draw_image(frame,windowsize)
            #frame = frame[::int(self.scale_factor)+1,::int(self.scale_factor)+1]
            #self.img_wind.update_image_and_drawings( "frame", frame, 'MONO8' )

        self.img_wind.Refresh( eraseBackground=False )
        # update the slider
        self.slider.SetThumbPosition( framenumber )

    def OnSlider( self, evt ):
        """Frame slider callback. Change text and display new frame."""
        self.play_break = True
        self.start_frame = self.slider.GetThumbPosition()
        self.ShowCurrentFrame()

    def OnCheckShowAnn( self, evt ):
        """"Show annotation" box checked. Repaint current frame."""
        self.ShowCurrentFrame()

    def OnCheckRefresh( self, evt ):
        if self.menu.IsChecked( xrc.XRCID("menu_do_refresh") ):
            params.do_refresh = True
            if self.tracking:
                self.rate_text.SetValue("Refresh Rate: Never")
        else:
            params.do_refresh = False
            if self.tracking:
                self.rate_text.SetValue("Refresh Period: %02f fr"%params.framesbetweenrefresh)

    def OnResize( self, evt ):
        """Window resized. Repaint in new window size."""
        if evt is not None: evt.Skip()
        self.frame.Layout()
        try:
            self.ShowCurrentFrame()
            new_size = wx.Size( self.img_wind.GetRect().GetWidth()-30,
                                self.slider.GetRect().GetHeight() )
            self.slider.SetMinSize( new_size )
            self.slider.SetSize( new_size )
            const.file_box_max_width = int(float(self.img_wind.GetRect().GetWidth())/11.)
            self.UpdateStatusMovie()
        except AttributeError: pass # during initialization
    
    def OnQuit( self, evt ):
        """Quit selected (or window closing). Stop threads and close window."""
        if self.menu.GetLabel( xrc.XRCID("menu_track_start") ) == const.TRACK_STOP:
            self.OnStopTracking( None ) # quit in mid-operation
        self.play_break = True
        self.WriteUserfile()
        self.alive = False
        self.frame.Destroy()

    def OnStopTracking( self, evt=None ):
        """Stop button pressed. Stop threads."""
        
        self.StopThreads() # located in mtrax_algo
        self.batch_executing = False

        # set tracking flag
        self.tracking = False
        
    def OnStartTrackingMenu( self, evt ):
        """Start button pressed. Begin tracking."""
        if self.menu.GetLabel( xrc.XRCID("menu_track_start") ) == const.TRACK_STOP:
            # stop tracking
            self.OnStopTracking()
        else:
            self.OnStartTracking(evt)

    def OnPlayButton( self, evt ):
        self.OnStartPlayback()

    def OnStopButton(self,evt):
        if self.tracking:
            self.OnStopTracking()
        else:
            self.OnStopPlayback()

    def OnStartTracking(self,evt=None):

        # check for bg model
        isbgmodel = self.CheckForBGModel()

        if isbgmodel == False:
            return

        isshapemodel = self.CheckForShapeModel()
        if isshapemodel == False:
            return

        # set tracking flag
        self.tracking = True

        # update toolbar functions
        self.UpdateToolBar('started')

        self.menu.SetLabel( xrc.XRCID("menu_track_start"), const.TRACK_STOP )
        self.menu.Enable( xrc.XRCID("menu_track_resume"), False )
        self.menu.Check( xrc.XRCID("menu_playback_show_ann"), True )
        self.menu.Enable( xrc.XRCID("menu_playback_show_ann"), False )
        self.menu.Enable( xrc.XRCID("menu_choose_orientations"), False )
        self.menu.Enable( xrc.XRCID("menu_file_export"), True )
        self.menu.Enable( xrc.XRCID("menu_file_save_avi"), True )
        self.menu.Enable( xrc.XRCID("menu_load_settings"), False )
        self.menu.Enable( xrc.XRCID("menu_settings_bg"), False )
        self.menu.Enable( xrc.XRCID("menu_settings_bg_model"), False )
        self.menu.Enable( xrc.XRCID("menu_settings_tracking"), False )
        self.menu.Enable( xrc.XRCID("menu_track_play"), False )
        self.menu.Enable( xrc.XRCID("menu_compute_background"), False )
        self.menu.Enable( xrc.XRCID("menu_compute_shape"), False )

        self.slider.Enable( False )
        wx.Yield() # refresh GUI

        # reinitialize if start tracking, as opposed to resume tracking
        if evt.GetId() == xrc.XRCID("menu_track_resume"):
            #print 'resume tracking'
            # remove the last frame in case writing was interrupted
            if len(self.ann_data) == 1:
                self.ann_data = []
                params.nids = 0
            elif len(self.ann_data) > 1:
                ids = set([])
                # remove last frame
                self.ann_data = self.ann_data[:-1]
                # set ids
                for t in range(len(self.ann_data)):
                    ids |= set(self.ann_data[t].keys())
                params.nids = max(ids) + 1
            self.start_frame = params.start_frame + len(self.ann_data)
                
        else:
            self.ann_data = []
            params.nids = 0
            params.start_frame = self.start_frame

        self.Track() # located in mtrax_algo

        if self.alive:
            self.OnStopTracking()

            # update toolbar function
            self.UpdateToolBar('stopped')
            
            self.menu.SetLabel( xrc.XRCID("menu_track_start"), const.TRACK_START )
            if hasattr(self,'ann_data') and \
                   (self.ann_data is not None) and \
                   (len(self.ann_data) > 0):
                self.menu.Enable(xrc.XRCID("menu_track_resume"),True)
                self.menu.Enable( xrc.XRCID("menu_playback_show_ann"), True )
                self.menu.Enable( xrc.XRCID("menu_choose_orientations"), True )
                self.menu.Enable( xrc.XRCID("menu_file_export"), True )
                self.menu.Enable( xrc.XRCID("menu_file_save_avi"), True )
            self.menu.Enable( xrc.XRCID("menu_track_start"), True )
            self.menu.Enable( xrc.XRCID("menu_load_settings"), True )
            self.menu.Enable( xrc.XRCID("menu_settings_bg"), True )
            self.menu.Enable( xrc.XRCID("menu_settings_bg_model"), True )
            self.menu.Enable( xrc.XRCID("menu_settings_tracking"), True )
            self.menu.Enable( xrc.XRCID("menu_track_play"), True )
            self.menu.Enable( xrc.XRCID("menu_compute_background"), True )
            self.menu.Enable( xrc.XRCID("menu_compute_shape"), True )
            self.slider.Enable( True )
            if self.ann_data is not None and len( self.ann_data ) < 1:
                self.CheckAnnotation()
            else:
                self.ann_file = annot.AnnotationFile( self.ann_filename, __version__ )
                # don't re-read ann_data!

    def OnComputeBg(self,evt):
        start_color = self.status.GetBackgroundColour()
        self.status.SetBackgroundColour( params.status_green )
        self.status.SetStatusText( "calculating background", params.status_box )
        wx.BeginBusyCursor()
        wx.Yield()
        self.bg_imgs.est_bg()
        wx.EndBusyCursor()
        self.status.SetBackgroundColour( start_color )
        self.status.SetStatusText( "", params.status_box )

    def OnComputeShape(self,evt):

        start_color = self.status.GetBackgroundColour()

        if not hasattr( self.bg_imgs, 'center' ) and self.interactive:
            if params.use_median:
                algtxt = 'Median'
            else:
                algtxt = 'Mean'
            msgtxt = 'Background model has not been calculated.\nCalculate now using the following parameters?\n\nAlgorithm: %s\nNumber of Frames: %d' %(algtxt,params.n_bg_frames)
            if wx.MessageBox( msgtxt, "Calculate?", wx.OK|wx.CANCEL ) == wx.CANCEL:
                return
            else:
                # set up for running background calculation
                bg_calc = True
                self.status.SetBackgroundColour( params.status_green )
                self.status.SetStatusText( "calculating background", params.status_box )
                wx.Yield()
                self.bg_imgs.est_bg()

        self.status.SetBackgroundColour( params.status_red )
        self.status.SetStatusText( "calculating shape", params.status_box )
        wx.BeginBusyCursor()
        wx.Yield()
        ell.est_shape( self.bg_imgs )
        wx.EndBusyCursor()
        self.status.SetBackgroundColour( start_color )
        self.status.SetStatusText( "", params.status_box )

    def OnStopPlayback( self, evt=None ):
        # pause playback
        self.play_break = True

        # update toolbar function
        self.UpdateToolBar('stopped')

        # change menu items
        self.menu.SetLabel( xrc.XRCID("menu_track_play"), const.TRACK_PLAY )
        self.menu.Enable( xrc.XRCID("menu_track_start"), True )
        if hasattr(self,'ann_data') and \
               (self.ann_data is not None) and \
               (len(self.ann_data) > 0):
            self.menu.Enable( xrc.XRCID("menu_track_resume"), True )

    def PlaybackMenu( self, evt ):
        if self.menu.GetLabel( xrc.XRCID("menu_track_play") ) == const.TRACK_PAUSE:
            self.OnStopPlayback()
        else:
            self.OnStartPlayback()

    def OnStartPlayback( self, evt=None ):
        """Begin playback."""

        # update toolbar function
        self.UpdateToolBar('started')

        # change menu items
        self.menu.SetLabel( xrc.XRCID("menu_track_play"), const.TRACK_PAUSE )
        self.menu.Enable( xrc.XRCID("menu_track_start"), False )
        self.menu.Enable( xrc.XRCID("menu_track_resume"), False )
        self.play_break = False

        # start playback
        self.start_frame += 1 # don't play current frame again
        self.play_start_stamp = self.last_timestamp
        self.play_start_time = time.time()
        while self.start_frame < self.n_frames:
            # show current frame
            self.slider.SetThumbPosition( self.start_frame )
            self.ShowCurrentFrame()
            wx.Yield()
            if self.play_break: break

            # calculate which frame to show next
            # test actual and movie elapsed time
            actual_time = max( time.time() - self.play_start_time, 0.05 )
            movie_time = max( self.last_timestamp - self.play_start_stamp, 0.05 )
            # the ratio of these two should equal the play_speed...
            if movie_time / actual_time > self.play_speed:
                # more movie time has elapsed than real time, so slow down
                time.sleep( movie_time - actual_time*self.play_speed )
                self.start_frame += 1
            else:
                # more actual time has elapsed than movie time, so skip frames
                self.start_frame += int(round( actual_time*self.play_speed / movie_time ))

        if self.alive:
            self.OnStopPlayback()

    def OnSpeedUpButton( self, evt ):
        if self.tracking:
            self.OnSpeedUpTracking()
        else:
            self.OnChangePlaybackSpeed(evt)

    def OnSlowDownButton( self, evt ):
        if self.tracking:
            self.OnSlowDownTracking()
        else:
            self.OnChangePlaybackSpeed(evt)

    def OnRefreshButton( self, evt ):
        params.request_refresh = True

    def OnSpeedUpTracking(self):

        params.framesbetweenrefresh = max(1,params.framesbetweenrefresh-1)
        self.rate_text.SetValue("Refresh Period: %02d fr"%params.framesbetweenrefresh)

    def OnSlowDownTracking(self):

        params.framesbetweenrefresh += 1
        self.rate_text.SetValue("Refresh Period: %02d fr"%params.framesbetweenrefresh)
        
    def OnChangePlaybackSpeed(self,evt=None):
        """Change playback speed."""
        if evt.GetId() == self.speedup_id:
            self.play_speed *= 2
        elif evt.GetId() == self.slowdown_id:
            self.play_speed /= 2
        self.play_speed = min( self.play_speed, 32.0 )
        self.play_speed = max( self.play_speed, 1/32. )
        self.rate_text.SetValue("Play Rate: %.1f fps"%self.play_speed)
        # reset timers
        self.play_start_stamp = self.last_timestamp
        self.play_start_time = time.time()
        
    def OnBatch( self, evt ):
        """Open batch processing window."""
        if self.batch is not None and self.batch.is_showing:
            self.batch.frame.Raise()
            return
        
        # open selector window
        if self.batch is None:
            self.batch = batch.BatchWindow( self.frame, self.dir, self.filename )
        else: # not none but not showing, either
            self.batch.ShowWindow( self.frame )

        # bind callbacks
        self.batch.frame.Bind( wx.EVT_SIZE, self.OnBatchResize )
        self.batch.frame.Bind( wx.EVT_MOVE, self.OnBatchResize )
        self.batch.frame.Bind( wx.EVT_BUTTON, self.OnBatchExecute, id=xrc.XRCID("button_execute") )

        # set window position from memory
        if self.last_batch_pos is not None:
            self.batch.frame.SetPosition( self.last_batch_pos )
            self.batch.frame.SetSize( self.last_batch_size )

    def OnBatchResize( self, evt ):
        """Batch window was moved or resized, remember new location."""
        evt.Skip()
        try:
            self.last_batch_size = self.batch.frame.GetSize()
            self.last_batch_pos = self.batch.frame.GetPosition()
        except AttributeError: pass # during initialization

    def OnBatchExecute( self, evt ):
        """Begin executing batch processing."""
        if self.interactive and wx.MessageBox( "Execute batch processing now?", "Execute?", wx.YES_NO ) == wx.NO:
            return
        
        self.batch_executing = True
        self.batch.executing = True

        # run batch
        start_list = self.batch.file_list[:]
        for filename in start_list:
            # open movie
            self.filename = filename
            self.dir, self.file = self.filename.rsplit( '/', 1 ) # Linux only
            self.start_frame = 0
            self.OpenMovie()
            self.UpdateStatusMovie()

            # do tracking
            if self.menu.IsEnabled( xrc.XRCID("menu_track_start") ):
                self.OnStartButton( None )
            if not self.batch_executing: break # stop button pressed

            # remove file from list
            self.batch.file_list.pop( 0 )
            self.batch.list_box.Set( self.batch.file_list )

        # finish up... whether batch executed completely or not
        if self.alive:
            if self.batch.is_showing:
                self.batch.OnButtonClose( None )
        if self.batch_executing:
            self.batch = None
            self.batch_executing = False
        else:
            self.batch.executing = False

    def OnCheckBatchStats( self, evt ):
        """Batch statistics box checked. Force re-read of annotation data."""
        self.batch_data = None # currently irrelevant
        
    def OnStats( self, evt ):
        """Make a plot of data from the annotation file."""
        if self.ann_file is None:
            # TODO: could allow batch stats not including this movie
            if self.interactive:
                wx.MessageBox( "No valid annotation file\nexists for this movie\nor no movie is loaded.",
                               "Error", wx.ICON_ERROR )
            else:
                print "no valid annotation file exists"
            return
        
        start_color = self.status.GetBackgroundColour()
        self.status.SetBackgroundColour( params.status_blue )
        wx.BeginBusyCursor()
        wx.Yield()
        
        # if batch, read data from files
        if self.batch is not None and \
               self.menu.IsChecked( xrc.XRCID("menu_stats_batch") ) \
               and True:#self.batch_data is None: # would have to reset this somehow when batch changes
            batch_stats = True
            self.status.SetStatusText( "reading annotation data from files",
                                       params.status_box )
            self.batch_data = []
            start_filename = self.status.GetStatusText( params.file_box )
            for filename in self.batch.file_list:
                self.status.SetStatusText( filename, params.file_box )
                wx.Yield()
                this_filename = filename + '.ann'
                try:
                    this_file = annot.AnnotationFile( this_filename, __version__ )
                except:
                    if self.interactive:
                        wx.MessageBox( "No valid annotation file exists for\n%s\n...skipping"%this_filename, "Warning", wx.ICON_WARNING )
                    else:
                        print "no valid annotation file for %s, skipping"%this_filename
                else:
                    this_data = this_file.GetAnnotation()
                    for datum in this_data:
                        self.batch_data.append( datum )
            self.status.SetStatusText( start_filename, params.file_box )
        else:
            batch_stats = False
        
        # make new frame for plotting
        self.status.SetStatusText( "analyzing", params.status_box )
        wx.Yield()

        # make panel with appropriate methods
        if evt.GetId() == xrc.XRCID( "menu_stats_vel" ):
            frame = wx.Frame( None, -1, "velocity (%d bins)"%draw.const.vel_bins )
            if batch_stats:
                panel = draw.VelPlotPanel( frame, self.batch_data,
                                           "velocity (%d files)"%len(self.batch.file_list),
                                           params.max_jump )
            else:
                panel = draw.VelPlotPanel( frame, self.ann_data,
                                           "velocity (%s)"%self.file,
                                           params.max_jump )
        elif evt.GetId() == xrc.XRCID( "menu_stats_orn" ):
            frame = wx.Frame( None, -1, "orientation (%d bins)"%draw.const.orn_bins )
            if batch_stats:
                panel = draw.OrnPlotPanel( frame, self.batch_data,
                                           "orientation (%d files)"%len(self.batch.file_list) )
            else:
                panel = draw.OrnPlotPanel( frame, self.ann_data,
                                           "orientation (%s)"%self.file )
        elif evt.GetId() == xrc.XRCID( "menu_stats_space" ):
            frame = wx.Frame( None, -1, "space (%d bins)"%draw.const.space_bins )
            if batch_stats:
                panel = draw.SpacePlotPanel( frame, self.batch_data,
                                             "space (%d files)"%len(self.batch.file_list) )
            else:
                panel = draw.SpacePlotPanel( frame, self.ann_data,
                                             "space (%s)"%self.file )
        elif evt.GetId() == xrc.XRCID( "menu_stats_pos" ):
            frame = wx.Frame( None, -1, "position (bins %d pixels)"%draw.const.pos_binsize )
            if batch_stats:
                panel = draw.PosPlotPanel( frame, self.batch_data,
                                           "position (%d files)"%len(self.batch.file_list),
                                           self.movie.get_width(),
                                           self.movie.get_height() )
            else:
                panel = draw.PosPlotPanel( frame, self.ann_data,
                                           "position (%s)"%self.file,
                                           self.movie.get_width(),
                                           self.movie.get_height() )

        # add panel to frame and show it
        sizer = wx.BoxSizer( wx.HORIZONTAL )
        panel.SetSizer( sizer )
        sizer.SetItemMinSize( panel, 100, 100 )
        panel.Fit()
        panel._SetSize()
        frame.Show()
        
        self.status.SetBackgroundColour( start_color )
        self.status.SetStatusText( "", params.status_box )
        wx.EndBusyCursor()

    def OnHelp( self, evt ):
        """Help requested. Popup box with website."""
        wx.MessageBox( "Documentation available at\nhttp://www.dickinson.caltech.edu/Research/Mtrax", "Help" )

    def OnAbout( self, evt ):
        """About box requested."""
        AboutBox( const.info )

def main():
    app = MtraxApp( 0 )
    app.MainLoop()
    
if __name__ == '__main__':
    main()
