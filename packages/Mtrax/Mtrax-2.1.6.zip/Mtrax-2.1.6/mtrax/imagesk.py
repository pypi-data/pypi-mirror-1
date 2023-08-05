from scipy.misc.pilutil import imresize
import numpy as num
from wxwrap import wx
import string

def img_normalize(img):

    img -= num.min(img)
    v = num.max(img)
    if v > 0:
        img /= v

    return img

def draw_image(img,windowsize=None,zoomaxes=None):

    # get axes if not input
    if zoomaxes is None:
        zoomaxes = [0,img.shape[1]-1,0,img.shape[0]-1]
    # check to make sure valid
    if (int(zoomaxes[3]) < int(zoomaxes[2])) or (int(zoomaxes[1]) < int(zoomaxes[0])):
        raise ValueError('Invalid zoom axes input')
    # crop image
    scale_img = img.copy()
    scale_img = scale_img[int(zoomaxes[2]):int(zoomaxes[3]+1),int(zoomaxes[0]):int(zoomaxes[1]+1)]
    
    # resize image so that it fits in the window
    if windowsize is not None:
        scale_x = float(windowsize[1])/float(scale_img.shape[1])
        scale_y = float(windowsize[0])/float(scale_img.shape[0])
        if scale_x < scale_y:
            size_x = windowsize[1]
            size_y = scale_img.shape[0]*scale_x
            resize = scale_x
        else:
            size_y = windowsize[0]
            size_x = scale_img.shape[1]*scale_y
            resize = scale_y
        scale_img = imresize(scale_img,(int(size_y),int(size_x)))

    # create an rgb image out of img
    if scale_img.ndim == 3:
        if not (scale_img.dtype == 'uint8'):
            scale_img = scale_img.astype('uint8')
    elif scale_img.dtype == 'uint8':
        scale_img = to_rgb8('MONO8',scale_img)
    elif scale_img.dtype == 'double':
        # scale to between 0 and 255
        scale_img = num.astype(img_normalize(scale_img)*255.,'uint8')
        scale_img = to_rgb8('MONO8',scale_img)

    #print 'image shape:'
    #print scale_img.shape
    #print 'resize: %f'%resize
    
    # create a bitmap out of image
    h,w,three = scale_img.shape
    img_size = [h,w]
    image = wx.EmptyImage(w,h)
    image.SetData( scale_img.tostring() )
    bmp = wx.BitmapFromImage(image)

    return (bmp,resize,img_size)

