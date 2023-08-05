# algorithm.py
# KMB 09/07/07

import numpy as num
from scipy.linalg.basic import eps
import time
import wx
from wx import xrc

import wxvalidatedtext as wxvt # part of Motmot

from version import DEBUG
import annfiles as annot
import ellipsesk as ell
from movies import NoMoreFramesException
import settings
import hindsight

from params import params

import pkg_resources # part of setuptools
SETTINGS_RSRC_FILE = pkg_resources.resource_filename( __name__, "track_settings.xrc" )

# MtraxApp.Track #################################################
class MtraxAlgorithm (settings.AppWithSettings):
    """Cannot be used alone -- this class only exists
    to keep algorithm code together in one file."""
    def Track( self ):
        """Run the m-tracker."""

        ## initialization ##

        # maximum number of frames we will look back to fix errors
        self.maxlookback = max(params.lostdetection_length,
                               params.spuriousdetection_length,
                               params.mergeddetection_length,
                               params.splitdetection_length)

        # initialize annotation file
        self.ann_file = annot.AnnotationFile( self.ann_filename, params.version, True )
        self.ann_file.WriteAnnHeader( params.start_frame, self.bg_imgs )

        # write the current tracks to file
        for ff in range(len(self.ann_data)-self.maxlookback):
            self.ann_file.write_ellipses(self.ann_data[ff])
        self.lastframewritten = max(-1,len(self.ann_data)-self.maxlookback-1)
        
        wx.Yield()

        # if we haven't done any tracking yet
        if (self.ann_data is None) or (len(self.ann_data) == 0):
            self.ann_data = []
            params.nids = 0

        # initialize hindsight data structures
        self.hindsight = hindsight.Hindsight(self.ann_data,self.bg_imgs)
        self.hindsight.initialize_milestones()

        self.break_flag = False

        #print 'In Track, just before main loop: self.start_frame = %d, params.start_frame = %d, len(ann_data) = %d'%(self.start_frame,params.start_frame,len(self.ann_data))

        for self.start_frame in range(self.start_frame,self.n_frames):

            if self.break_flag:
                break

            last_time = time.time()

            # perform background subtraction
            (self.dfore,self.isfore) = self.bg_imgs.sub_bg( self.start_frame )

            #print 'time to perform background subtraction: '+str(time.time() - last_time)

            # process gui events
            wx.Yield()
            if self.break_flag:
                break

            # find observations
            self.ellipses = ell.find_ellipses( self.dfore, self.isfore )

            # process gui events
            wx.Yield()
            if self.break_flag:
                break

            # match target identities to observations
            if len( self.ann_data ) > 1:
                flies = ell.find_flies( self.ann_data[-2],
                                        self.ann_data[-1],
                                        self.ellipses )                    
            elif len( self.ann_data ) == 1:
                flies = ell.find_flies( self.ann_data[0],
                                        self.ann_data[0],
                                        self.ellipses )
            else:
                flies = ell.TargetList()
                for i,obs in enumerate(self.ellipses):
                    if obs.isEmpty():
                        print 'empty observation'
                    else:
                        obs.identity = params.nids
                        flies.append(obs)
                        params.nids+=1

            # save to ann_data
            self.ann_data.append( flies )

            # fix any errors using hindsight
            self.hindsight.fixerrors()
            #print 'time to fix errors: '+str(time.time() - last_time)

            # write to file
            if (self.ann_data is not None) and \
                   (len(self.ann_data) > self.maxlookback+self.lastframewritten): 
                self.lastframewritten = self.lastframewritten + 1
                self.ann_file.write_ellipses(self.ann_data[self.lastframewritten])
            #print 'In Track, after writing: self.start_frame = %d, params.start_frame = %d, len(ann_data) = %d'%(self.start_frame,params.start_frame,len(self.ann_data))

            # draw?
            if params.request_refresh or (params.do_refresh and ((self.start_frame % params.framesbetweenrefresh) == 0)):
                self.ShowCurrentFrame()
                params.request_refresh = False

            # process gui events
            wx.Yield()
            if self.break_flag:
                break

        self.Finish()

    def Finish(self):

        # write the rest of the frames to file
        for ff in range(self.lastframewritten+1,len(self.ann_data)):
            self.ann_file.write_ellipses(self.ann_data[ff])
        self.lastframewritten = len(self.ann_data)-1
        # close the file
        self.ann_file.file.close()

    # enddef: Track()

    def StopThreads( self ):

        wx.Yield()

        # stop algorithm
        self.break_flag = True
