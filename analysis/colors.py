from matplotlib import pyplot as plt
import numpy as np
plt.rcParams['figure.facecolor'] = 'white'

# UT BASED CMAPS
def ut(key,print_swatch=False):
	'''
	Returns a list of hexadecimal colors based on UT's signature burnt orange.

	Options for keys to pass in the arguments:
	* Complementary: 2 colors, returns UT Orange and a complementary dark blue. Good for plotting 2 vars.
	* Monochromatic: 2 colors, returns UT Orange and a slightly brighter orange.
	* Analogous: 3 colors, returns nearby shades of red and dark yellow alongside UT Orange.
	* Triadic: 3 colors, returns UT Orange and two maximally perceptually distant colors. Good for plotting 3 vars.
	* Tetradic: 4 colors, returns UT Orange and three maximally perceptually distant colors. Good for plotting 4 vars.

	If print_swatch set to True, will plot a sample graph using matplotlib.

	''' 
	color_dict = {
	'complementary' : ['#bf5700','#0068bf'],
	'monochromatic' : ['#bf5700','#f26e00'],
	'monochromatic_tri': ['#bf5700','#f26e00','#ff8926'],
	'analogous' : ['#bf5700','#bfb700','#bf0009'],
	'triadic' : ['#bf5700','#00bf57','#5700bf'],
	'tetradic' : ['#bf5700','#08bf00','#0068bf','#b600bf']
	}

	x = color_dict[key]

	if print_swatch == True:
		y = np.ones(len(x)).astype('int')
		bar = plt.bar(x,y)
		for i,c in enumerate(x):
			bar[i].set_color(c)
		plt.box(False)
		plt.gca().set_yticks([])

	return x
def ut_analogous_red(key,print_swatch=False):
	'''
	Returns a list of hexadecimal colors based on UT's signature burnt orange.
	By taking analogous colors to the burnt orange hex, we can generate a color palette
	that looks good with burnt orange without explicitly including it in the palette.
	This allows your plots and posters to have excellent color composition while keeping the
	burnt orange in the title/other elements of the visualization, as including it in both
	title elements and plot elements may cause confusion to viewers.

	Options for keys to pass:
	* Complementary: 2 colors, returns analogous dark red and a complementary teal/turquoise.
	* Monochromatic: 2 colors, returns analogous dark red and a lighter shade of red.
	* Analogous: 3 colors, returns analogous dark red, UT Burnt Orange, and a fuschia.
	* Triadic: 3 colors, returns analogus dark red alongside a green and a blue.
	* Tetradic, 4 colors, returns analogous dark red, green, teal/turquoise, and purple.

	If print_swatch set to True, will plot a sample graph using matplotlib.
	'''
	color_dict = {
	'complementary' : ['#BF0007','#00BFB8'],
	'monochromatic' : ['#BF0007','#F20009'],
	'analogous' : ['#BF0007','#BF5800','#BF0067'],
	'triadic' : ['#BF0007','#07BF00','#0007BF'],
	'tetradic' : ['#BF0007','#67BF00','#00BFB8','#5800BF']
	}

	x = color_dict[key]

	if print_swatch == True:
		y = np.ones(len(x)).astype('int')
		bar = plt.bar(x,y)
		for i,c in enumerate(x):
			bar[i].set_color(c)
		plt.box(False)
		plt.gca().set_yticks([])

	return x