def draw_annotated_image(img,pointlists=None,linelists=None,circlelists=None,
                         windowsize=None,zoomaxes=None,
                         pointcolors=None,linecolors=None,circlecolors=None,
                         pointsizes=None,linewidths=None,circlewidths=None):

    #print 'in draw_annotated_image'

    # get axes if not input
    if zoomaxes is None:
        zoomaxes = [0,img.shape[1]-1,0,img.shape[0]-1]
    # check to make sure valid
    if (int(zoomaxes[3]) < int(zoomaxes[2])) or (int(zoomaxes[1]) < int(zoomaxes[0])):
        raise ValueError('Invalid zoom axes input')
    # crop image
    scale_img = img.copy()
    scale_img = scale_img[int(zoomaxes[2]):int(zoomaxes[3]+1),int(zoomaxes[0]):int(zoomaxes[1]+1)]
    xoffset = -zoomaxes[0]
    yoffset = -zoomaxes[2]

    #print 'zoomaxes = ' + str(zoomaxes)

    # resize image so that it fits in the window
    if windowsize is not None:
        scale_x = float(windowsize[1])/float(scale_img.shape[1])
        scale_y = float(windowsize[0])/float(scale_img.shape[0])
        if scale_x < scale_y:
            size_x = windowsize[1]
            size_y = scale_img.shape[0]*scale_x
            resize = scale_x
        else:
            size_y = windowsize[0]
            size_x = scale_img.shape[1]*scale_y
            resize = scale_y
        scale_img = imresize(scale_img,(int(size_y),int(size_x)))

    #print 'current size of scale_img = ' + str(scale_img.shape)

    # create an rgb image out of img
    if scale_img.ndim == 3:
        if not (scale_img.dtype == 'uint8'):
            scale_img = scale_img.astype('uint8')
    elif scale_img.dtype == 'uint8':
        scale_img = to_rgb8('MONO8',scale_img)
    elif scale_img.dtype == 'double':
        # scale to between 0 and 255
        scale_img = num.astype(img_normalize(scale_img)*255.,'uint8')
        scale_img = to_rgb8('MONO8',scale_img)

    #print 'image shape after converting to rgb:'
    #print scale_img.shape
    #print 'resize: %f'%resize
    
    # create a bitmap out of image
    h,w,three = scale_img.shape
    img_size = [h,w]
    image = wx.EmptyImage(w,h)

    #print 'created empty image of size (%d,%d)'%(w,h)
    
    image.SetData( scale_img.tostring() )

    #print 'set the data'
    
    bmp = wx.BitmapFromImage(image)

    #print 'created bmp'

    # draw into bmp
    drawDC = wx.MemoryDC()
    drawDC.SelectObject( bmp ) # draw into bmp
    # set default point color
    drawDC.SetPen(wx.Pen('GREEN'))
    drawDC.SetBrush(wx.Brush(wx.Colour(255,255,255), wx.TRANSPARENT))
    # by default set point radius to 8
    point_radius=8

    #print 'starting to draw stuff'

    if pointlists is not None:
        pointcolor = 'GREEN'
        for i,points in enumerate(pointlists):
            # set color
            if (pointcolors is not None) and (len(pointcolors) > i):
                pointcolor = wx.Colour(pointcolors[i][0],pointcolors[i][1],pointcolors[i][2])
            if (pointsizes is not None) and (len(pointsizes) > i):
                point_radius = pointsizes[i]
            drawDC.SetPen(wx.Pen(colour=pointcolor,width=point_radius))
            # set radius
            for j,pt in enumerate(points):
                # draw a circle
                x = int((xoffset+pt[0])*resize)
                y = int((yoffset+pt[1])*resize)
                if (x >= 0) and (x < img_size[1]) and \
                   (y >= 0) and (y < img_size[0]):
                    drawDC.DrawCircle(x,y,point_radius)

    #print 'finished drawing points'

    if linelists is not None:
        # set default line color
        linecolor = 'GREEN'
        # set default line width
        linewidth = 1

        for i,lines in enumerate(linelists):

            #print i

            # create a list of wxPoints
            points = []
            for j,pt in enumerate(lines):
                x = int((xoffset+pt[0])*resize)
                y = int((yoffset+pt[1])*resize)
                newpoint = wx.Point(x,y)
                if (j < 1) or not (newpoint == lastpoint):
                    points.append(newpoint)
                    lastpoint = newpoint

            if len(points) == 0:
                continue
            if len(points) == 1:
                points.append(newpoint)

            # set color
            if (linecolors is not None) and (len(linecolors) > i):
                linecolor = wx.Colour(linecolors[i][0],linecolors[i][1],
                                      linecolors[i][2])
            # set width
            if (linewidths is not None) and (len(linewidths) > i):
                linewidth = linewidths[i]
                
            drawDC.SetPen(wx.Pen(colour=linecolor,width=linewidth))

            #print 'drawing line with color'
            #print linecolor
            #print 'width'
            #print linewidth
            #print 'points'
            #print points

            # draw the lines
            drawDC.DrawLines(points)

    #print 'finished drawing lines'

    if circlelists is not None:
        circlecolor = 'GREEN'
        for i,circles in enumerate(circlelists):
            # set color
            if (circlecolors is not None) and (len(circlecolors) > i):
                circlecolor = wx.Colour(circlecolors[i][0],circlecolors[i][1],circlecolors[i][2])
            if (circlewidths is not None) and (len(circlewidths) > i):
                circlewidth = circlewidths[i]
            drawDC.SetPen(wx.Pen(colour=circlecolor,width=circlewidth))
            # set radius
            if (circlewidths is not None) and (len(circlewidths) > i):
                circlewidth = circlewidths[i]
            for j,circle in enumerate(circles):
                # draw a circle
                x = int((xoffset+circle[0])*resize)
                y = int((yoffset+circle[1])*resize)
                r = int(circle[2]*resize)
                if (x >= 0) and (x < img_size[1]) and \
                   (y >= 0) and (y < img_size[0]):
                    drawDC.DrawCircle(x,y,r)

    #print 'finished drawing circles'
                    
    #print 'leaving draw_annotated_image'

    return (bmp,resize,img_size)

