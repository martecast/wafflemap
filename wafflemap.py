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
import matplotlib.cm as cm
import matplotlib.colors
import matplotlib.patches

import matplotlib.path as mpath

class Dies:
    ##############################################################################
    
    # dies included in the wafer
    default_wafer_dies = [(-4, 2), (-4, 3), (-4, 4), (-4, 5), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6),
                (-2, 0), (-2, -1), (-2, 1), (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-1, -1), (-1, 0), (-1, 1),
                (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6), (-1, 7), (-1, 8), (0, -2), (0, -1), (0, 0), (0, 1),
                (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, -3), (1, -2), (1, -1), (1, 0),
                (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (2, -3), (2, -2), (2, -1),
                (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (3, -3), (3, -2),
                (3, -1), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (4, -3),
                (4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9),
                (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9),
                (6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (7, 0), (7, 1),
                (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6),
                (9, 2), (9, 3), (9, 4), (9, 5)]
    
    def __init__(self, x_range=[-4,9], y_range=[-3,10],
                 width=9, height=9,
                 v_flip=True, h_flip=False,
                 die_list = default_wafer_dies):
        
        # Default die parameters
        self.default_die_facecolor = 'gray'
        self.default_die_edgecolor = 'black'
        self.default_blank_die_color = 'none'
        self.defautl_die_line_width = 0.5
        default_figsize = (5,5)
        default_figure_dpi = 200
        #######################################
        
        self.x_range = np.array(x_range)
        self.y_range = np.array(y_range)
        
        self.width = width
        self.height = height
        
        die_list_x_col = []
        die_list_y_col = []
        die_list_plotx_col = []
        die_list_ploty_col = []
        die_list_color_col = []
        die_list_edgecolor = []
        in_wafer_list = []
        
        die_x_range = list(range(self.x_range.min(), self.x_range.max()+1))
        die_y_range = list(range(self.y_range.min(), self.y_range.max()+1))
            
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

        self.fig, self.ax = plt.subplots(1,1, figsize=default_figsize,
                                         dpi=default_figure_dpi)
            
            
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
    
    def dies_in_radius(self, radius_in_number_of_dies=0): # change to give a radius in terms of number of dies, and use self.height or slef.width
        die_list = []
        if radius_in_number_of_dies == 0:
            eff_radius = np.ceil(np.max([self.x_range[1]-self.x_range[0], self.y_range[1]-self.y_range[0]])/2)*np.max([self.width, self.height])
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

         
##############################################################################
############################## Plot functions ################################
##############################################################################

    def colorfill_die_list(self, d_list=[], color='gray', edgecolor='black', hatch=''):
        for die in d_list:
            x,y = die
            self.set_color(x,y, color)
            self.set_edgecolor(x,y, edgecolor)
            self.set_hatch(x,y, hatch)
    def get(self, x,y,column=''):
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
    
                
    def plot(self, dies_to_plot=[], fig_margin=6, imshow=True):
        
        if not dies_to_plot:
            dies_to_plot = self.df[self.df.in_wafer == True].xy

        if len(dies_to_plot) > 0:
            for (x,y) in dies_to_plot:
                px = self.get_plotx(x,y)
                py = self.get_ploty(x,y)
                #print("plot", x, y, "at", px, py)
                # ax.plot(die_x, die_y, 'o',c='black', markersize=2)
                r = plt.Rectangle((px, py), self.width, self.height, fill=True,
                                  facecolor=self.get_color(x,y),
                                  edgecolor=self.get_edgecolor(x,y),
                                  hatch=self.get_hatch(x,y),
                                  linewidth=self.defautl_die_line_width)
                self.ax.add_patch(r)
        else:
            print("No dies in wafer to plot. add a die with self.add_die(x,y) or many dies with self.add_die_list(self.dies_in_radius(R)) ")
        
        self.ax.set_axis_off()
        self.ax.axis('equal')
        self.ax.set_xlim([self.df.plotx.min() - fig_margin,
                          self.df.plotx.max() + self.width + fig_margin])
        self.ax.set_ylim([self.df.ploty.min() - fig_margin,
                          self.df.ploty.max() + self.height + fig_margin])
        if imshow:
            plt.show()
        
    def rescale_fig(self, fig_margin=6):
        self.ax.set_xlim([self.df.plotx.min() - fig_margin,
                          self.df.plotx.max() + self.width + fig_margin])
        self.ax.set_ylim([self.df.ploty.min() - fig_margin,
                          self.df.ploty.max() + self.height + fig_margin])
        
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

    ### Labels
    def label_die(self,x,y, label='default', loc='center',  **text_kwargs):
        if 'fontsize' not in text_kwargs:
            text_kwargs['fontsize'] = 6
        if loc == 'center':
            px = self.get_plotx(x,y) + self.width/2
            py = self.get_ploty(x,y) + self.height/2
        # in the future i could add more options to place the label within the die
        if label == 'default':
            label_text = "{}.{}".format(x,y)
        #other default labels may be added
        #elif label == ...
        else:
            label_text = label
            
        self.ax.annotate(label_text, (px, py),
                         ha='center', va='center',
                         **text_kwargs)
    
    def label_all_dies(self, column = "", not_in_wafer=False, **text_kwargs):

        dies_to_label_list = self.df[self.df.in_wafer == True].xy
        
        assert len(dies_to_label_list) > 0, "No dies in wafer to label, to add a die use self.add_die(x,y)"
        
        if not_in_wafer:
            dies_to_label_list = self.df.xy
        
        if column:
            assert column in self.df.columns, "Error: column label not found in die DataFrame"

       
        for (x, y) in np.array(dies_to_label_list):
            if column:
                self.label_die(x,y, label=self.df[(self.df.x==x) & (self.df.y==y)][column].iloc[0],
                               **text_kwargs)
            else:
                self.label_die(x,y, label='default', **text_kwargs)
            
    ###Save figure
    def save_svg(self, filename = 'wafer_test'):
        
        path = r'C:\Users\martin.arteaga\Desktop'
        file = filename + '.svg' if not filename.endswith(".svg") else filename
        self.fig.savefig(os.path.join(path, file),format='svg')
    
    def save_png(self, filename = 'wafer_test'):
        
        path = r'C:\Users\martin.arteaga\Desktop'
        file = filename + '.png' if not filename.endswith(".png") else filename
        self.fig.savefig(os.path.join(path, file),format='png')

    ### Wafer
    def plot_wafer_outline(self, w_rad_in_number_of_dies,
                           x_offset=0, y_offset=0,
                           notch=None, notch_type='f', **kwargs):
        
        w_rad = w_rad_in_number_of_dies * np.max([self.width, self.height])
        
        path_step = 0.01
        
        w_x0 = (self.x_range.min()+self.x_range.max())/2*self.width + x_offset
        w_y0 = (self.y_range.min()+self.y_range.max())/2*self.height + y_offset
        
        if notch:
            assert notch in ['N','S','E','W'], "notch must be either 'N', 'S', 'E' or 'W'"
            
            t = np.arange(0, np.pi * 2.0, path_step)
            t = t.reshape((len(t), 1))
            wafer_X = w_rad * np.cos(t) + w_x0
            wafer_Y = w_rad * np.sin(t) + w_y0
            wafer = np.hstack((wafer_X, wafer_Y))
            
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
            n_big_rad = w_rad/10
            n_small_rad = w_rad/12
            
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
            notch_points = np.hstack((notch_X, notch_Y))
            
            notched_wafer = []
            
            if notch_type == 'f':
                cut_notch = False
            else:
                cut_notch = True
            for x,y in wafer:
                if (x-n_x0)**2/n_x_rad**2 + (y-n_y0)**2/n_y_rad**2 > 1:
                    notched_wafer.append((x,y))
                elif cut_notch == True:
                    notch_points = np.flip(notch_points, axis=0)
                    if notch == 'W':
                        notch_points = np.roll(notch_points, shift=len(notch_points)//2, axis=0)
                    for (xn, yn) in notch_points:
                        if (xn-w_x0)**2 + (yn-w_y0)**2 < w_rad**2:
                            notched_wafer.append((xn,yn))
                    cut_notch=False
            
            # close the path
            notched_wafer.append(notched_wafer[0])
            # avoid weird effects at the joining point of beginning and end 
            notched_wafer.append(notched_wafer[1])
            
            path_codes = np.ones(len(notched_wafer), dtype=mpath.Path.code_type) * mpath.Path.LINETO
            path_codes[0] = mpath.Path.MOVETO
            
            patch = matplotlib.patches.PathPatch(mpath.Path(notched_wafer, path_codes),
                                                 **kwargs)
            self.ax.add_patch(patch)
        
        else:
            c = matplotlib.patches.Circle((w_x0,w_y0), radius=w_rad, **kwargs)
            self.ax.add_patch(c)
      
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
    # lists of dies for examples
    selected_dies = [(1, -3), (4, -3), (2, -2), (5, -2), (-2, -1), (0, -1), (3, -1), (6, -1), (-1, 0), (2, 0), (4, 0),
                     (6, 0), (-2, 1), (1, 1), (5, 1), (8, 1), (-4, 2), (0, 2), (3, 2), (6, 2), (-3, 3), (1, 3), (5, 3),
                     (9, 3), (0, 4), (2, 4), (4, 4), (7, 4), (9, 4), (-4, 5), (-2, 5), (3, 5), (8, 5), (-1, 6), (0, 6),
                     (4, 6), (6, 6), (1, 7), (5, 7), (7, 7), (-1, 8), (3, 8), (0, 9), (2, 9), (5, 9)]
    
    formed_dies_pulsed = [(-4, 2), (-3, 3), (-2, -1), (-2, 1), (-2, 5), (-1, 0), (-1, 8), (0, -1), (0, 2), (0, 6),
                 (0, 9), (1, -3), (1, 3), (1, 7), (2, -2), (2, 0), (2, 9), (3, -1), (3, 5), (3, 8), (4, -3), (4, 0),
                 (4, 4), (5, -2), (5, 1), (5, 3), (5, 7), (5, 9), (6, -1), (6, 0), (6, 6), (7, 4), (7, 7), (8, 1), (8, 5),
                 (9, 4)]
    
    formed_dies_QS = [(-4, 2), (-4, 5), (-3, 3), (-2, 1), (-2, 5), (-1, 0), (-1, 6), (-1, 8), (0, -1), (0, 4), (0, 6),
             (0, 9), (1, -3), (1, 3), (1, 7), (2, -2), (2, 0), (2, 4), (2, 9), (3, -1), (3, 5), (3, 8), (4, -3), (4, 0),
             (4, 4), (4, 6), (5, 1), (5, 3), (5, 7), (6, -1), (6, 0), (6, 2), (6, 6), (7, 4), (7, 7), (8, 1), (8, 5)]
    
    #my die
    """
    d=Dies()
    d.colorfill_die_list(selected_dies,'yellow')  
    d.plot_wafer_outline(8,5,6,notch='E', notch_type = 'c',
                            facecolor="none", edgecolor='k')
    d.plot(fig_margin=12)
    d.label_all_dies()
    """
    # random die to make sure the library works for any use case  
    """
    d = Dies([-2,3],[4,9],
                 width=5,height=3,
                 v_flip=False,h_flip=False,
                 die_list=[])
    d.add_die_list(d.dies_in_radius(2))
    d.plot_wafer_outline(2.5,x_offset=2.2,y_offset=1,notch='W', facecolor="mintcream")
    d.plot(fig_margin=5, imshow=False)
    d.label_all_dies()
    """
    # another example
    """
    #init dies
    d=Dies([1,6],[1,5], width=5, height=5, v_flip=False , h_flip=True, die_list=[])
    # create new column with some random variation
    d.df["Voltage"] = ["{:.1f}V".format((x+y-3)/14+2.8 + np.round(np.random.rand()/2.5-0.2, 1)) for (x,y) in zip(d.df.x, d.df.y)]
    d.add_die_list(d.dies_in_radius())
    norm = matplotlib.colors.Normalize(vmin=2.6,vmax=3.4)
    for (x,y) in d.df.xy:
        d.set_color(x,y, cm.RdYlGn(norm(float(d.get(x,y,'Voltage').strip("V")))))
    d.plot_wafer_outline(3.5,x_offset=2.2,y_offset=2.5,notch='S', notch_type='c', facecolor="none")
    d.plot(fig_margin=3, imshow=False)
    d.label_all_dies(column='Voltage')
    """
    # example with a lot of dies
    """
    d= Dies([1,100],[1,150], width=1.5, height=1,die_list=[])
    d.add_die_list(d.dies_in_radius(50))
    d.plot_wafer_outline(52, x_offset=1, y_offset=0.5, notch='S',
                         notch_type='f', facecolor="none")
    d.plot(fig_margin=5, imshow=False)
    """