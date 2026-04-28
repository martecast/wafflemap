# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 16:52:24 2024

@author: martin.arteaga
"""
import os
import re
import json
from pathlib import Path
from configparser import ConfigParser

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.patches
import matplotlib.path as mpath

######################################################################################
######################################################################################
### default values

default_config_dict = {
    "figure":{
        "fig_width":5,
        "fig_height":5,
        "dpi":200,
        "facecolor": None,
        "edgecolor":None,
    },
    "axis_labels":{
        "size":8
        # offset
    },

    "dies":{
        "aspect_ratio":1 ,
        # ^ aspect_ratio:width/height
        # width value is created during init
        "height":5,
        "facecolor":'gray',
        "edgecolor":'black',
        "blank_die_color":'none',
        # ^ none means transparent
        "linewidth":0.5
    },

    "outline":{
        "enable": True,
        "radius":None,
        "linewidth":1.5,
        "facecolor":'none',
        "edgecolor":'black',
    },

    "notch":{
        "enable":False,
        "type":'c',
        "side":'N',
        "size":2
    },

    "labels":{
        "die_height_over_fontsize_ratio":1.05,
        "fontcolor":"black"
    },
    
    "grid":{
        "enable":True,
        "color":"gray",
        "alpha":0.5,
        "linewidth":0.5
    },
    "coord system":{
        "vflip": False,
        "hflip": False,
        "rotation": 0 # 0, 90, 180
        }
}

######################################################################################
######################################################################################
### classes

# TODO simplify wafflemap with Die and Wafer classes
class Die:
    pass

class Wafer:
    # TODO make sure to write a function to clearly define xrange and yrange
    # because they have great impact on the figure boudaries
    pass


class Wafflemap:

    def __init__(self, xmin=None,xmax=None, ymin=None, ymax=None, die_list = None,
                 die_aspect_ratio=1, v_flip=False, h_flip=False,
                 ax=None):
        """
        Constructor of the Wafflemap class
        Parameters:
            - xmin, xmax: interval of the x-coordinate of the dies (tuple of 2 integers)
            - ymin, ymax: interval of the y-coordinate of the dies (tuple of 2 integers)
            - die_list list of dies to be included in the wafer (list of 2-tuples)
                (the dies fo the list must be within the given range,
                 i.e.  for a die (x,y), x must be in x_range and y in y_range)
            - die_aspect_ratio: aspect ratio of the dies
            - v_flip: wether to flip the coordinate system of the dies along y
            - h_flip: wether to flip the coordinate system of the dies along x
            - ax: matplotlib.axes.Axes object (to be used only if you want 
            multiple wafermaps in a single figure)
        """
        ### TODO make the init with X range and Y range come back
        ### TODO propagate the current init signature to the rest of the file
        self.v_flip = False
        self.h_flip = False # put these two in the config file
        
        
        self.config : dict = self.parse_config(config_file=config_file)
        
        self.die_config = self.config["dies"] 
        self.die_config["width"] = self.die_config["height"]*self.die_config["aspect_ratio"]
        
        self.die_width = self.die_config["width"]
        self.die_height = self.die_config["height"]
        
        self.parse_die_df(die_df_file=die_df_file, die_list=die_list)
        
        self.outline_config = self.config["outline"]
        self.notch_config = self.config["notch"]
        self.default_fontsize = self.die_config["height"]/self.config["labels"]["die_height_over_fontsize_ratio"]
        self.grid_config = self.config["grid"]
        
        # Figure parameters
        self.fig_width=self.config["figure"]["fig_width"]
        self.fig_height=self.config["figure"]["fig_height"]
        self.fig_kwargs = {
            'figsize' : (self.fig_width, self.fig_height),
            'dpi' : self.config["figure"]["dpi"],
            'facecolor' : self.config["figure"]["facecolor"], 
            'edgecolor' : self.config["figure"]["edgecolor"]
            }
        
        self.fig_xmin = None
        self.fig_xmax = None
        self.fig_ymin = None
        self.fig_ymax = None
        
        self.default_save_dir = os.path.dirname(__file__)

            
        if label_df_file is None:
            self.label_df = pd.DataFrame({"x": 0, "y": 0,
                                         "label":'', "loc":'center',
                                         "fontsize":0, "fontcolor":'none',
                                         "visible":False}, index=[0])
        else:
            self.label_df = self.parse_label_df(label_df_file = label_df_file)
            
    def parse_config(self,config_file=None):
        # TODO !!! check if the dictionnary is valid (valid keys and everything)
        if config_file == None:
            return default_config_dict
        else:
            return json.load(config_file)
        
    def parse_die_df(self, die_df_file=None, die_list=[]):
        
        # check columns are ok
        if die_df_file == None:
            self.x_range = np.array([0,8])
            self.y_range = np.array([0,8])
            print(f"No die list file, creating default wafer: X{self.x_range}, Y{self.y_range}")
            self.init_die_df(die_list=die_list) 
        else:
            self.df = pd.read_csv(die_df_file)
            self.x_range = np.array([self.df.x.min(), self.df.x.max()])
            self.y_range = np.array([self.df.y.min(), self.df.y.max()])
            print(f"Loading die list file: X{self.x_range}, Y{self.y_range}\n{die_df_file}")

### init end
######################################################################################
######################################################################################

    def figure_init(self, ax=None):
        ##################################################################
        # create ax instance or link to ax argument
        if ax is None:
            self.fig, self.ax = plt.subplots(1,1, **self.fig_kwargs)
        else:
            self.ax = ax
            self.fig = ax.figure

        # make figure orthonormal
        self.ax.axis('equal')

        # remove axes and ticks
        self.ax.set_axis_off()
        self.ax.xaxis.set_visible(False)
        self.ax.yaxis.set_visible(False)
        # remove figure frame
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        
        
        self.fig_xmin = self.df.plotx.min() - self.die_config["width"],
        self.fig_xmax = self.df.plotx.max() + self.die_config["width"]*2
        self.fig_ymin = self.df.ploty.min() - self.die_config["height"],
        self.fig_ymax = self.df.ploty.max() + self.die_config["height"]*2

    def fig_resize(self):
        if (self.fig_xmin is not None) and (self.fig_xmax is not None) and (self.fig_ymin is not None) and (self.fig_ymax is not None):
            self.ax.set_xlim([self.fig_xmin,self.fig_xmax])
            self.ax.set_ylim([self.fig_ymin,self.fig_ymax])
        else:
            return

    # TODO put the grid and axis labels in a different function !!!!
    def plot_single_die(self, x, y):    
        px = self.get_plotx(x,y)
        py = self.get_ploty(x,y)
        r = plt.Rectangle((px, py),
                          self.die_config["width"], self.die_config["height"],
                          fill=True,
                          facecolor=self.get_color(x,y),
                          edgecolor=self.get_edgecolor(x,y),
                          hatch=self.get_hatch(x,y),
                          linewidth=self.die_config["linewidth"])
        self.ax.add_patch(r)
    
    def plot_dies(self, margin = 0.0, imshow=False,
                  die_coord_on_axis={"enable":True,
                                     "fontsize": 10,
                                     "offset":1,
                                     "left":True,
                                     "right":True,
                                     "top":True,
                                     "bottom": True}):
        
        assert isinstance(margin, float) or isinstance(margin, int), "margin must be either float or int"
        
        dies_to_plot = self.df[self.df.in_wafer == True].xy

        if len(dies_to_plot) > 0:
            for (x,y) in dies_to_plot:
                self.plot_single_die(x,y)
        else:
            print("No dies in wafer to plot. add a die with self.add_die(x,y) or many dies with self.add_die_list(self.dies_in_a_circle(R)) ")
        
        self.fig_xmin = self.df.plotx.min() - margin
        self.fig_xmax = self.df.plotx.max() + self.die_config["width"] + margin
        self.fig_ymin = self.df.ploty.min() - margin
        self.fig_ymax = self.df.ploty.max() + self.die_config["height"] + margin
        self.fig_resize()

        # calculate die coords on axis and create 
        x_coord_list = list(self.df.x.drop_duplicates().sort_values())
        y_coord_list = list(self.df.y.drop_duplicates().sort_values())
        
        px_coord_list_centered = list(self.df.plotx.drop_duplicates().sort_values() + self.die_config["width"]/2)
        py_coord_list_centered = list(self.df.ploty.drop_duplicates().sort_values() + self.die_config["height"]/2)

        px_coord_list = list(self.df.plotx.drop_duplicates().sort_values())
        py_coord_list = list(self.df.ploty.drop_duplicates().sort_values())

        if die_coord_on_axis["enable"]:
            x_offset = self.die_config["width"]*die_coord_on_axis["offset"]
            y_offset = self.die_config["height"]*die_coord_on_axis["offset"]
            for i in range(len(x_coord_list)):
                if die_coord_on_axis["bottom"]:
                    self.ax.annotate(x_coord_list[i], (px_coord_list_centered[i],
                                                       py_coord_list_centered[0]-y_offset),
                                     ha="center", va="center", color="black",
                                     fontsize=die_coord_on_axis["fontsize"])
                if die_coord_on_axis["left"]:
                    self.ax.annotate(y_coord_list[i], (px_coord_list_centered[0]-x_offset,
                                                   py_coord_list_centered[i]),
                                     ha="center", va="center", color="black",
                                     fontsize=die_coord_on_axis["fontsize"])
                if die_coord_on_axis["top"]:
                    self.ax.annotate(x_coord_list[i], (px_coord_list_centered[i],
                                                       py_coord_list_centered[-1]+x_offset),
                                     ha="center", va="center", color="black",
                                     fontsize=die_coord_on_axis["fontsize"])
                if die_coord_on_axis["right"]:
                    self.ax.annotate(y_coord_list[i], (px_coord_list_centered[-1]+y_offset,
                                                       py_coord_list_centered[i]),
                                     ha="center", va="center", color="black",
                                     fontsize=die_coord_on_axis["fontsize"])

                self.fig_xmin = self.fig_xmin - die_coord_on_axis["offset"]
                self.fig_xmax = self.fig_xmax + die_coord_on_axis["offset"]
                self.fig_ymin = self.fig_ymin - die_coord_on_axis["offset"]
                self.fig_ymax = self.fig_ymax + die_coord_on_axis["offset"]
                self.fig_resize()

        if self.grid_config["enable"]:
            if (self.fig_xmin is not None) and (self.fig_xmax is not None) and (self.fig_ymin is not None) and (self.fig_ymax is not None):
                grid_xmin = px_coord_list[0] - np.round(np.abs(self.fig_xmin - px_coord_list[0])/self.die_config["width"]) * self.die_config["width"]
                grid_xmax = px_coord_list[-1] +  np.round(np.abs(self.fig_xmax - px_coord_list[-1])/self.die_config["width"]) * self.die_config["width"]
                grid_ymin = py_coord_list[0] - np.round(np.abs(self.fig_ymin - py_coord_list[0])/self.die_config["height"]) * self.die_config["height"]
                grid_ymax = py_coord_list[-1] +  np.round(np.abs(self.fig_ymax - py_coord_list[-1])/self.die_config["height"]) * self.die_config["height"]
                for x in np.arange(grid_xmin, grid_xmax+1, self.die_config["width"]):
                    self.ax.plot([x,x],[self.fig_ymin,self.fig_ymax], c=self.grid_config["color"], lw = self.grid_config["linewidth"],
                                 alpha=self.grid_config["alpha"], zorder=-5)
                for y in np.arange(grid_ymin, grid_ymax+1, self.die_config["height"]):
                    self.ax.plot([self.fig_xmin,self.fig_xmax],[y,y], c=self.grid_config["color"], lw =self.grid_config["linewidth"],
                                  alpha=self.grid_config["alpha"], zorder=-5)
        if imshow:
            self.fig.show()
##############################################################################
############################## Die management ################################
##############################################################################  
            
    def init_die_df(self, die_list=[]):

        df_x_col = []
        df_y_col = []
        df_plotx_col = []
        df_ploty_col = []
        df_color_col = []
        df_edgecolor = []
        in_wafer_list = []

        die_x_range = list(range(self.x_range[0], self.x_range[1]+1))
        die_y_range = list(range(self.y_range[0], self.y_range[1]+1))
            
        for i in die_x_range:
            for j in die_y_range:
                df_x_col.append(i)
                df_y_col.append(j)
                yplot = j*self.die_config["height"]
                if self.v_flip:
                    yplot = (self.y_range.max()+self.y_range.min()-j)*self.die_config["height"]
                xplot = i*self.die_config["width"]
                if self.h_flip:
                    xplot = (self.x_range.max()+self.x_range.min()-i)*self.die_config["width"]
                df_plotx_col.append(xplot)
                df_ploty_col.append(yplot)
                if (i,j) in die_list:
                    df_color_col.append(self.die_config["facecolor"])
                    df_edgecolor.append(self.die_config["edgecolor"])
                    in_wafer_list.append((i,j) in die_list)
                else:
                    df_color_col.append(self.die_config["blank_die_color"])
                    df_edgecolor.append(self.die_config["blank_die_color"])
                    in_wafer_list.append(False)

        self.df = pd.DataFrame({
            "x":df_x_col,
            "y":df_y_col,
            "plotx":df_plotx_col,
            "ploty":df_ploty_col,
            "color":df_color_col,
            "edgecolor":df_edgecolor,
            "hatch":'',
            "in_wafer":in_wafer_list,
        })

        self.df["xy"]=list(zip(self.df.x, self.df.y))
        self.add_die_list(self.dies_in_a_circle())

        
    def add_die(self,x,y):
        """
        Add given die to te list of dies considered as part of the wafer
        """
        index = self.df.loc[(self.df.x==x)&(self.df.y==y)].index
        self.df.loc[index, 'in_wafer']=True
        self.set_color(x,y, self.die_config["facecolor"])
        self.set_edgecolor(x, y, self.die_config["edgecolor"])
        
    def add_die_list(self,die_list):
        """Add multiple dies by passing a list"""
        for die in die_list:
            self.add_die(*die)
    
    def remove_die(self,x,y):
        """
        Remove given die to te list of dies considered as part of the wafer.
        Also reset it's color and hatch to the 'blank die' format 
        """ # maybe i should change this to only hide the die, without reset
        index = self.df.loc[(self.df.x==x)&(self.df.y==y)].index
        self.df.loc[index, 'in_wafer']=False
        self.set_color(x, y, self.die_config["blank_die_color"])
        self.set_edgecolor(x, y, self.die_config["blank_die_color"])
        self.set_hatch(x, y, '')
    
    def remove_die_list(self, die_list):
        """Remove multiple dies by passing a list"""
        for die in die_list:
            self.remove_die(*die)
    
    def dies_in_a_circle(self, radius_in_number_of_dies=0):
        die_list = []
        wafer_length_x = self.x_range.max()-self.x_range.min()
        wafer_length_y = self.y_range.max()-self.y_range.min()
        if radius_in_number_of_dies == 0:
            if wafer_length_x > wafer_length_y:
                eff_radius = np.ceil(wafer_length_x/2)*self.die_config["width"]
            else:
                eff_radius = np.ceil(wafer_length_y/2)*self.die_config["height"]
        else:
            eff_radius = radius_in_number_of_dies*np.max([self.die_config["width"], self.die_config["height"]])
        w_x0 = (self.x_range.min()+self.x_range.max())/2*self.die_config["width"]
        w_y0 = (self.y_range.min()+self.y_range.max())/2*self.die_config["height"]
        for (x, y) in self.df.xy:
            px = self.get_plotx(x,y)
            py = self.get_ploty(x,y)
            if(((px-w_x0)**2+(py-w_y0)**2) < eff_radius**2):
               die_list.append((x,y))
        return die_list  

    def get_die_list(self):
        return self.df[self.df.in_wafer == True].xy.values
         
################################################################################
############################## Plot functions ##################################
################################################################################

    def colorfill_die_list(self, d_list=[], color='gray', edgecolor='black', hatch=''):
        for die in d_list:
            x,y = die
            self.set_color(x,y, color)
            self.set_edgecolor(x,y, edgecolor)
            self.set_hatch(x,y, hatch)
            
    def get(self, x,y,column=''):
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

    def add_image(self,x,y,im_file):
        arr_image = plt.imread(im_file, format='png')
        pltx = self.get_plotx(x,y)
        plty = self.get_ploty(x,y)
        w = self.die_config["width"]
        h = self.die_config["height"]
        axin = self.ax.inset_axes([pltx,plty,w,h],transform=self.ax.transData)    # create new inset axes in data coordinates
        axin.axis('off')
        axin.imshow(arr_image)
        
    def reset_die(self,x,y):
        self.set_color(x,y,self.die_facecolor)
        self.set_edgecolor(x,y,self.die_edgecolor)
        self.set_hatch(x,y,'')
            
    ######### Labels

    def label_die(self,x,y, label='COORD',
                  loc='center',fontcolor='black', fontsize=None,
                  verbose=False):
        if label == '':
            return
        assert loc in ['upper left' , 'upper', 'upper right',
                       'center left', 'center','center right',
                       'lower left' , 'lower', 'lower right'], "invalid loc"
        
        if fontsize == None:
            fontsize = self.default_fontsize

        new_line = pd.DataFrame({"x": x, "y": y,
                                 "label":label,
                                 "loc":loc,
                                 "fontsize":fontsize,
                                 "fontcolor":fontcolor,
                                 "visible":True}, index=[0])
        if verbose:
            print(f"added label '{label}' to die {x}.{y}")
        self.label_df = pd.concat([self.label_df, new_line], ignore_index=True).reset_index(drop=True)
        # print("updated label df \n", self.label_df)

    def remove_label_die(self,x,y):
        die_labels = self.label_df[(self.label_df.x==x)&(self.label_df.y==y)]
        if len(die_labels)>0:
            last_label_index = die_labels.index[-1]
            print(f"removed label '{self.label_df.loc[last_label_index].label}' from die {x}.{y}")
            self.label_df.drop(index=last_label_index, inplace=True)
        else:
            print(f"No more labels on die {x}.{y}")

    def label_all_dies(self, label='COORD', loc='center',fontcolor='black', fontsize=None):
        dies_to_label_list = self.df[self.df.in_wafer == True].xy.values
        assert len(dies_to_label_list) > 0, "No dies in wafer to label, to add a die use self.add_die(x,y)"
        for (x, y) in np.array(dies_to_label_list):
                self.label_die(x,y,label=label, loc=loc,fontcolor=fontcolor, fontsize=fontsize)

    def draw_label_die(self,x,y):
        """
        Print label on specific die. By default prints the die coordinate.
        - label: string with the label to be printed on the label
        - loc: position of the text within the die
        - fontsize: size of the font :P
        - text_kwargs: other key-word arguments that can be passed to plt.annotate()
        """

        label_list_df = self.label_df[(self.label_df.x == x) &(self.label_df.y == y)]

        if len(label_list_df) == 0:
            return
        for i in label_list_df.index:
            label_visible = label_list_df.visible[i]
            if not label_visible:
                continue
            row = label_list_df.loc[i]
            loc = row["loc"]
            label = row["label"]
            fontsize = row["fontsize"]
            fontcolor = row["fontcolor"]
            if loc == 'center':
                px = self.get_plotx(x,y) + self.die_config["width"]/2
                py = self.get_ploty(x,y) + self.die_config["height"]/2
                horizintal_alignment = 'center'
                vertical_alignment = 'center'
            elif loc == 'lower':
                px = self.get_plotx(x,y) + self.die_config["width"]/2
                py = self.get_ploty(x,y) + self.die_config["height"]/20
                horizintal_alignment = 'center'
                vertical_alignment = 'bottom'
            elif loc == 'upper':
                px = self.get_plotx(x,y) + self.die_config["width"]/2
                py = self.get_ploty(x,y) + self.die_config["height"] - self.die_config["height"]/20
                horizintal_alignment = 'center'
                vertical_alignment = 'top'
            elif loc == 'center left':
                px = self.get_plotx(x,y) + self.die_config["width"]/20
                py = self.get_ploty(x,y) + self.die_config["height"]/2
                horizintal_alignment = 'left'
                vertical_alignment = 'center'
            elif loc == 'lower left':
                px = self.get_plotx(x,y) + self.die_config["width"]/20
                py = self.get_ploty(x,y) + self.die_config["height"]/20
                horizintal_alignment = 'left'
                vertical_alignment = 'bottom'
            elif loc == 'upper left':
                px = self.get_plotx(x,y) + self.die_config["width"]/20
                py = self.get_ploty(x,y) + self.die_config["height"] - self.die_config["height"]/20
                horizintal_alignment = 'left'
                vertical_alignment = 'top'
            elif loc == 'center right':
                px = self.get_plotx(x,y) + self.die_config["width"] - self.die_config["width"]/20
                py = self.get_ploty(x,y) + self.die_config["height"]/2
                horizintal_alignment = 'right'
                vertical_alignment = 'center'
            elif loc == 'lower right':
                px = self.get_plotx(x,y) + self.die_config["width"] - self.die_config["width"]/20
                py = self.get_ploty(x,y) + self.die_config["height"]/20
                horizintal_alignment = 'right'
                vertical_alignment = 'bottom'
            elif loc == 'upper right':
                px = self.get_plotx(x,y) + self.die_config["width"] - self.die_config["width"]/20
                py = self.get_ploty(x,y) + self.die_config["height"] - self.die_config["height"]/20
                horizintal_alignment = 'right'
                vertical_alignment = 'top'
                
            if label == 'COORD':
                label_text = "{}.{}".format(x,y)
            #other default labels may be added
            elif label == 'CHECK':
                self.check_die(x=x,y=y,loc=loc,color=fontcolor,size=fontsize)
                return
            elif label == 'CROSS':
                self.cross_die(x=x,y=y,color=fontcolor,size=fontsize)
                return
            elif label in self.df.columns:
                label_text = str(self.get(x, y, label))
            else:
                label_text = label
            self.ax.annotate(label_text, (px, py),
                             ha=horizintal_alignment,
                             va=vertical_alignment,
                             fontsize=fontsize,
                             color=fontcolor)
    
    def plot_all_labels(self):
        """
        Print label on each die. By default prints the die coordinate, but it
        can print any value stored in the DataFrame attribute.
        - column: name of the DataFrame column whose values will be printed
        - not_in_wafer: wether to label the dies that are not added to the wafermap
        - fontsize: size of the font :P
        - text_kwargs: other key-word arguments that can be passed to plt.annotate()
        """
        
        dies_to_label_list = self.df[self.df.in_wafer == True].xy.values
        assert len(dies_to_label_list) > 0, "No dies in wafer to label, to add a die use self.add_die(x,y)"
       
        for (x, y) in np.array(dies_to_label_list):
            self.draw_label_die(x,y)

    def check_die(self, x, y, loc='center',color='black', size=None):
        px = self.get_plotx(x,y)
        py = self.get_ploty(x,y)
        cx = px+self.die_config["width"]/2
        cy = py+self.die_config["height"]/2

        point1 = (px+self.die_config["width"]/3, cy)
        point2 = (cx, (cy+py)/2)
        point3 = (px+self.die_config["width"]*3/4, py+self.die_config["height"]*3/4)

        check_path = np.array([point1,point2,point3])
        check_codes = np.array([mpath.Path.MOVETO,mpath.Path.LINETO,mpath.Path.LINETO])

        check = matplotlib.patches.PathPatch(mpath.Path(check_path, check_codes),
                                                 facecolor="none",edgecolor=color,
                                                 linewidth=size)
        self.ax.add_patch(check)


    def cross_die(self, x, y, color='black', size=None):
        px = self.get_plotx(x,y)
        py = self.get_ploty(x,y)
        lower_left_corner = (px,py)
        lower_right_corner = (px+self.die_config["width"],py)
        upper_left_corner = (px,py+self.die_config["height"])
        upper_right_corner = (px+self.die_config["width"],py+self.die_config["height"])

        cross_path = np.array([lower_left_corner, lower_right_corner,
                              upper_left_corner, upper_right_corner,
                              lower_left_corner])
        cross_path_codes = np.array([mpath.Path.MOVETO, mpath.Path.MOVETO,
                                  mpath.Path.LINETO, mpath.Path.MOVETO,
                                  mpath.Path.LINETO])

        cross = matplotlib.patches.PathPatch(mpath.Path(cross_path, cross_path_codes),
                                                 facecolor=color,edgecolor=color,
                                                 linewidth=size)
        self.ax.add_patch(cross)


    ### Wafer
    def plot_wafer_outline(self, radius=None, verbose=True,
                           x_offset=0, y_offset=0,
                           facecolor=None, edgecolor=None, linewidth=None,
                           notch=None, notch_type='f', notch_size=None,
                           margin={"enable":True,"value":0.0}):
        """
        Plot a circular outline around the dies.
        - radius: Radius of outline. If None, a radius is calculated based on 
                  die numbers
        - x_offset: displace the center of the outline horizontally
        - y_offset: displace the center of the outline vertically
        - facecolor: background color of the wafer. Transparent by default
        - edgecolor: color of the edge. Black by default
        - linewidth: 
        - notch: Wether to include a notch on the outline and on which side to 
                 place it. By default no notch is added. To add a notch pass
                 'N', 'S', 'E', 'W' to indicate on which side the notch should be
        - notch_type: 'c' for circular notch
                      'e' for elliptic notch
                      'f' for flat cut notch
        - notch_size: size of the notch. Default value is around 3
        """

        if radius == None:
            temp = np.max([(self.x_range.max()-self.x_range.min()+1)/2,
                           (self.y_range.max()-self.y_range.min()+1)/2])
    
            w_rad = temp * np.sqrt((self.die_config["width"]/self.die_config["height"])**(2) + 1) * self.die_config["height"]
            if verbose:
                print('auto radius:', w_rad)
        else:
            w_rad = radius #* np.max([self.die_config["width"], self.die_config["height"]])

        # Define wafer outline center
        w_x0 = ((self.x_range.min()+self.x_range.max())/2 + 0.5)*self.die_config["width"] + x_offset
        w_y0 = ((self.y_range.min()+self.y_range.max())/2 + 0.75)*self.die_config["height"] + y_offset
        
        if abs(self.fig_xmin) < abs(w_x0 - w_rad - 0.5):
            self.fig_xmin = w_x0 - w_rad - 0.5
        if abs(self.fig_xmax) < abs(w_x0 + w_rad + 0.5):
            self.fig_xmax = w_x0 + w_rad + 0.5
        if abs(self.fig_ymin) < abs(w_y0 - w_rad - 0.5):
            self.fig_ymin = w_y0 - w_rad - 0.5
        if abs(self.fig_ymax) < abs(w_y0 + w_rad + 0.5):
            self.fig_ymax = w_y0 + w_rad + 0.5
        self.fig_resize()
        
        if linewidth == None:
            linewidth = self.outline_linewidth
        if facecolor == None or facecolor == '':
            facecolor = self.outline_facecolor
        if edgecolor == None or edgecolor == '':
            edgecolor = self.outline_edgecolor
        
        if notch:
            assert notch in ['N','S','E','W'], f"notch must be either 'N', 'S', 'E' or 'W', received {notch}"
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
                
            for x,y in wafer_XY: # for each point of the outline (a circle)
                if (x-n_x0)**2/n_x_rad**2 + (y-n_y0)**2/n_y_rad**2 > 1: 
                # if the point is outside of the notch shape (circle or ellipse)
                # then add it to the final outline point list
                    notched_wafer.append((x,y))
                # if the point is not outside the notch shape, then it is inside! 
                # so it must not be added to the outline point list
                elif use_notch_points == True:
                    notch_XY = np.flip(notch_XY, axis=0) 
                    # the notch must be iterated clock wise to avoid weird shape 
                    # errors, thus the list is flipped
                    if notch == 'W':
                        notch_XY = np.roll(notch_XY, shift=len(notch_XY)//2, axis=0) 
                        # for this particular case the notch points must be cycled 
                        # to avoid visual glitches
                    for (xn, yn) in notch_XY:
                        if (xn-w_x0)**2 + (yn-w_y0)**2 < w_rad**2:
                        # for each point of the notch if the point is inside the 
                        # wafer, add it to the ouline point list
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

        if radius == None:
            return w_rad
        else:
            return None
        
    ###Save figure
    def pre_save_check(self, filename):
        save_path = Path(filename)
        if not save_path.parent.exists():
            print(f"warning: location does not exist.\n{save_path}\nusing default location instead.")
            save_path = Path(self.default_save_dir) / save_path.name
        return save_path
        
        
    def save_image(self, filename = 'wafer_test'):
        ext = Path(filename).suffix
        if ext not in [".png", ".svg"]:
            print(f"warning: extesnion {ext} is unsupported")
        new_filename = self.pre_save_check(filename)
        if new_filename.suffix != ext:
            new_filename = new_filename.parent / (filename + ext)
        self.fig.savefig(new_filename, 
                         format=ext.replace(".",""),
                         transparent=True)
        return new_filename
      
    ### Others
    def is_rgba_array(self, array):
        if not isinstance(array, np.ndarray):
            array = np.array(array)
        if len(array) > 4 or (array > 1).any() :
            return False
        else:
            return True
        
# def XY_list_2_tuple_list(XYlist):
#     res = []
#     for die in XYlist:
#         m = re.match(r'X([-\d]+)Y([-\d]+)', die)
#         if m:
#             res.append((int(m[1]),int(m[2])))
#         else:
#             print("error",die)
            
#     return res

# def tuple_list_2_XY_list(tuple_list):
#     res = []
#     for (x,y) in tuple_list:
#         res.append(f'X{x:d}Y{y:d}')            
#     return res
        
# tests for when you run this script instead of importing it
if __name__ == "__main__":
    # Default
    wm = Wafflemap()
    wm.figure_init()
    wm.plot_dies()
    wm.plot_wafer_outline()
    wm.label_all_dies()
    # wm.add_image(1,2,r"example_image.png")
    plt.show()
    # wm.save_png()