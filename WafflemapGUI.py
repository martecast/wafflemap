import matplotlib
matplotlib.use('TkAgg')

import json
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from PIL import Image, ImageTk

import tkinter as tk
import tkinter.ttk as ttk

from wafflemap import Wafflemap

class WafflemapGUI(Wafflemap):

    def __init__(self, root, gui_config_file = None, split_windows=True):

        root.title("WafflemapGUI")
        if split_windows:
            root.geometry("450x450")
        else:
            root.geometry("900x450")

        # ICON; from stack overflow 
        # !!!(i have to make the image)
        # ico = Image.open('WafflemapGUI.png')
        # photo = ImageTk.PhotoImage(ico)
        # root.wm_iconphoto(False, photo)

        if split_windows:
            # configure window
            root.columnconfigure(0,weight=1) # for the ui
            root.rowconfigure(0, weight=1)   # required for the only column to fill the frame 
            self.fig_frame=tk.Toplevel(root)
            self.ui_frame=tk.Frame(root)
            self.ui_frame.grid(row=0,column=0,sticky='NEWS')

        else:
            # configure window
            root.columnconfigure(0,weight=1) # weight = horizontal proportion taken by the canvas
            root.columnconfigure(1,weight=1) # weight = horizontal proportion taken by the ui
            root.rowconfigure(0, weight=1)   # required for the only column to fill the frame 
            self.fig_frame=tk.Frame(root)
            self.fig_frame.grid(row=0,column=0,sticky='NEWS')
            self.ui_frame=tk.Frame(root)
            self.ui_frame.grid(row=0,column=1,sticky='NEWS')

        # configure figure frame
        self.fig_frame.columnconfigure(0, weight=1)
        self.fig_frame.rowconfigure(0, weight=1)
        # configure the ui frame
        # The UI layout will entirely depend on this, so be sure of what you want!
        for i in range(10):
            self.ui_frame.rowconfigure(i, weight=1)
        self.ui_frame.columnconfigure(0, weight=1)

        #####################
        # MATPLOTLIB FIGURE #
        #####################
        px = 1/plt.rcParams['figure.dpi']  # pixel in inches
        self.fig_params = {
            "fig_width" : 400,
            "fig_height": 400,
            "x_range" : [],
            "y_range" : [],
            "die_list" : None,
            "v_flip": False,
            "h_flip": False,
            "plot_die_margin": 1,
            "wafer_xoffset": 0.0,
            "wafer_yoffset": 0.0,
            "notch_direction": None,
            "notch_type": "f",
            "notch_size": None
        }
        self.fig=plt.figure(figsize=(self.fig_params["fig_width"]*px,
                                     self.fig_params["fig_height"]*px))
        self.ax=self.fig.add_axes([0,0,1,1])
        self.canvas=FigureCanvasTkAgg(self.fig,master=self.fig_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # canvas.get_tk_widget().grid(row=0,column=0) 
        # keep this in case pack() method stops working
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.fig_frame,
                                            pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
#################################################################################
### WAFFLEMAP INIT
        super().__init__()
        self.figure_init(ax=self.ax)
        self.label_all_dies(label="COORD")
        self.draw_default_wafflemap()

        #####################
        #        UI         #
        #####################

        #label template
        # ttk.Label(text, textvariable, underline, image, compound, width)
        #button template
        # ttk.Button(master, text, command)
        
        ## NOTEBOOK and TABS self.ui_nb.index(nb.select())

        self.ui_nb = ttk.Notebook(master=self.ui_frame)
        self.ui_nb.columnconfigure(0, weight=1)
        self.ui_nb.columnconfigure(1, weight=1)
        self.ui_nb.grid(row=0, column=0,rowspan=8,columnspan=2, sticky="NEWS")

        # create frames/tabs
        frames={
            # frame title : frame object
            "setup":ttk.Frame(self.ui_nb),
            "dies": ttk.Frame(self.ui_nb),
            "outline": ttk.Frame(self.ui_nb),
            "image": ttk.Frame(self.ui_nb)
        }

        # put them in
        for frame_name, frame in frames.items():
            frame.pack(fill='both', expand=True)
            self.ui_nb.add(frame, text=frame_name)

        ### Resize the figure - ROWS 0-1
        resize_fig_frame = ttk.Labelframe(master= frames["setup"], text="Resize figure")
        resize_fig_frame.grid(row=0, column=0, sticky="WN")
        for col, col_w in zip(range(4),[1]*4):
            resize_fig_frame.columnconfigure(col, weight=col_w)
        for row, row_w in zip(range(2),[1]*2):
            resize_fig_frame.columnconfigure(row, weight=row_w)
        im_resizew_label = ttk.Label(master=resize_fig_frame, text="Width (px)")
        im_resizeh_label = ttk.Label(master=resize_fig_frame, text="Height (px)")
        self.im_width=tk.StringVar() # default value of StringVar is ''
        self.im_height=tk.StringVar()# default value of StringVar is ''
        im_resizew_entry = ttk.Entry(master=resize_fig_frame, width=7, textvariable=self.im_width)
        im_resizeh_entry = ttk.Entry(master=resize_fig_frame, width=7, textvariable=self.im_height)
        apply_resize_b = ttk.Button(master=resize_fig_frame,text="Apply", command=lambda: self.resize_figure())

        im_resizew_label.grid(row=0,column=0, sticky="NE")
        im_resizew_entry.grid(row=0,column=1, sticky="NW")
        im_resizeh_label.grid(row=0,column=2, sticky="NE")
        im_resizeh_entry.grid(row=0,column=3, sticky="NW")
        apply_resize_b.grid(row=0,column=5, sticky="E")

        ### Change the Die range
        die_range_frame = ttk.Labelframe(master= frames["setup"], text='Wafer Die Ranges')
        die_range_frame.grid(row=1, column=0, sticky="WN")
        for col, col_w in zip(range(5),[1]*5):
            die_range_frame.columnconfigure(col, weight=col_w)
        for row, row_w in zip(range(2),[1]*2):
            die_range_frame.columnconfigure(row, weight=row_w)
        waff_die_rangex_label = ttk.Label(master=die_range_frame, text="Range X")
        waff_die_rangey_label = ttk.Label(master=die_range_frame, text="Range Y")
        self.die_rangex_min=tk.StringVar(value="xmin")
        self.die_rangex_max=tk.StringVar(value="xmax")
        self.die_rangey_min=tk.StringVar(value="ymin")
        self.die_rangey_max=tk.StringVar(value="ymax")
        die_rangexmin_entry = ttk.Entry(master=die_range_frame, width=5, textvariable=self.die_rangex_min)
        die_rangexmax_entry = ttk.Entry(master=die_range_frame, width=5, textvariable=self.die_rangex_max)
        die_rangeymin_entry = ttk.Entry(master=die_range_frame, width=5, textvariable=self.die_rangey_min)
        die_rangeymax_entry = ttk.Entry(master=die_range_frame, width=5, textvariable=self.die_rangey_max)
        apply_die_range_b = ttk.Button(master=die_range_frame,text="Apply", command=lambda: self.rerange_wafflemap())

        waff_die_rangex_label.grid(row=0,column=0, sticky="E")
        waff_die_rangey_label.grid(row=0,column=3, sticky="E")
        die_rangexmin_entry.grid(row=0,column=1, sticky="W")
        die_rangexmax_entry.grid(row=0,column=2, sticky="W")
        die_rangeymin_entry.grid(row=0,column=4, sticky="W")
        die_rangeymax_entry.grid(row=0,column=5, sticky="W")
        apply_die_range_b.grid(row=0,column=6, sticky="E")

        
        ### Coord Flip configuration
        coord_flip_frame = ttk.Labelframe(master= frames["setup"], text='Flip Coordinates')
        coord_flip_frame.grid(row=2, column=0, sticky="WN")
        self.vflip_var = tk.BooleanVar()   # default is False
        self.hflip_var = tk.BooleanVar()   # default is False
        vflip_check = ttk.Checkbutton(coord_flip_frame, text='vertically', variable=self.vflip_var,command=lambda: self.flip_wafflemap() )
        hflip_check = ttk.Checkbutton(coord_flip_frame, text='horizontally', variable=self.hflip_var,command=lambda: self.flip_wafflemap())
        ## Placement
        vflip_check.grid(row=0,column=0)
        hflip_check.grid(row=0,column=1)

        die_coord_labelframe = ttk.Labelframe(master= frames["setup"], text='Enable Die Coordinates')
        die_coord_labelframe.grid(row=3, column=0, sticky="WN")
        ## die coords on axes:
        self.diexy_onaxis_var = tk.BooleanVar(value=False)
        diexy_onaxis_checkb = ttk.Checkbutton(die_coord_labelframe, text='Die coordinates on axis',
                                             variable=self.diexy_onaxis_var,
                                             command=lambda: self.toggle_diexy_onaxis())
        self.diexy_onaxis_offset_var=tk.DoubleVar(value=1)
        diexy_onaxis_offset_label = tk.Label(master=die_coord_labelframe, text="Offset")
        diexy_onaxis_offset_sbox = ttk.Spinbox(master=die_coord_labelframe, width=5,
                                                from_=0, to=10, increment=1,
                                                textvariable=self.diexy_onaxis_offset_var,
                                                command=lambda: self.refresh_wafflemap())
        self.diexy_onaxis_size_var=tk.DoubleVar(value=7)
        diexy_onaxis_size_label = tk.Label(master=die_coord_labelframe, text="Size")
        diexy_onaxis_size_sbox = ttk.Spinbox(master=die_coord_labelframe, width=5,
                                                from_=1, to=15, increment=1,
                                                textvariable=self.diexy_onaxis_size_var,
                                                command=lambda: self.refresh_wafflemap())
        diexy_onaxis_checkb.grid(row=0,column=0, sticky="WN")
        diexy_onaxis_offset_label.grid(row=1,column=0, sticky="WN")
        diexy_onaxis_size_label.grid(row=2,column=0, sticky="WN")
        diexy_onaxis_offset_sbox.grid(row=1,column=1, sticky="WN")
        diexy_onaxis_size_sbox.grid(row=2,column=1, sticky="WN")

        for child in frames["setup"].winfo_children():
            child.grid_configure(padx=5, pady=5)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=5, pady=2)

        ##  BASIC EDITING FRAME
        ### ADD/REMOVE - COLORIZE - LABEL DIES
        die_edit_frame = ttk.Labelframe(master= frames["dies"], text='Edit Dies')
        die_edit_frame.grid(row=3, column=0, sticky="WN")
        for col, col_w in zip(range(3),[1]*3):
            die_edit_frame.columnconfigure(col, weight=col_w)
        for row, row_w in zip(range(2),[1]*4):
            die_edit_frame.columnconfigure(row, weight=row_w)

        self.edit_choice = tk.IntVar(master=root)
        addrem_radbutt = ttk.Radiobutton(master=die_edit_frame, text='Add/Remove', value=1,
                                        variable=self.edit_choice)
        color_radbutt = ttk.Radiobutton(master=die_edit_frame, text='Colorize', value=2,
                                        variable=self.edit_choice)
        hatch_radbutt = ttk.Radiobutton(master=die_edit_frame, text='Hatch', value=3,
                                        variable=self.edit_choice)
        label_radbutt = ttk.Radiobutton(master=die_edit_frame, text="Label",value=4,
                                        variable=self.edit_choice)

        addrem_radbutt.grid(row=0,column=0, sticky="W")
        color_radbutt.grid(row=1,column=0, sticky="W")
        hatch_radbutt.grid(row=2,column=0, sticky="W")
        label_radbutt.grid(row=3,column=0, sticky="W")
        self.color_die_entry = tk.StringVar()
        self.hatch_die_entry = tk.StringVar()
        self.label_text=tk.StringVar()
        color_entry = ttk.Entry(master=die_edit_frame, width=20, textvariable=self.color_die_entry)
        color_entry.grid(row=1, column=1, columnspan=2)
        hatch_entry = ttk.Entry(master=die_edit_frame, width=20, textvariable=self.hatch_die_entry)
        hatch_entry.grid(row=2, column=1, columnspan=2)
        label_entry = ttk.Entry(master=die_edit_frame, width=20, textvariable=self.label_text)
        label_entry.grid(row=3, column=1)

        label_loc_frame = ttk.Labelframe(master= die_edit_frame, text="label location")
        label_loc_frame.grid(row=4, column=0, rowspan=2)
        self.label_loc_var = tk.IntVar(value=5)
        label_loc_NW = ttk.Radiobutton(master=label_loc_frame, value=1,variable=self.label_loc_var)
        label_loc_NN = ttk.Radiobutton(master=label_loc_frame, value=2,variable=self.label_loc_var)
        label_loc_NE = ttk.Radiobutton(master=label_loc_frame, value=3,variable=self.label_loc_var)
        label_loc_WW = ttk.Radiobutton(master=label_loc_frame, value=4,variable=self.label_loc_var)
        label_loc_CC = ttk.Radiobutton(master=label_loc_frame, value=5,variable=self.label_loc_var)
        label_loc_EE = ttk.Radiobutton(master=label_loc_frame, value=6,variable=self.label_loc_var)
        label_loc_SW = ttk.Radiobutton(master=label_loc_frame, value=7,variable=self.label_loc_var)
        label_loc_SS = ttk.Radiobutton(master=label_loc_frame, value=8,variable=self.label_loc_var)
        label_loc_SE = ttk.Radiobutton(master=label_loc_frame, value=9,variable=self.label_loc_var)
        label_loc_NW.grid(row=0, column=0)
        label_loc_NN.grid(row=0, column=1)
        label_loc_NE.grid(row=0, column=2)
        label_loc_WW.grid(row=1, column=0)
        label_loc_CC.grid(row=1, column=1)
        label_loc_EE.grid(row=1, column=2)
        label_loc_SW.grid(row=2, column=0)
        label_loc_SS.grid(row=2, column=1)
        label_loc_SE.grid(row=2, column=2)
        for child in label_loc_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.loc_dict = {
            1:"upper left",
            2:"upper",
            3:"upper right",
            4:"center left",
            5:"center",
            6:"center right",
            7:"lower left",
            8:"lower",
            9:"lower right"
        }
        label_fontsize_label = ttk.Label(master=die_edit_frame, text="label size")
        label_fontsize_label.grid(row=7, column=0)
        self.label_fontsize=tk.StringVar(value="10")
        label_fontsize_sbox=ttk.Spinbox(master=die_edit_frame, width=10,
                                        from_=1, to=50, increment=2,
                                        textvariable=self.label_fontsize)
        label_fontsize_sbox.grid(row=7, column=1)
        apply_all_button=ttk.Button(master=die_edit_frame, text="Apply to all dies", command=lambda: self.apply_label_to_all())
        apply_all_button.grid(row=8,column=0, sticky="NE")
        remove_all_button=ttk.Button(master=die_edit_frame, text="Remove all labels", command=lambda: self.remove_all_labels())
        remove_all_button.grid(row=8,column=1, sticky="NE")

        ### Format frames to make them less tight
        for child in frames["dies"].winfo_children():
            child.grid_configure(padx=5, pady=5)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=5, pady=2)
        