def ut_analogous_yellow(key,print_swatch=False):
	'''
	Returns a list of hexadecimal colors based on UT's signature burnt orange.
	By taking analogous colors to the burnt orange hex, we can generate a color palette
	that looks good with burnt orange without explicitly including it in the palette.
	This allows your plots and posters to have excellent color composition while keeping the
	burnt orange in the title/other elements of the visualization, as including it in both
	title elements and plot elements may cause confusion to viewers.

	Options for keys to pass:
	* Complementary: 2 colors, returns analogous yellow and a complementary blue.
	* Monochromatic: 2 colors, returns analogous yellow and a lighter shade of yellow.
	* Analogous: 3 colors, returns analogous yellow, UT Burnt Orange, and a green.
	* Triadic: 3 colors, returns analogus yellow alongside a teal/turquiose and fuschia.
	* Tetradic, 4 colors, returns analogous yellow, green, blue, and burgundy.

	If print_swatch set to True, will plot a sample graph using matplotlib.
	'''
	color_dict = {
	'complementary' : ['#BFB800','#0007BF'],
	'monochromatic' : ['#BFB800','#F2E900'],
	'analogous' : ['#BFB800','#BF5900','#67BF00'],
	'triadic' : ['#BFB800','#00BFB8','#B800BF'],
	'tetradic' : ['#BFB800','#00BF59','#0007BF','#BF0067']
	}

	x = color_dict[key]

	if print_swatch == True:
		y = np.ones(len(x)).astype('int')
		bar = plt.bar(x,y)
		for i,c in enumerate(x):
			bar[i].set_color(c)
		plt.box(False)
		plt.gca().set_yticks([])

	return x
def ut_branding(key='secondary', print_swatch=False):
	'''
	no customization here. just returns UT brand colors as a list for you to choose from.
	primary: burnt orange, gray, and white
	secondary: more colors that seem to be losely based off tertiary colors of ut burnt orange
	'''
	color_dict = {
	'primary' : ['#bf5700','#333f48','#ffffff'],
	'secondary': ['#f8971f','#ffd600','#a6cd57','#579d42','#00a9b7','#005f86','#9cadb7','#d6d2c4']
	}

	x = color_dict[key]

	if print_swatch == True:
		y = np.ones(len(x)).astype('int')
		bar = plt.bar(x,y)
		for i,c in enumerate(x):
			bar[i].set_color(c)
		plt.box(False)
		plt.gca().set_yticks([])

	return 
# COLORBLIND FRIENDLY CMAPS
def okabe_ito(print_swatch=False):
	'''
	Colorblind-friendly palette developed by Masataka Okabe and Kei Ito.
	'''
	colors_list = ['#e69f00','#56b4e9','#009e73','#f0e442','#0072b2','#d55e00','#cc79a7','#000000']
	if print_swatch == True:
		y = np.ones(len(colors_list)).astype('int')
		bar = plt.bar(colors_list,y)
		for i,c in enumerate(colors_list):
			bar[i].set_color(c)
		plt.box(False)
		plt.gca().set_yticks([])
	return colors_list
def tol_bright(print_swatch=False):
	'''
	Colorblind-friendly palette developed by Masataka Okabe and Kei Ito.
	'''
	colors_list = ['#ee6677','#228833','#4477aa','#ccbb44','#66ccee','#aa3377','#bbbbbb']
	if print_swatch == True:
		y = np.ones(len(colors_list)).astype('int')
		bar = plt.bar(colors_list,y)
		for i,c in enumerate(colors_list):
			bar[i].set_color(c)
		plt.box(False)
		plt.gca().set_yticks([])
	return colors_list
def tol_muted(print_swatch=False):
	'''
	Colorblind-friendly palette developed by Masataka Okabe and Kei Ito.
	'''
	colors_list = ['#88ccee','#44aa99','#117733','#332288','#ddcc77','#999933','#cc6677','#882255','#aa4499','#dddddd']
	if print_swatch == True:
		y = np.ones(len(colors_list)).astype('int')
		bar = plt.bar(colors_list,y)
		for i,c in enumerate(colors_list):
			bar[i].set_color(c)
		plt.box(False)
		plt.gca().set_yticks([])
	return colors_list
def tol_light(print_swatch=False):
	'''
	Colorblind-friendly palette developed by Masataka Okabe and Kei Ito.
	'''
	colors_list = ['#bbcc33','#aaaa00','#77aadd','#ee8866','#eedd88','#ffaabb','#99ddff','#44bb99','#dddddd']
	if print_swatch == True:
		y = np.ones(len(colors_list)).astype('int')
		bar = plt.bar(colors_list,y)
		for i,c in enumerate(colors_list):
			bar[i].set_color(c)
		plt.box(False)
		plt.gca().set_yticks([])
	return colors_list
