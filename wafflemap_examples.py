# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 15:12:06 2024

@author: martin.arteaga
"""

import wafflemap
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.cm as cm
import numpy as np

# create a figure with multiple axe to put the wafermaps in it
fig, axes = plt.subplots(1,3, figsize=(10,5))

###############################################################################

# Default
print("wafer 1")
wm1 = wafflemap.Wafflemap(ax=axes[0])
wm1.plot_dies()
wm1.plot_wafer_outline()
wm1.label_all_dies()

###############################################################################

# Specific dies in wafer, color dies, circular notch
specific_die_list = [(-4, 2), (-4, 3), (-4, 4), (-4, 5), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-2, 0), (-2, -1), (-2, 1), 
                     (-2, 2), (-2, 3), (-2, 4), (-2, 5), (-2, 6), (-2, 7), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (-1, 6),
                     (-1, 7), (-1, 8), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (1, -3),
                     (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (2, -3), (2, -2), (2, -1), 
                     (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1),
                     (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (4, -3),(4, -2), (4, -1), (4, 0), (4, 1), (4, 2), (4, 3),
                     (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (5, -2), (5, -1), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
                     (5, 7), (5, 8), (5, 9),(6, -1), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (7, 0), (7, 1),
                     (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (9, 2), (9, 3), (9, 4), (9, 5)]

selected_dies = [(1, -3), (4, -3), (2, -2), (5, -2), (-2, -1), (0, -1), (3, -1), (6, -1), (-1, 0), (2, 0), (4, 0),
                 (6, 0), (-2, 1), (1, 1), (5, 1), (8, 1), (-4, 2), (0, 2), (3, 2), (6, 2), (-3, 3), (1, 3), (5, 3),
                 (9, 3), (0, 4), (2, 4), (4, 4), (7, 4), (9, 4), (-4, 5), (-2, 5), (3, 5), (8, 5), (-1, 6), (0, 6),
                 (4, 6), (6, 6), (1, 7), (5, 7), (7, 7), (-1, 8), (3, 8), (0, 9), (2, 9), (5, 9)]
print("wafer 2")
wm2 = wafflemap.Wafflemap(x_range=[-4,9], y_range=[-3,10],
                          v_flip=True, h_flip=False,
                          die_list=specific_die_list,
                          ax=axes[1])
wm2.colorfill_die_list(selected_dies,'yellow')
wm2.plot_dies(margin=12, imshow=False)        
wm2.plot_wafer_outline(45, notch='E', notch_type = 'c', notch_size=1)

###############################################################################

# Custom colors and labels, flat notch and colored wafer
print("wafer 3")
wm3=wafflemap.Wafflemap([1,6],[1,5], v_flip=False , h_flip=True, ax=axes[2])
# create new column with some random variation
wm3.df["Voltage"] = ["{:.1f}V".format((x+y-3)/14+2.8 + np.round(np.random.rand()/2.5-0.2, 1)) for (x,y) in wm3.df.xy]
norm = matplotlib.colors.Normalize(vmin=2.6,vmax=3.4)
for (x,y) in wm3.df.xy:
    wm3.set_color(x,y, cm.RdYlGn(norm(float(wm3.get_value(x,y,'Voltage').strip("V")))))
wm3.plot_dies(margin=5, imshow=False)
wm3.plot_wafer_outline(18, y_offset=-1, notch='S', notch_type='f', notch_size=3,
                       facecolor='gray')
wm3.label_all_dies(column='Voltage', fontsize=7)
print(wm3.get_die_list())
###############################################################################
plt.tight_layout()
plt.show()