############################################################################################################################
#### OUTLINE AND NOTCH TAB
        # outline_edits_tab.columnconfigure(0, weight=1)
        # outline_edits_tab.rowconfigure(0, weight=1)
        outline_edit_frame = ttk.Labelframe(master=frames["outline"], text="outline parameters")
        outline_edit_frame.grid(row=1,column=0,sticky="NEWS")
        ## outline enable/diable
        outline_enable_label = ttk.Label(master=outline_edit_frame, text="enable")
        self.outline_enable_var = tk.BooleanVar(value=self.outline_config["enable"])
        
        
        self.outline_size_var = tk.DoubleVar(value=np.round(self.outline_config["radius"],2))
        self.outline_xoffset_var = tk.DoubleVar(value=self.fig_params["wafer_xoffset"])
        self.outline_yoffset_var = tk.DoubleVar(value=self.fig_params["wafer_yoffset"])
        self.linewidth_var = tk.DoubleVar(value=self.outline_config["linewidth"])
        self.outline_edgecolor_var = tk.StringVar(value=self.outline_config["edgecolor"])
        self.outline_facecolor_var = tk.StringVar(value=self.outline_config["facecolor"])
        self.outline_alpha_var = tk.DoubleVar(value=0.5)
        self.outline_zorder_var = tk.DoubleVar(value=-1)

        self.notch_enable_var = tk.BooleanVar(value=self.notch_config["enable"])
        self.notch_type_var = tk.StringVar(value=self.notch_config["type"])
        self.notch_dir_var = tk.StringVar(value=self.notch_config["side"])
        self.notch_size_var = tk.DoubleVar(value=self.notch_config["size"])

        facecolor_label = ttk.Label(master=outline_edit_frame, text="facecolor")
        outline_alpha_label = ttk.Label(master=outline_edit_frame, text="alpha")
        outline_enable = ttk.Radiobutton(master=outline_edit_frame, value=True,text="yes",variable=self.outline_config["enable"], command=lambda: self.refresh_wafflemap())
        outline_disable = ttk.Radiobutton(master=outline_edit_frame, value=False,text="no",variable=self.outline_config["enable"], command=lambda: self.refresh_wafflemap())
        outline_enable_label.grid(row=0,column=0,sticky="NEWS")
        outline_enable.grid(row=0,column=1,sticky="NEWS")
        outline_disable.grid(row=0,column=2,sticky="NEWS")
        ## size and linewidth
        size_label = ttk.Label(master=outline_edit_frame, text="size")
        size_spinbox = ttk.Spinbox(master=outline_edit_frame, width=6, text = "test",
                                    from_=1, to=50, increment=1,
                                    textvariable=self.outline_size_var,
                                    command=lambda: self.refresh_wafflemap())
        size_label.grid(row=1, column=0)
        size_spinbox.grid(row=1, column=1)
        linewidth_label = ttk.Label(master=outline_edit_frame, text="linewidth")
        linewidth_spinbox = ttk.Spinbox(master=outline_edit_frame, width=6,
                                    from_=0.1, to=10, increment=0.5,
                                    textvariable=self.linewidth_var,
                                    command=lambda: self.refresh_wafflemap())
        linewidth_label.grid(row=1, column=2)
        linewidth_spinbox.grid(row=1, column=3)
        ## offset
        xoffset_label = ttk.Label(master=outline_edit_frame, text="x offset")
        xoffset_spinbox = ttk.Spinbox(master=outline_edit_frame, width=6,
                                    from_=-50, to=50, increment=0.5,
                                    textvariable=self.outline_xoffset_var,
                                    command=lambda: self.refresh_wafflemap())
        xoffset_label.grid(row=2, column=0)
        xoffset_spinbox.grid(row=2, column=1)
        yoffset_label = ttk.Label(master=outline_edit_frame, text="y offset")
        yoffset_spinbox = ttk.Spinbox(master=outline_edit_frame, width=6,
                                    from_=-50, to=50, increment=0.5,
                                    textvariable=self.outline_yoffset_var,
                                    command=lambda: self.refresh_wafflemap())
        yoffset_label.grid(row=2, column=2)
        yoffset_spinbox.grid(row=2, column=3)
        ## facecolor and edgecolor
        facecolor_entry = ttk.Entry(master=outline_edit_frame, width=7,
                                    textvariable=self.outline_facecolor_var)
        facecolor_label.grid(row=3, column=0)
        facecolor_entry.grid(row=3, column=1)
        edgecolor_label = ttk.Label(master=outline_edit_frame, text="edgecolor")
        edgecolor_entry = ttk.Entry(master=outline_edit_frame, width=7,
                                    textvariable=self.outline_edgecolor_var)
        edgecolor_label.grid(row=3, column=2)
        edgecolor_entry.grid(row=3, column=3)
        ## alpha and zorder
        # !!! turn into spinbox
        outline_alpha_entry = ttk.Entry(master=outline_edit_frame, width=7,
                                textvariable=self.outline_alpha_var)
        outline_alpha_label.grid(row=4, column=0)
        outline_alpha_entry.grid(row=4, column=1)
        outline_zorder_label = ttk.Label(master=outline_edit_frame, text="z-order")
        # !!! turn into spinbox
        outline_zorder_entry = ttk.Entry(master=outline_edit_frame, width=7,
                                    textvariable=self.outline_zorder_var)
        outline_zorder_label.grid(row=4, column=2)
        outline_zorder_entry.grid(row=4, column=3)

        # notch frame
        notch_edit_frame = ttk.Labelframe(master=frames["outline"], text="notch parameters")
        notch_edit_frame.grid(row=2,column=0,sticky="NEWS")
        ## notch enable/disable
        notch_enable_label = ttk.Label(master=notch_edit_frame, text="enable")
        notch_enable = ttk.Radiobutton(master=notch_edit_frame, value=True,text="yes",variable=self.notch_enable_var,
                                        command=lambda: self.refresh_wafflemap())
        notch_disable = ttk.Radiobutton(master=notch_edit_frame, value=False,text="no",variable=self.notch_enable_var,
                                        command=lambda: self.refresh_wafflemap())
        notch_enable_label.grid(row=0,column=0,sticky="NEWS")
        notch_enable.grid(row=0,column=1,sticky="NEWS")
        notch_disable.grid(row=0,column=2,sticky="NEWS")
        ## notch type radiobutton
        notch_type_label = ttk.Label(master=notch_edit_frame, text="type")
        notch_type_f = ttk.Radiobutton(master=notch_edit_frame, value="f",text="flat",variable=self.notch_type_var,
                                       command=lambda: self.refresh_wafflemap())
        notch_type_c = ttk.Radiobutton(master=notch_edit_frame, value="c",text="circle",variable=self.notch_type_var,
                                       command=lambda: self.refresh_wafflemap())
        notch_type_e = ttk.Radiobutton(master=notch_edit_frame, value="e",text="ellipse",variable=self.notch_type_var,
                                       command=lambda: self.refresh_wafflemap())
        notch_type_label.grid(row=1,column=0,sticky="NEWS")
        notch_type_f.grid(row=1,column=1,sticky="NEWS")
        notch_type_c.grid(row=1,column=2,sticky="NEWS")
        notch_type_e.grid(row=1,column=3,sticky="NEWS")
        ## notch direction radiobutton
        notch_dir_label = ttk.Label(master=notch_edit_frame, text="side")
        notch_dir_N = ttk.Radiobutton(master=notch_edit_frame, value="N",text="N",variable=self.notch_dir_var,
                                      command=lambda: self.refresh_wafflemap())
        notch_dir_S = ttk.Radiobutton(master=notch_edit_frame, value="S",text="S",variable=self.notch_dir_var,
                                      command=lambda: self.refresh_wafflemap())
        notch_dir_E = ttk.Radiobutton(master=notch_edit_frame, value="E",text="E",variable=self.notch_dir_var,
                                      command=lambda: self.refresh_wafflemap())
        notch_dir_W = ttk.Radiobutton(master=notch_edit_frame, value="W",text="W",variable=self.notch_dir_var,
                                      command=lambda: self.refresh_wafflemap())
        notch_dir_label.grid(row=2,column=0,sticky="NEWS")
        notch_dir_N.grid(row=2,column=1,sticky="NEWS")
        notch_dir_S.grid(row=2,column=2,sticky="NEWS")
        notch_dir_E.grid(row=2,column=3,sticky="NEWS")
        notch_dir_W.grid(row=2,column=4,sticky="NEWS")
        ## notch size
        notch_size_label = ttk.Label(master=notch_edit_frame, text="size")
        notch_size_spinbox = ttk.Spinbox(master=notch_edit_frame, width=6,
                                        from_=0.1, to=10, increment=0.5,
                                        textvariable=self.notch_size_var,
                                        command=lambda: self.refresh_wafflemap())
        notch_size_label.grid(row=3, column=0,sticky="NEWS")
        notch_size_spinbox.grid(row=3, column=1,sticky="NEWS")

        ### Format frames to make them less tight
        for child in frames["outline"].winfo_children():
            child.grid_configure(padx=5, pady=5)
            for grandchild in child.winfo_children():
                grandchild.grid_configure(padx=5, pady=2)
