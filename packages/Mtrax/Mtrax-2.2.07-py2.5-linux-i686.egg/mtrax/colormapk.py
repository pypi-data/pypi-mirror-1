import matplotlib
import numpy
import matplotlib.colors

def colormap_image(imin,cmap=None,cbounds=None):

    # check to make sure that imin has 2 dimensions or less
    assert(imin.ndim <= 2)

    if cmap is None:
        cmap = matplotlib.cm.jet

    # check to make sure the input colormap is in fact a colormap
    assert(isinstance(cmap, matplotlib.colors.Colormap))

    # copy the image
    im = imin.astype(numpy.double)

    # create the cbounds argument
    if cbounds is not None:
        # check the cbounds input
        assert(len(cbounds)==2)
        assert(cbounds[0]<=cbounds[1])
        # threshold at cbounds
        im = im.clip(cbounds[0],cbounds[1])

    # scale the image to be between 0 and cmap.N-1
    im -= im.min()
    im /= im.max()
    im *= (cmap.N-1.)

    # round
    im = im.round()
    im = im.astype(int)

    # create rgb image
    rgb = cmap(im)
    rgb = rgb[:,:,:-1]

    # scale to 0 to 255
    rgb *= 255
    rgb = rgb.astype(numpy.uint8)

    return rgb
