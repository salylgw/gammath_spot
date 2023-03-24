# Author: Salyl Bhagwat, Gammath Works
# Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = 'Salyl Bhagwat'
__copyright__ = 'Copyright (c) 2021-2023, Salyl Bhagwat, Gammath Works'

from tkinter import *
from tkinter import ttk
import threading, queue
import os
try:
    from gammath_spot import gammath_utils as gut
except:
    import gammath_utils as gut

class Gammath_SPOT_GUI:

    def __init__(self):
        self.tool_if_thread = None
        self.msg_queue = queue.Queue()
        self.scraper_pb = None
        self.scorer_pb = None
        self.projector_pb = None
        self.historian_pb = None
        self.backtester_pb = None
        self.screener_pb = None
        self.curr_watchlist = None

        #Root window
        self.root = Tk()

        #Disable window resizing
        self.root.resizable(FALSE, FALSE)

        #Disable tear-off menus
        self.root.option_add('*tearOff', FALSE)

        #Set title for the main window
        self.root.title("Gammath SPOT")

        #Get the path of program/package
        pgm_dir_path, fn = os.path.split(__file__)

        #Append the data dir
        pgm_data_path = os.path.join(pgm_dir_path, 'data')

        #Read the logo
        self.logo_image = PhotoImage(file=f'{pgm_data_path}/logo.png')

        #Add menus
        self.add_menus()

        #Keep pixels per inch count for setting widget dimensions
        self.pixels_per_inch=self.root.winfo_pixels('1i')

        #Create canvas for logo
        self.create_canvas()

        #Add logo after canvas appears on the screen (to get actual dimensions)
        self.canvas.after(5, lambda: self.add_logo())

        #Add the app frame
        self.add_app_frame()

        #Start the event loop
        self.root.mainloop()

    def get_canvas_dimensions_in_inches(self):
        return 8, 1.2

    def get_app_frame_dimensions_in_inches(self):
        return 8, 8

    def load_watchlist(self, wl_name):
        self.curr_watchlist = wl_name

        #Placeholder to show the watchlist content

    def save_watchlist(self):
        wl_name = self.curr_watchlist

        #Placeholder to update current watchlist

    def save_watchlist_as(self, wl_name):
        #Check if there was a name entered
        if (len(wl_name)):
            self.curr_watchlist = wl_name

        #Placeholder to update current watchlist

        #Destroy the window
        self.wl_name_window.destroy()

    def get_save_as_watchlist_name(self):

        #Create a window for watchlist name entry
        self.wl_name_window = Toplevel(self.app_frame)

        #Disable window resizing
        self.wl_name_window.resizable(FALSE, FALSE)

        #Save As
        self.wl_name_window.title('Save Watchlist As')

        #Create a frame for dialog
        self.dialog_frame = ttk.Frame(self.wl_name_window)
        self.dialog_frame.grid(row=0, column=0)

        #Prompt user to enter watchlist name
        self.wl_dialog_label = ttk.Label(self.dialog_frame, text="Enter watchlist name:")
        self.wl_dialog_label.grid(row=1, column=0)

        #Entry widget to enter text
        wl_name = StringVar()

        wl_name_entry = ttk.Entry(self.dialog_frame, width=30, textvariable=wl_name)
        wl_name_entry.grid(row=2, column=0)

        #Add a cancel button
        wl_name_cancel_button = ttk.Button(self.dialog_frame, text="Cancel", command=lambda: self.wl_name_window.destroy())

        #Place it under the entry widget
        wl_name_cancel_button.grid(row=3, column=0, sticky=(N, S))

        #Add OK button
        #Pass in the entered text
        wl_name_ok_button = ttk.Button(self.dialog_frame, text="OK", command=lambda: self.save_watchlist_as(wl_name.get()))

        #Place it next to cancel button
        wl_name_ok_button.grid(row=3, column=0, sticky=(E))


    def add_menus(self):
        self.menubar = Menu(self.root)
        self.root['menu'] = self.menubar

        #Item for watchlist
        self.menu_wl = Menu(self.menubar)

        #Item for About
        self.menu_about = Menu(self.menubar)

        #Watchlist menu item details
        self.menubar.add_cascade(menu=self.menu_wl, label='Watchlist')
        self.menu_wl.add_command(label='Create Watchlist')
        self.menu_wls = Menu(self.menu_wl)
        self.menu_wl.add_cascade(menu=self.menu_wls, label='Load Watchlist')

        #Init list of existing watchlists
        self.wl_fp_list = gut.get_watchlist_list()

        #Show list of existing watchlists
        if (len(self.wl_fp_list)):
            for f in self.wl_fp_list:
                self.menu_wls.add_command(label=(os.path.basename(f).split('.')[0]), command=lambda f=f: self.load_watchlist(f))
        else:
            self.menu_wl.entryconfigure('Load Watchlist', state=DISABLED)

        #Placeholder for saving watchlist
        self.menu_wl.add_command(label='Save Watchlist', command=self.save_watchlist)
        #Placeholder for saving watchlist
        self.menu_wl.add_command(label='Save Watchlist As', command=self.get_save_as_watchlist_name)

        #Placeholder to show info
        self.menubar.add_cascade(menu=self.menu_about, label='About')
        self.menu_about.add_command(label='(c) Gammath Works\nhttps://www.gammathworks.com')

    def create_canvas(self):

        width_in_inches, height_in_inches = self.get_canvas_dimensions_in_inches()

        #Convert inches into number of pixels
        self.canvas_width_in_pixels = (width_in_inches*self.pixels_per_inch)
        self.canvas_height_in_pixels = (height_in_inches*self.pixels_per_inch)

        #Create and position the canvas
        self.canvas = Canvas(self.root, width=self.canvas_width_in_pixels, height=(height_in_inches*self.pixels_per_inch), background='white', borderwidth = 3, relief='solid')
        self.canvas.grid(column=0, row=0)

    def add_logo(self):
        #Get the logo image dimensions
        image_width = self.logo_image.width()
        image_height = self.logo_image.height()

        #Derive coordinates based on actual width and height of canvas
        x_coord = (self.canvas.winfo_width()/2)
        y_coord = (self.canvas.winfo_height()/2)

        #Add logo in the middle of the canvas
        self.canvas.create_image(x_coord, y_coord, image=self.logo_image)

    def add_app_frame(self):
        #Get app frame dimensions
        width_in_inches, height_in_inches = self.get_app_frame_dimensions_in_inches()

        #Convert dimensions into number of pixels
        self.app_frame_width_in_pixels = (width_in_inches*self.pixels_per_inch)
        self.app_frame_height_in_pixels = (height_in_inches*self.pixels_per_inch)

        #Create app frame to hold the widgets
        self.app_frame = ttk.Frame(self.root, width=self.app_frame_width_in_pixels, height=self.app_frame_height_in_pixels, padding=5)
        self.app_frame.grid()

    def gui_tool_if(self, msg_queue):

        progress_data = 0
        while (TRUE):
            msg = msg_queue.get()
            try:
                tool = msg['Tool']
                if (tool == 'Scraper'):
                    pb = self.scraper_pb
                elif (tool == 'Scorer'):
                    pb = self.scorer_pb
                elif (tool == 'Projector'):
                    pb = self.projector_pb
                elif (tool == 'Historian'):
                    pb = self.historian_pb
                elif (tool == 'Backtester'):
                    pb = self.backtester_pb
                elif (tool == 'Screener'):
                    pb = self.screener_pb

                if (progress_data == 0):
                    pb.stop()
                    pb['mode'] = 'determinate'

                progress_data = msg['PD']
                pb['value'] = progress_data
                if ((progress_data == pb['maximum']) or (progress_data == 0)):
                    msg_queue.task_done()
                    return
                else:
                    msg_queue.task_done()
            except:
                msg_queue.task_done()
                return

    def launch_gui_tool_if_thread(self, tool, msg_queue):
        self.gui_tool_if_thread = threading.Thread(name=f'GUI_{tool}_thread', target=self.gui_tool_if, args=(msg_queue,))
        self.gui_tool_if_thread.start()

def main():
    #Start/Instantiate GUI. Won't return until app is closed
    Gammath_SPOT_GUI()

if __name__ == '__main__':
    main()