def add_annotations(bmp,resize,pointlists=None,linelists=None,
                    zoomaxes=[0,10,0,10],
                    pointcolors=None,linecolors=None,
                    pointsizes=None,linewidths=None):

    # check to make sure valid
    if (zoomaxes is None) or (int(zoomaxes[3]) < int(zoomaxes[2])) \
           or (int(zoomaxes[1]) < int(zoomaxes[0])):
        raise ValueError('Invalid zoom axes input')
    xoffset = -zoomaxes[0]
    yoffset = -zoomaxes[2]

    # draw into bmp
    drawDC = wx.MemoryDC()
    drawDC.SelectObject( bmp ) # draw into bmp
    # set default point color
    drawDC.SetPen(wx.Pen('GREEN'))
    drawDC.SetBrush(wx.Brush(wx.Colour(255,255,255), wx.TRANSPARENT))
    # by default set point radius to 8
    point_radius=8

    if pointlists is not None:
        for i,points in enumerate(pointlists):
            # set color
            if (pointcolors is not None) and (len(pointcolors) > i):
                c = wx.Colour(pointcolors[i][0],pointcolors[i][1],pointcolors[i][2])
                drawDC.SetPen(wx.Pen(c))
            # set radius
            if (pointsizes is not None) and (len(pointsizes) > i):
                point_radius = pointsizes[i]
            for j,pt in enumerate(points):
                # draw a circle
                x = int((xoffset+pt[0])*resize)
                y = int((yoffset+pt[1])*resize)
                drawDC.DrawCircle(x,y,point_radius)

    if linelists is not None:
        # set default line color
        linecolor = 'GREEN'
        # set default line width
        linewidth = 1

        for i,lines in enumerate(linelists):

            #print i

            # create a list of wxPoints
            points = []
            for j,pt in enumerate(lines):
                x = int((xoffset+pt[0])*resize)
                y = int((yoffset+pt[1])*resize)
                newpoint = wx.Point(x,y)
                if (j < 1) or not (newpoint == lastpoint):
                    points.append(newpoint)
                    lastpoint = newpoint

            if len(points) == 0:
                continue
            if len(points) == 1:
                points.append(newpoint)

            # set color
            if (linecolors is not None) and (len(linecolors) > i):
                linecolor = wx.Colour(linecolors[i][0],linecolors[i][1],
                                      linecolors[i][2])
            # set width
            if (linewidths is not None) and (len(linewidths) > i):
                linewidth = linewidths[i]
                
            drawDC.SetPen(wx.Pen(colour=linecolor,width=linewidth))

            #print 'drawing line with color'
            #print linecolor
            #print 'width'
            #print linewidth
            #print 'points'
            #print points

            # draw the lines
            drawDC.DrawLines(points)

    return bmp

def draw_circle(bmp,resize,x,y,r,color=None,zoomaxes=[0,0,0,0]):

    xoffset = -zoomaxes[0]
    yoffset = -zoomaxes[2]

    # draw into bmp
    drawDC = wx.MemoryDC()
    drawDC.SelectObject( bmp ) # draw into bmp
    # set pen color
    if color is None:
        drawDC.SetPen(wx.Pen('GREEN'))
    else:
        c = wx.Colour(color[0],color[1],color[2])
        drawDC.SetPen(wx.Pen(c))

    x = int((xoffset+x)*resize)
    y = int((yoffset+y)*resize)
    r = r*resize

    drawDC.SetBrush(wx.Brush(wx.Colour(255,255,255), wx.TRANSPARENT))
    drawDC.DrawCircle(x,y,r)

    return bmp

def draw_line(bmp,resize,x0,y0,x1,y1,color=None,zoomaxes=[0,0,0,0]):

    xoffset = -zoomaxes[0]
    yoffset = -zoomaxes[2]

    # draw into bmp
    drawDC = wx.MemoryDC()
    drawDC.SelectObject( bmp ) # draw into bmp
    # set pen color
    if color is None:
        drawDC.SetPen(wx.Pen('GREEN'))
    else:
        c = wx.Colour(color[0],color[1],color[2])
        drawDC.SetPen(wx.Pen(c))

    x0 = int((xoffset+x0)*resize)
    y0 = int((yoffset+y0)*resize)
    x1 = int((xoffset+x1)*resize)
    y1 = int((yoffset+y1)*resize)

    drawDC.SetBrush(wx.Brush(wx.Colour(255,255,255), wx.TRANSPARENT))
    drawDC.DrawLine(x0,y0,x1,y1)

    return bmp

def draw_arc(bmp,resize,x0,y0,x1,y1,xc,yc,color=None,zoomaxes=[0,0,0,0]):

    xoffset = -zoomaxes[0]
    yoffset = -zoomaxes[2]

    # draw into bmp
    drawDC = wx.MemoryDC()
    drawDC.SelectObject( bmp ) # draw into bmp
    # set pen color
    if color is None:
        drawDC.SetPen(wx.Pen('GREEN'))
    else:
        c = wx.Colour(color[0],color[1],color[2])
        drawDC.SetPen(wx.Pen(c))

    x0 = int((xoffset+x0)*resize)
    y0 = int((yoffset+y0)*resize)
    x1 = int((xoffset+x1)*resize)
    y1 = int((yoffset+y1)*resize)
    xc = int((xoffset+xc)*resize)
    yc = int((yoffset+yc)*resize)

    drawDC.SetBrush(wx.Brush(wx.Colour(255,255,255), wx.TRANSPARENT))
    drawDC.DrawArc(x0,y0,x1,y1,xc,yc)

    return bmp

def to_rgb8(inputtype,img):
    
    if string.lower(inputtype) == 'mono8':
        rgb_img = img.reshape(img.shape[0],img.shape[1],1)
        rgb_img = num.tile(rgb_img,(1,1,3))
    else:
        print 'Inputtype: ' + inputtype + ' not supported.'
        rgb_img = img

    return rgb_img
