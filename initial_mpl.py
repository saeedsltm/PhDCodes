import matplotlib as mpl

def init_plotting():

    mpl.rcParams['figure.figsize']       = (16, 9)
    mpl.rcParams['figure.dpi']           = 75
    mpl.rcParams['font.size']            = 16
    mpl.rcParams['font.family']          = 'Times New Roman'
    mpl.rcParams['axes.labelsize']       = 18
    mpl.rcParams['axes.titlesize']       = 20
    mpl.rcParams['legend.fontsize']      = mpl.rcParams['font.size']
    mpl.rcParams['xtick.labelsize']      = mpl.rcParams['font.size']
    mpl.rcParams['ytick.labelsize']      = mpl.rcParams['font.size']
    mpl.rcParams['xtick.major.size']     = 3
    mpl.rcParams['xtick.minor.size']     = 3
    mpl.rcParams['xtick.major.width']    = 1
    mpl.rcParams['xtick.minor.width']    = 1
    mpl.rcParams['ytick.major.size']     = 3
    mpl.rcParams['ytick.minor.size']     = 3
    mpl.rcParams['ytick.major.width']    = 1
    mpl.rcParams['ytick.minor.width']    = 1
    mpl.rcParams['legend.frameon']       = True
    mpl.rcParams['legend.shadow']        = True
    mpl.rcParams['legend.loc']           = 'lower left'
    mpl.rcParams['legend.numpoints']     = 1
    mpl.rcParams['legend.scatterpoints'] = 1
    mpl.rcParams['axes.linewidth']       = 1
    mpl.rcParams['savefig.dpi']          = 300
    mpl.rcParams['xtick.minor.visible']  = 'False'
    mpl.rcParams['ytick.minor.visible']  = 'False'
    mpl.gca().xaxis.set_ticks_position('bottom')
    mpl.gca().yaxis.set_ticks_position('left')
    mpl.locator_params(nticks=4)

def cm2inch(value):
    return value/2.54

def init_plotting_isi(*args):

    if len(args) == 2:

        xsize = cm2inch(float(args[0]))
        ysize = cm2inch(float(args[1]))

    else:

        xsize = cm2inch(9.5)
        ysize = cm2inch(11.)

    mpl.rcParams['figure.figsize']       = (xsize,ysize)
    mpl.rcParams['figure.dpi']           = 300
    mpl.rcParams['font.size']            = 8
    mpl.rcParams['font.family']          = 'Times New Roman'
    mpl.rcParams['axes.labelsize']       = 8
    mpl.rcParams['axes.titlesize']       = 8
    mpl.rcParams['legend.fontsize']      = 8
    mpl.rcParams['xtick.labelsize']      = 8
    mpl.rcParams['ytick.labelsize']      = 8
    mpl.rcParams['xtick.major.size']     = 2
    mpl.rcParams['xtick.minor.size']     = 1.5
    mpl.rcParams['xtick.major.width']    = 0.50
    mpl.rcParams['xtick.minor.width']    = 0.25
    mpl.rcParams['ytick.major.size']     = 2
    mpl.rcParams['ytick.minor.size']     = 1.5
    mpl.rcParams['ytick.major.width']    = 0.50
    mpl.rcParams['ytick.minor.width']    = 0.25
    mpl.rcParams['legend.frameon']       = True
    mpl.rcParams['legend.shadow']        = False
    mpl.rcParams['legend.loc']           = 'lower left'
    mpl.rcParams['legend.numpoints']     = 1
    mpl.rcParams['legend.scatterpoints'] = 1
    mpl.rcParams['axes.linewidth']       = .5
    mpl.rcParams['savefig.dpi']          = 300
    mpl.rcParams['xtick.minor.visible']  = 'False'
    mpl.rcParams['ytick.minor.visible']  = 'False'
    mpl.rcParams['patch.linewidth']      = .5
