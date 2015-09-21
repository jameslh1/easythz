from pylab import rcParams#, rc
from pylab import MultipleLocator, FormatStrFormatter, text
from matplotlib import font_manager as fm
from matplotlib import cm

params = {'xtick.major.size':8,'ytick.major.size':8,'xtick.minor.size':4,'ytick.minor.size':4,'lines.linewidth':2.0}
rcParams.update(params)
fig_size =  [6.0,4.0]

fp=fm.FontProperties()
fp.set_file('/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf')
fp.set_size(20)

#font = {'size':18 }
#font = { 'family':'Times New Roman', 'size':18 }
#tickfont = { 'family':'Times New Roman', 'size':18 }
#rc('font', **font)


FIG_WIDTH=12.0
FIG_HEIGHT=4.0

SMALL_FIG_SIZE=(0.5*FIG_WIDTH,FIG_HEIGHT)
SMALL_RECT_SIZE=[0.15,0.19,0.95-0.2,0.95-0.25]
SMALL_RECT_SIZE_SUBPLOT121=[0.15,0.15,0.35,0.8]
SMALL_RECT_SIZE_SUBPLOT122=[0.6,0.15,0.35,0.8]
SMALL_RECT_SIZE_SUBPLOT211=[0.2,0.6,0.75,0.35]
SMALL_RECT_SIZE_SUBPLOT212=[0.2,0.25,0.75,0.35]
SMALL_RECT_SIZE_SUBPLOT211_O=[0.15,0.55,0.8,0.4] 	# overlapping x axes
SMALL_RECT_SIZE_SUBPLOT212_O=[0.15,0.15,0.8,0.4]	# overlapping x axes
SMALL_RECT_SIZE_SUBPLOT221=[0.15,0.6,0.3,0.35]
SMALL_RECT_SIZE_SUBPLOT222=[0.65,0.6,0.3,0.35]
SMALL_RECT_SIZE_SUBPLOT223=[0.15,0.15,0.3,0.35]
SMALL_RECT_SIZE_SUBPLOT224=[0.65,0.15,0.3,0.35]
SMALL_RECT_SIZE_SUBPLOT221_O=[0.15,0.55,0.35,0.4]	# overlapping x axes
SMALL_RECT_SIZE_SUBPLOT223_O=[0.15,0.15,0.35,0.4]	# overlapping x axes
SMALL_RECT_SIZE_SUBPLOT222_O=[0.65,0.55,0.3,0.4]	# overlapping x axes
SMALL_RECT_SIZE_SUBPLOT224_O=[0.65,0.15,0.3,0.4]	# overlapping x axes
WIDE_FIG_SIZE=(FIG_WIDTH,1.2*FIG_HEIGHT)
WIDE_RECT_SIZE =[0.10,0.15,0.95-0.1,0.95-0.23]

LEGEND_LOC=8	# 6 = centre left, 7=centre right, 8=lower centre, 9 = upper centre, 10 = centre
#String 	Number
#upper right 	1
#upper left 	2
#lower left 	3
#lower right 	4
#right	 	5
#center left 	6
#center right 	7
#lower center 	8
#upper center 	9
#center 	10
LEGEND_FONT='/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf'
LEGEND_FONT_SIZE=16


cdict = {'red':   ((0.0, 0.0, 0.0),
	           (0.25,0.0, 0.0),
	           (0.5, 0.8, 1.0),
	           (0.75,1.0, 1.0),
	           (1.0, 0.4, 1.0)),

	 'green': ((0.0, 0.0, 0.0),
	           (0.25,0.0, 0.0),
	           (0.5, 0.9, 0.9),
	           (0.75,0.0, 0.0),
	           (1.0, 0.0, 0.0)),

	 'blue':  ((0.0, 0.0, 0.4),
	           (0.25,1.0, 1.0),
	           (0.5, 1.0, 0.8),
	           (0.75,0.0, 0.0),
	           (1.0, 0.0, 0.0))
	}

blue_red = cm.colors.LinearSegmentedColormap('BlueRed', cdict) 




def setTicks(axis,majorLocator,majorFormatter,minorLocator):
	axis.set_major_locator(majorLocator)
	axis.set_major_formatter(majorFormatter)
	axis.set_minor_locator(minorLocator)

#	for x in axis.get_ticklabels():
#		x.set_fontsize(tickfont['size'])
#		x.set_fontname(tickfont['family'])
#		x.set_fontproperties(fp)

	return



def setTicks2(axis,majorSpacing=1.0,minorSpacing=0.2,formatStr='%2.0f'):
	majorLocator   = MultipleLocator(majorSpacing)
	majorFormatter = FormatStrFormatter(formatStr)
	minorLocator   = MultipleLocator(minorSpacing)

	axis.set_major_locator(majorLocator)
	axis.set_major_formatter(majorFormatter)
	axis.set_minor_locator(minorLocator)

	return



def subplotLabel(axes,textStr='(a)',position='top-right',xfr=0.8,yfr=0.8,**kwargs):

	xmin,xmax=axes.get_xlim()
	ymin,ymax=axes.get_ylim()

	if position == 'top-left':
		xpos = (1-xfr)*(xmax-xmin) + xmin
		ypos = yfr*(ymax-ymin) + ymin
	else:
		xpos = xfr*(xmax-xmin) + xmin
		ypos = yfr*(ymax-ymin) + ymin

	txt=axes.text(xpos,ypos,textStr,**kwargs)

	return txt