############################################################################################################################
### BOTTOM BUTTONS
        bottom_buttons_frame=ttk.Frame(master=self.ui_frame)
        bottom_buttons_frame.grid(row=10,column=0)
        reset_button=ttk.Button(master=bottom_buttons_frame, text="SAVE MAP", command=lambda: self.save_wafflemap())
        reset_button.grid(row=0,column=0, sticky="E")
        plotbutton=ttk.Button(master=bottom_buttons_frame, text="REFRESH", command=lambda: self.refresh_wafflemap())
        plotbutton.grid(row=0,column=1, sticky="E")
        savebutton=ttk.Button(master=bottom_buttons_frame, text="SAVE FIG", command=lambda: self.save_wafflemap_image())
        savebutton.grid(row=0,column=2, sticky="W")
        print_df_button=ttk.Button(master=bottom_buttons_frame, text="PRINT DF", command=lambda: self.print_df())
        print_df_button.grid(row=0,column=3, sticky="W")
        print_label_df_button=ttk.Button(master=bottom_buttons_frame, text="PRINT LABELS", command=lambda: self.print_label_df())
        print_label_df_button.grid(row=0,column=4, sticky="W")
        self.on_figure = False
        self.fig_frame.bind("<Enter>", lambda c: self.set_on_figure_True())
        self.fig_frame.bind("<Leave>", lambda c: self.set_on_figure_False())
        root.bind('<Button-1>', lambda c: self.left_click_edit_die(c.x,c.y))
        root.bind('<Button-2>', lambda c: self.right_click_edit_die(c.x,c.y))
        root.bind('<Button-3>', lambda c: self.right_click_edit_die(c.x,c.y))
        self.fig_frame.bind('<Button-1>', lambda c: self.edit_die(c.x,c.y))

