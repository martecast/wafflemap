# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 16:52:24 2024

@author: martin.arteaga
"""
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.patches
import matplotlib.path as mpath

class Wafflemap:
    
    def __init__(self, x_range=[], y_range=[], die_list = [],
                 die_aspect_ratio=1, v_flip=False, h_flip=False,
                 ax=None):
        """
        Constructor of the Wafflemap class
        Parameters:
            - x_range: interval of the x-coordinate of the dies (tuple of 2 integers)
            - y_range: interval of the y-coordinate of the dies (tuple of 2 integers)
            - die_list list of dies to be included in the wafer (list of 2-tuples)
                (the dies fo the list must be within the given range,
                 i.e.  for a die (x,y), x must be in x_range and y in y_range)
            - die_aspect_ratio: aspect ratio of the dies
            - v_flip: wether to flip the coordinate system of the dies along y
            - h_flip: wether to flip the coordinate system of the dies along x
            - ax: matplotlib.axes.Axes object (to be used only if you want multiple wafermaps in a single figure)
        """
        
        self.height = 5
        self.width = die_aspect_ratio * self.height
        
        # Default die parameters
        self.default_die_facecolor = 'gray'
        self.default_die_edgecolor = 'black'
        self.default_blank_die_color = 'none'
        self.default_die_line_width = 0.5
        # Default wafer outline parameters
        self.default_wafer_linewidth = 1.5
        self.default_wafer_facecolor = 'none' # 'none' means transparent
        self.default_wafer_edgecolor = 'black'
        # Default label parameters
        self.default_fontsize = self.height /1.05
        # Figure parameters
        fig_kwargs = {
            'figsize' : (3,3),
            'dpi' : 200,
            'facecolor' : None, # None means "white" (plt default)
            'edgecolor' : None, # None means "white" (plt default)
            }
        self.default_save_dir = os.path.dirname(__file__)
        
        #######################################################################
        if x_range == []:
            print("No x range: setting default [-5,5]")
            x_range = [-5,5]
        if y_range == []:
            print("No y range: setting default [-5,5]")
            y_range = [-5,5]
        #######################################################################
        self.x_range = np.array(x_range)
        self.y_range = np.array(y_range)
        
        die_list_x_col = []
        die_list_y_col = []
        die_list_plotx_col = []
        die_list_ploty_col = []
        die_list_color_col = []
        die_list_edgecolor = []
        in_wafer_list = []
        
        die_x_range = list(range(self.x_range[0], self.x_range[1]+1))
        die_y_range = list(range(self.y_range[0], self.y_range[1]+1))
            
#        print("die_x_range",die_x_range)
#        print("die_y_range",die_y_range)
            
        for i in die_x_range:
            for j in die_y_range:
                #print("die", i,j)
                die_list_x_col.append(i)
                die_list_y_col.append(j)
                yplot = j*self.height
                if v_flip:
                    yplot = (self.y_range.max()+self.y_range.min()-j)*self.height
                xplot = i*self.width
                if h_flip:
                    xplot = (self.x_range.max()+self.x_range.min()-i)*self.width
                die_list_plotx_col.append(xplot)
                die_list_ploty_col.append(yplot)
                if (i,j) in die_list:
                    die_list_color_col.append(self.default_die_facecolor)
                    die_list_edgecolor.append(self.default_die_edgecolor)
                    in_wafer_list.append((i,j) in die_list)
                else:
                    die_list_color_col.append(self.default_blank_die_color)
                    die_list_edgecolor.append(self.default_blank_die_color)
                    in_wafer_list.append(False)
                
        self.df = pd.DataFrame({"x":die_list_x_col,
                                 "y":die_list_y_col,
                                 "plotx":die_list_plotx_col,
                                 "ploty":die_list_ploty_col,
                                 "color":die_list_color_col,
                                 "edgecolor":die_list_edgecolor,
                                 "hatch":'',
                                 "in_wafer":in_wafer_list})
    
        self.df["xy"]=list(zip(self.df.x, self.df.y))
        
        if die_list == []:
            print("No die list, setting default with dies_in_radius()")
            self.add_die_list(self.dies_in_radius())
        
        if ax is None:
            self.fig, self.ax = plt.subplots(1,1, **fig_kwargs)
        else:
            self.ax = ax
            self.fig = ax.figure # parent figure of the passed ax
            
        self.ax.set_axis_off()
        self.ax.tick_params(axis='both', which='both',
                            length=0, width=0, labelsize=0)
        self.ax.axis('equal')
        self.ax.set_xlim([self.df.plotx.min(),
                          self.df.plotx.max() + self.width])
        self.ax.set_ylim([self.df.ploty.min(),
                          self.df.ploty.max() + self.height])
            
##############################################################################
############################## Die management ################################
##############################################################################  

    def add_die(self,x,y):
        index = self.df.loc[(self.df.x==x)&(self.df.y==y)].index
        self.df.loc[index, 'in_wafer']=True
        self.set_color(x,y, self.default_die_facecolor)
        self.set_edgecolor(x, y, self.default_die_edgecolor)
        
    def add_die_list(self,die_list):
        for die in die_list:
            self.add_die(*die)
    
    def remove_die(self,x,y):
        index = self.df.loc[(self.df.x==x)&(self.df.y==y)].index
        self.df.loc[index, 'in_wafer']=False
        self.set_color(x, y, self.default_blank_die_color)
        self.set_edgecolor(x, y, self.default_blank_die_color)
        self.set_hatch(x, y, '')
    
    def dies_in_radius(self, radius_in_number_of_dies=0):
        die_list = []
        wafer_length_x = self.x_range[1]-self.x_range[0]
        wafer_length_y = self.y_range[1]-self.y_range[0]
        if radius_in_number_of_dies == 0:
            if wafer_length_x > wafer_length_y:
                eff_radius = np.ceil(wafer_length_x/2)*self.width
            else:
                eff_radius = np.ceil(wafer_length_y/2)*self.height
        else:
            eff_radius = radius_in_number_of_dies*np.max([self.width, self.height])
        w_x0 = (self.x_range.min()+self.x_range.max())/2*self.width
        w_y0 = (self.y_range.min()+self.y_range.max())/2*self.height
        for (x, y) in self.df.xy:
            px = self.get_plotx(x,y)
            py = self.get_ploty(x,y)
            if(((px-w_x0)**2+(py-w_y0)**2) < eff_radius**2):
               die_list.append((x,y))
        return die_list  

    def get_die_list(self):
        return self.df[self.df.in_wafer == True].xy.values
         
##############################################################################
############################## Plot functions ################################
##############################################################################

    def colorfill_die_list(self, d_list=[], color='gray', edgecolor='black', hatch=''):
        for die in d_list:
            x,y = die
            self.set_color(x,y, color)
            self.set_edgecolor(x,y, edgecolor)
            self.set_hatch(x,y, hatch)
            
    def get_value(self, x,y,column=''):
        assert column in self.df.columns, "column not found in DataFrame"
        if column:
            return self.df[(self.df.x == x) & (self.df.y == y)][column].iloc[0]
        else:
            return self.df[(self.df.x == x) & (self.df.y == y)]
        
    def get_color(self,x,y):
        df = self.df
        return df[(df.x==x) & (df.y==y)].color.iloc[0]

    def set_color(self,x,y,color):
        if isinstance(color, str):
            pass
        elif self.is_rgba_array(color):
            color = matplotlib.colors.to_hex(color)
        index = self.df.loc[(self.df.x==x)&(self.df.y==y)].index
        self.df.loc[index, 'color']=color
        
    def get_edgecolor(self,x,y):
        df = self.df
        return df[(df.x==x) & (df.y==y)].edgecolor.iloc[0]

    def set_edgecolor(self,x,y,color):
        index = self.df.loc[(self.df.x==x)&(self.df.y==y)].index
        self.df.loc[index, 'edgecolor']=color
        
    def get_hatch(self,x,y):
        df = self.df
        return df[(df.x==x) & (df.y==y)].hatch.iloc[0]

    def set_hatch(self,x,y,hatch):
        index = self.df.loc[(self.df.x==x)&(self.df.y==y)].index
        self.df.loc[index, 'hatch']=hatch
    
    def get_plotx(self,x,y):
        df = self.df
        return df[(df.x==x) & (df.y==y)].plotx.iloc[0]
    
    def get_ploty(self,x,y):
        df = self.df
        return df[(df.x==x) & (df.y==y)].ploty.iloc[0]
    
                
    def plot_dies(self, dies_to_plot=[], margin='tight', imshow=False):
        
        assert margin == 'tight' or  isinstance(margin, float) or isinstance(margin, int), "margin must be either 'tight' or float or int"
        
        if not dies_to_plot:
            dies_to_plot = self.df[self.df.in_wafer == True].xy

        if len(dies_to_plot) > 0:
            for (x,y) in dies_to_plot:
                px = self.get_plotx(x,y)
                py = self.get_ploty(x,y)
                #print("plot", x, y, "at", px, py)
                # ax.plot_dies(die_x, die_y, 'o',c='black', markersize=2)
                r = plt.Rectangle((px, py), self.width, self.height, fill=True,
                                  facecolor=self.get_color(x,y),
                                  edgecolor=self.get_edgecolor(x,y),
                                  hatch=self.get_hatch(x,y),
                                  linewidth=self.default_die_line_width)
                self.ax.add_patch(r)
        else:
            print("No dies in wafer to plot. add a die with self.add_die(x,y) or many dies with self.add_die_list(self.dies_in_radius(R)) ")
        
        if margin == 'tight':
            self.fig.tight_layout()
        else:
            self.ax.set_xlim([self.df.plotx.min() - margin,
                              self.df.plotx.max() + self.width + margin])
            self.ax.set_ylim([self.df.ploty.min() - margin,
                              self.df.ploty.max() + self.height + margin])
    
        if imshow:
            self.fig.show()

        
    def rescale_fig(self, margin=6):
        self.ax.set_xlim([self.df.plotx.min() - margin,
                          self.df.plotx.max() + self.width + margin])
        self.ax.set_ylim([self.df.ploty.min() - margin,
                          self.df.ploty.max() + self.height + margin])
        
    def reset_die(self,x,y):
        self.set_color(x,y,self.default_die_facecolor)
        self.set_edgecolor(x,y,self.default_die_edgecolor)
        self.set_hatch(x,y,'')
        
    def reset(self, what='figure'):
        assert what in ['figure', 'all', 'dies'], "can only reset 'figure', 'dies' or 'all'"
        if what == 'dies' or what == 'all':
            for (x,y) in zip(self.df.x,self.df.y):
                self.reset_die(x,y)
        if what == 'figure' or what == 'all':
            self.ax.cla()
            
    ######### Labels
    def label_die(self,x,y, label='coord', loc='center', fontsize=None, **text_kwargs):
        
        assert loc in ['center', 'lower', 'upper', 'center left', 'lower left', 'upper left', 'center right', 'lower right', 'upper right'], "invalid loc"
        
        if fontsize == None:
            fontsize = self.default_fontsize
        
        if loc == 'center':
            px = self.get_plotx(x,y) + self.width/2
            py = self.get_ploty(x,y) + self.height/2
            horizintal_alignment = 'center'
            vertical_alignment = 'center'
        elif loc == 'lower':
            px = self.get_plotx(x,y) + self.width/2
            py = self.get_ploty(x,y) + self.height/20
            horizintal_alignment = 'center'
            vertical_alignment = 'bottom'
        elif loc == 'upper':
            px = self.get_plotx(x,y) + self.width/2
            py = self.get_ploty(x,y) + self.height - self.height/20
            horizintal_alignment = 'center'
            vertical_alignment = 'top'
        elif loc == 'center left':
            px = self.get_plotx(x,y) + self.width/20
            py = self.get_ploty(x,y) + self.height/2
            horizintal_alignment = 'left'
            vertical_alignment = 'center'
        elif loc == 'lower left':
            px = self.get_plotx(x,y) + self.width/20
            py = self.get_ploty(x,y) + self.height/20
            horizintal_alignment = 'left'
            vertical_alignment = 'bottom'
        elif loc == 'upper left':
            px = self.get_plotx(x,y) + self.width/20
            py = self.get_ploty(x,y) + self.height - self.height/20
            horizintal_alignment = 'left'
            vertical_alignment = 'top'
        elif loc == 'center right':
            px = self.get_plotx(x,y) + self.width - self.width/20
            py = self.get_ploty(x,y) + self.height/2
            horizintal_alignment = 'right'
            vertical_alignment = 'center'
        elif loc == 'lower right':
            px = self.get_plotx(x,y) + self.width - self.width/20
            py = self.get_ploty(x,y) + self.height/20
            horizintal_alignment = 'right'
            vertical_alignment = 'bottom'
        elif loc == 'upper right':
            px = self.get_plotx(x,y) + self.width - self.width/20
            py = self.get_ploty(x,y) + self.height - self.height/20
            horizintal_alignment = 'right'
            vertical_alignment = 'top'
            
        if label == 'coord':
            label_text = "{}.{}".format(x,y)
        #other default labels may be added
        #elif label == ...
        else:
            label_text = label
            
        self.ax.annotate(label_text, (px, py),
                         ha=horizintal_alignment,
                         va=vertical_alignment,
                         fontsize=fontsize,
                         **text_kwargs)
    
    def label_all_dies(self, column = "", not_in_wafer=False, fontsize=None, **text_kwargs):

        dies_to_label_list = self.df[self.df.in_wafer == True].xy.values
        
        assert len(dies_to_label_list) > 0, "No dies in wafer to label, to add a die use self.add_die(x,y)"
        
        if not_in_wafer:
            dies_to_label_list = self.df.xy.values
            
        if column:
            assert column in self.df.columns, "Error: column label not found in die DataFrame"

       
        for (x, y) in np.array(dies_to_label_list):
            
            if column:
                self.label_die(x,y, label=self.df[(self.df.x==x) & (self.df.y==y)][column].iloc[0],
                               fontsize=fontsize,**text_kwargs)
            else:
                self.label_die(x,y, label='coord',fontsize=fontsize, **text_kwargs)

    ### Wafer
    def plot_wafer_outline(self, radius=None,
                           x_offset=0, y_offset=0,
                           facecolor=None, edgecolor=None, linewidth=None,
                           notch=None, notch_type='f', notch_size=None):
        
        if radius == None:
            temp = np.max([(self.x_range.max()-self.x_range.min()+1)/2,
                           (self.y_range.max()-self.y_range.min()+1)/2])
    
            w_rad = temp * np.sqrt((self.width/self.height)**(2) + 1) * self.height
            print('auto radius:', w_rad)
        else:
            w_rad = radius #* np.max([self.width, self.height])

        # Define wafer outline center
        w_x0 = ((self.x_range.min()+self.x_range.max())/2 + 0.5)*self.width + x_offset
        w_y0 = ((self.y_range.min()+self.y_range.max())/2 + 0.75)*self.height + y_offset
        
        self.ax.set_xlim([w_x0 - w_rad - 0.5, w_x0 + w_rad + 0.5])
        self.ax.set_ylim([w_y0 - w_rad - 0.5, w_y0 + w_rad + 0.5])
        
        if linewidth == None:
            linewidth = self.default_wafer_linewidth
        if facecolor == None:
            facecolor = self.default_wafer_facecolor
        if edgecolor == None:
            edgecolor = self.default_wafer_edgecolor
        
        if notch:
            assert notch in ['N','S','E','W'], "notch must be either 'N', 'S', 'E' or 'W'"
            path_step = 0.01
            t = np.arange(0, np.pi * 2.0, path_step)
            t = t.reshape((len(t), 1))
            wafer_X = w_rad * np.cos(t) + w_x0
            wafer_Y = w_rad * np.sin(t) + w_y0
            wafer_XY = np.hstack((wafer_X, wafer_Y))
            
            # All n_* variables are related to the notch
            if notch == 'N':
                n_x0 = w_x0
                n_y0 = w_y0 + w_rad
            elif notch == 'S':
                n_x0 = w_x0
                n_y0 = w_y0 - w_rad
            elif notch == 'E':
                n_x0 = w_x0 + w_rad
                n_y0 = w_y0
            elif notch == 'W':
                n_x0 = w_x0 - w_rad
                n_y0 = w_y0
    
            orientation = 'v' if notch in ['N','S'] else 'h'
            
            # Scaling the size of the notch with respect to the size of the wafer
            if notch_size:
                n_big_rad = notch_size
                n_small_rad = notch_size/1.2 # arbitrary scaling
            else:
                n_big_rad = w_rad/10
                n_small_rad = w_rad/12
            
            assert notch_type in ['f','c','e'], "notch_type must be either 'f' or 'c' or 'e'"
            if notch_type == 'f':
                n_big_rad = n_big_rad*2
            
            if notch_type in  ['c', 'f']:
                n_x_rad = n_big_rad
                n_y_rad = n_big_rad
            elif notch_type == 'e':
                if orientation=='v':
                    n_x_rad = n_small_rad
                    n_y_rad = n_big_rad
                elif orientation =='h':
                    n_x_rad = n_big_rad
                    n_y_rad = n_small_rad
                    
            notch_X = n_x_rad * np.cos(t) + n_x0
            notch_Y = n_y_rad * np.sin(t) + n_y0
            notch_XY = np.hstack((notch_X, notch_Y))
            
            notched_wafer = []
            
            if notch_type == 'f':
                use_notch_points = False
            else:
                use_notch_points = True
                
            for x,y in wafer_XY: # for each point of the wafer (a circle)
                if (x-n_x0)**2/n_x_rad**2 + (y-n_y0)**2/n_y_rad**2 > 1: 
                # if the point is outside of the notch shape (circle or ellipse) then add it to the final outline point list
                    notched_wafer.append((x,y))
                # if the point is not outside the notch shape, then it is inside! so it must not be added to the outline point list
                elif use_notch_points == True:
                    notch_XY = np.flip(notch_XY, axis=0) # the notch must be iterated clock wise to avoid weird shape errors, thus the list is flipped
                    if notch == 'W':
                        notch_XY = np.roll(notch_XY, shift=len(notch_XY)//2, axis=0) # for this particular case the notch points must be cycled to avoid visual glitches
                    for (xn, yn) in notch_XY:
                        if (xn-w_x0)**2 + (yn-w_y0)**2 < w_rad**2:
                        # for each point of the notch if the point is inside the wafer, add it to the ouline point list
                            notched_wafer.append((xn,yn))
                    use_notch_points=False
            
            # close the path by adding the first point at the end of the list
            notched_wafer.append(notched_wafer[0])
            # avoid weird effects at the joining point of beginning and end 
            notched_wafer.append(notched_wafer[1])
            
            path_codes = np.ones(len(notched_wafer), dtype=mpath.Path.code_type) * mpath.Path.LINETO
            path_codes[0] = mpath.Path.MOVETO
            
            outline = matplotlib.patches.PathPatch(mpath.Path(notched_wafer, path_codes),
                                                 facecolor=facecolor,edgecolor=edgecolor,
                                                 linewidth=linewidth,
                                                 zorder=-1)

        
        else:
            outline = matplotlib.patches.Circle((w_x0,w_y0), radius=w_rad, 
                                          facecolor=facecolor, edgecolor=edgecolor,
                                          linewidth=linewidth,
                                          zorder=-1)
        self.ax.add_patch(outline)
        
    ###Save figure
    def save_svg(self, filename = 'wafer_test'):
        
        file = filename + '.svg' if not filename.endswith(".svg") else filename
        if r'/' in filename or r'\\' in filename: 
            self.fig.savefig(filename, format='svg')
        else:
            path = self.default_save_dir
            self.fig.savefig(os.path.join(path, file),format='svg')
    
    def save_png(self, filename = 'wafer_test'):
        
        file = filename + '.png' if not filename.endswith(".png") else filename
        if r'/' in filename or r'\\' in filename: 
            self.fig.savefig(filename, format='png')
        else:
            path = self.default_save_dir
            self.fig.savefig(os.path.join(path, file),format='png')
      
    ### Others
    def is_rgba_array(self, array):
        if not isinstance(array, np.ndarray):
            array = np.array(array)
        if len(array) > 4 or (array > 1).any() :
            return False
        else:
            return True
        
def XY_list_2_tuple_list(XYlist):
    res = []
    for die in XYlist:
        m = re.match(r'X([-\d]+)Y([-\d]+)', die)
        if m:
            res.append((int(m[1]),int(m[2])))
        else:
            print("error",die)
            
    return res

def tuple_list_2_XY_list(tuple_list):
    res = []
    for (x,y) in tuple_list:
        res.append(f'X{x:d}Y{y:d}')            
    return res
        
# tests for when you run this script instead of importing it
if __name__ == "__main__":
    # Default
    wm1 = Wafflemap()
    wm1.plot_dies()
    wm1.plot_wafer_outline()
    wm1.label_all_dies()
    wm1.save_png()