# END INIT
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
##############################################################################################################
# METHODS

    def left_click_edit_die(self, clickx, clicky):
        if self.on_figure:
            if self.ui_nb.index(self.ui_nb.select()) == 1:
                if self.edit_choice.get() == 1:
                    self.click_addrem_die(clickx, clicky)
                elif self.edit_choice.get() == 2:
                    self.click_color_die(clickx, clicky)
                elif self.edit_choice.get() == 3:
                    self.click_hatch_die(clickx, clicky)
                elif self.edit_choice.get() == 4:
                    self.click_label_die(clickx, clicky)
            if self.ui_nb.index(self.ui_nb.select()) == 2:
                if self.addrem_click_label.get() == 1:
                    self.click_label_die(clickx, clicky)
                elif self.addrem_click_label.get() == 2:
                    self.click_remove_label(clickx, clicky)

    def right_click_edit_die(self, clickx, clicky):
        if self.on_figure:
            if self.ui_nb.index(self.ui_nb.select()) == 1:
                if self.edit_choice.get() == 4:
                    self.click_remove_label(clickx, clicky)


    def click_addrem_die(self, clickx, clicky):
        detected_die = self.die_detect(clickx, clicky)
        if detected_die.empty:
            print("Die out of range. Increase the range and try again")
        else:
            # print(f"detected die : {detected_die}")
            # print("corresponding plot coords", detected_die[["plotx","ploty"]].values)
            if detected_die.in_wafer.values:
                print(f"Deleted die {detected_die.iloc[0]['x']}, {detected_die.iloc[0]['y']}")
                self.remove_die(*detected_die.iloc[0][["x","y"]])
            else:
                print(f"Added die {detected_die.iloc[0]['x']}, {detected_die.iloc[0]['y']}")
                self.add_die(*detected_die.iloc[0][["x","y"]])
        self.refresh_wafflemap()

    def click_color_die(self, clickx, clicky):
        detected_die = self.die_detect(clickx, clicky)
        color = self.color_die_entry.get()
        if not detected_die.empty:
            if len(color) == 0:
                color = 'none'
            print(f"color {detected_die.iloc[0]['x']}, {detected_die.iloc[0]['y']} {color}")
            self.set_color(detected_die.iloc[0]["x"], detected_die.iloc[0]["y"], color)
        self.refresh_wafflemap()

    def click_hatch_die(self, clickx, clicky):
        detected_die = self.die_detect(clickx, clicky)
        hatch = self.hatch_die_entry.get()
        if not detected_die.empty:
            print(f"hatch {detected_die.iloc[0]['x']}, {detected_die.iloc[0]['y']} {hatch}")
            self.set_hatch(detected_die.iloc[0]["x"], detected_die.iloc[0]["y"], hatch)
        self.refresh_wafflemap()

    def click_remove_label(self, clickx, clicky):
        detected_die = self.die_detect(clickx, clicky)
        self.remove_label_die(detected_die.iloc[0]["x"], detected_die.iloc[0]["y"])
        self.refresh_wafflemap()

    def click_label_die(self, clickx, clicky):
        detected_die = self.die_detect(clickx, clicky)
        self.label_die(detected_die.iloc[0]["x"], detected_die.iloc[0]["y"],
                        label=self.label_text.get(), loc=self.loc_dict[self.label_loc_var.get()],
                        fontsize=float(self.label_fontsize.get()),
                        verbose=True)
        self.refresh_wafflemap()

    def die_detect(self, clickx, clicky):
        fig_width, fig_height = self.fig.get_size_inches()*self.fig.dpi
        [x, y] = self.ax.transData.inverted().transform([clickx,fig_height-clicky]) # invert y-coord cuz figure origin is up but data origin is down
        df = self.df
        die_width = self.die_width
        die_height = self.die_height
        detected_die = df[(df.plotx<x) & (df.plotx+die_width>x) & (df.ploty<y) & (df.ploty+die_height>y)]
        #print(detected_die)
        return detected_die

    def resize_figure(self):
        # make it so that the window is resized according to the fiigure's width and height
        new_width = self.im_width.get()
        new_height = self.im_height.get()
        print(f"setting figure size to {new_width}x{new_height}")

        if new_width and new_height:
            root.geometry(f"{2*int(new_width)}x{new_height}")
            curr_width, curr_height = self.fig.get_size_inches()*self.fig.dpi
            # cur_aspect_ratio = curr_width/curr_height
        return
    
    def rerange_wafflemap(self):
        try:
            xmin= int(self.die_rangex_min.get())
            xmax= int(self.die_rangex_max.get())
            ymin= int(self.die_rangey_min.get())
            ymax= int(self.die_rangey_max.get())
        except Exception as e:
            print("invalid values:",e)
            return

        self.x_range = np.array([xmin, xmax])
        self.y_range = np.array([ymin, ymax])
        print(f"die ranges set to X{self.x_range}, Y{self.y_range}")
        self.init_die_df()
        self.refresh_wafflemap()

    def flip_wafflemap(self):
        try:
            v_flip = self.vflip_var.get()
            h_flip = self.hflip_var.get()
        except Exception as e:
            print("invalid values:",e)
            return
        self.v_flip = v_flip
        self.h_flip = h_flip
        self.init_dies()
        self.refresh_wafflemap()

    def draw_default_wafflemap(self):
        self.plot_dies(die_coord_on_axis={"enable":False,
                                     "fontsize": 10,
                                     "offset":1,
                                     "left":True,
                                     "right":True,
                                     "top":True,
                                     "bottom": True})
        margin=0.4
        self.fig.subplots_adjust(left=margin,
                                bottom=margin, 
                                right=1-margin, 
                                top=1-margin)
        if self.notch_config["enable"]:
            notch_side = self.notch_config["side"]
        else:
            notch_side = None
        new_radius=self.plot_wafer_outline(radius=None, # calculate radius based on dies
                                           x_offset=self.fig_params["wafer_xoffset"],
                                           y_offset=self.fig_params["wafer_yoffset"],
                                           facecolor=self.outline_config["facecolor"],
                                           edgecolor=self.outline_config["edgecolor"],
                                           linewidth=self.outline_config["linewidth"],
                                           notch=notch_side, 
                                           notch_type=self.notch_config["type"],
                                           notch_size=self.notch_config["size"],
                                           verbose=False)
        self.outline_config["radius"] = new_radius
        self.plot_all_labels()
        self.canvas.draw()

    def refresh_wafflemap(self):
        self.ax.cla()
        self.plot_dies(die_coord_on_axis={"enable":self.diexy_onaxis_var.get(),
                                     "fontsize": self.diexy_onaxis_size_var.get(),
                                     "offset":self.diexy_onaxis_offset_var.get(),
                                     "left":True,
                                     "right":True,
                                     "top":True,
                                     "bottom": True})
        if self.notch_enable_var.get():
            notch_side = self.notch_dir_var.get()
        else:
            notch_side = None
            
        if self.outline_enable_var.get() == True:
            self.plot_wafer_outline(radius=self.outline_size_var.get(),
                                   x_offset=self.outline_xoffset_var.get(),
                                   y_offset=self.outline_yoffset_var.get(),
                                   facecolor=self.outline_facecolor_var.get(),
                                   edgecolor=self.outline_edgecolor_var.get(),
                                   linewidth=self.linewidth_var.get(),
                                   notch=notch_side, 
                                   notch_type=self.notch_type_var.get(),
                                   notch_size=self.notch_size_var.get(),
                                   verbose=False)
        self.plot_all_labels()
        margin=0.2
        self.fig.subplots_adjust(left=margin,
                                bottom=margin, 
                                right=1-margin, 
                                top=1-margin)

        self.canvas.draw()

    def apply_label_to_all(self):
        for x,y in self.df.xy:
            self.label_die(x, y,
                        label=self.label_text.get(), loc=self.loc_dict[self.label_loc_var.get()],
                        fontsize=float(self.label_fontsize.get()),
                        verbose=True)
        self.refresh_wafflemap()

    def remove_all_labels(self):
        self.label_df = self.label_df.iloc[0:1]
        self.refresh_wafflemap()

    def toggle_diexy_onaxis(self):

    #     if self.diexy_onaxis_var:
    #         self.ax.set_axis_on()
    #         self.ax.spines['top'].set_visible(True)
    #         self.ax.spines['right'].set_visible(True)
    #         self.ax.spines['bottom'].set_visible(True)
    #         self.ax.spines['left'].set_visible(True)
    #         self.ax.tick_params(axis='both', which='major', direction="out",
    #                             labelsize=self.config["axis_labels"]["size"],
    #                             bottom=True, top=True, left=True, right=True,
    #                             labelbottom=True, labeltop=True, labelleft=True, labelright=True)
    #         plotx_list = self.df.plotx.drop_duplicates()+self.die_width/2
    #         ploty_list = self.df.ploty.drop_duplicates()+self.die_height/2
    #         diex_list = self.df.x.drop_duplicates().astype(str)
    #         diey_list = self.df.y.drop_duplicates().astype(str)
    #         self.ax.xaxis.set_ticks(plotx_list, diex_list)
    #         self.ax.yaxis.set_ticks(ploty_list, diey_list)
    #         self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)

    #     else:
    #         # remove axes and ticks
    #         self.ax.set_axis_off()
    #         self.ax.xaxis.set_visible(False)
    #         self.ax.yaxis.set_visible(False)
    #         # remove figure frame
    #         self.ax.spines['top'].set_visible(False)
    #         self.ax.spines['right'].set_visible(False)
    #         self.ax.spines['bottom'].set_visible(False)
    #         self.ax.spines['left'].set_visible(False)

        self.refresh_wafflemap()

    def set_on_figure_True(self):
        self.on_figure = True
        # print(f"on figure value: {self.on_figure}")

    def set_on_figure_False(self):
        self.on_figure = False
        # print(f"on figure value: {self.on_figure}")
        
    def load_gui_values_to_config(self):
        pass

    def save_wafflemap(self):
        print(self.config)
        filename = tk.filedialog.asksaveasfilename()
        if filename == '':
            print("canceled")
            return
        else:
            self.load_gui_values_to_config()
            with open(filename, "w") as f:
                json.dump(self.config , f, indent=4) 
        return

    def save_wafflemap_image(self):
        filename = tk.filedialog.asksaveasfilename()
        if filename == '':
            print("canceled")
            return
        saved_filename = self.save_image(filename = filename)
        print("image saved at", saved_filename)
        return

    def print_df(self):
        # option context est utlisé ici pour enlever la limite de 
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(self.df)

    def print_label_df(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(self.label_df)

root=tk.Tk()
gui = WafflemapGUI(root)
root.mainloop()