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
import pandas as pd
try:
    from gammath_spot import gammath_utils as gut
    from gammath_spot import gammath_stocks_data_scraper as gsds
    from gammath_spot import gammath_stocks_analyzer_and_scorer as gsas
    from gammath_spot import gammath_stocks_pep as gspep
    from gammath_spot import gammath_stocks_gscores_historian as gsgh
    from gammath_spot import gammath_stocks_backtesting as gsbt
    from gammath_spot import gammath_stocks_screener as gssc
except:
    import gammath_utils as gut
    import gammath_stocks_data_scraper as gsds
    import gammath_stocks_analyzer_and_scorer as gsas
    import gammath_stocks_pep as gspep
    import gammath_stocks_gscores_historian as gsgh
    import gammath_stocks_backtesting as gsbt
    import gammath_stocks_screener as gssc

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
        self.wl_fp_list = gut.get_watchlist_list()
        if (len(self.wl_fp_list)):
            self.curr_watchlist = self.wl_fp_list[0]
            self.curr_watchlist_len = len(pd.read_csv(self.curr_watchlist))
        else:
            self.curr_watchlist = None
            self.curr_watchlist_len = 0
        self.curr_screener = None
        self.starting_row_for_app_frame = 2

        #Root window
        self.root = Tk()

        #Disable window resizing
        self.root.resizable(FALSE, FALSE)

        #Disable tear-off menus
        self.root.option_add('*tearOff', FALSE)

        #Set title for the main window
        self.root.title("Gammath SPOT")

        #Keep pixels per inch count for setting widget dimensions
        self.pixels_per_inch=self.root.winfo_pixels('1i')

        #Get the path of program/package
        pgm_dir_path, fn = os.path.split(__file__)

        #Append the data dir
        pgm_data_path = os.path.join(pgm_dir_path, 'data')

        #Read the logo
        self.logo_image = PhotoImage(file=f'{pgm_data_path}/logo.png')

        #Add menus
        self.add_menus()

        #Create canvas for logo
        self.create_canvas()

        #Add logo after canvas appears on the screen (to get actual dimensions)
        self.canvas.update_idletasks()
        self.add_logo()

        #Add the app frame
        self.add_app_frame()

        #Add tools buttons and progress bars
        self.add_tool_buttons_and_progress_bars()

        #Start the event loop
        self.root.mainloop()

    def get_canvas_dimensions_in_inches(self):
        return 8, 1.2

    def get_app_frame_dimensions_in_inches(self):
        return 8, 8

    def get_progress_bar_len_in_pixels(self):
        return 200

    def load_watchlist(self, wl_name):
        self.curr_watchlist = wl_name

        #Placeholder to show the watchlist content

    def save_watchlist(self):
        if (self.curr_watchlist == None):
            self.get_save_as_watchlist_name()

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
        self.wl_dialog_label.grid(row=1, column=0, columnspan=2)

        #Entry widget to enter text
        wl_name = StringVar()

        wl_name_entry = ttk.Entry(self.dialog_frame, width=30, textvariable=wl_name)
        wl_name_entry.grid(row=2, column=0, columnspan=2)

        #Add a cancel button
        wl_name_cancel_button = ttk.Button(self.dialog_frame, text="Cancel", command=lambda: self.wl_name_window.destroy())

        #Place it under the entry widget
        wl_name_cancel_button.grid(row=3, column=0, sticky=(E))

        #Add OK button
        #Pass in the entered text
        wl_name_ok_button = ttk.Button(self.dialog_frame, text="OK", command=lambda: self.save_watchlist_as(wl_name.get()))

        #Place it next to cancel button
        wl_name_ok_button.grid(row=3, column=1, sticky=(W))

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

        #Init list of latest existing watchlists
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
        self.canvas = Canvas(self.root, width=self.canvas_width_in_pixels, height=self.canvas_height_in_pixels, background='white', borderwidth = 3, relief='solid')

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
        self.app_frame.grid(row=self.starting_row_for_app_frame, column=0)

    def add_tool_buttons_and_progress_bars(self):
        #Add Scraper tool button
        curr_row = (self.starting_row_for_app_frame + 1)
        self.scraper_button = ttk.Button(self.app_frame, text="Scraper", command=self.invoke_scraper)
        self.scraper_button.grid(row=curr_row, column=0)

        #Progress bar for Scraper run
        curr_row += 1
        self.scraper_pb = ttk.Progressbar(self.app_frame, orient=HORIZONTAL, length=self.get_progress_bar_len_in_pixels(), maximum=self.curr_watchlist_len, mode='indeterminate')
        self.scraper_pb.grid(row=curr_row, column=0)

        #Add Analyzer and Scorer tool buttons
        curr_row += 1
        self.scorer_button = ttk.Button(self.app_frame, text="Scorer", command=self.invoke_scorer)
        self.scorer_button.grid(row=curr_row, column=0)

        #Progress bar for Analyzer/Scorer run
        curr_row += 1
        self.scorer_pb = ttk.Progressbar(self.app_frame, orient=HORIZONTAL, length=self.get_progress_bar_len_in_pixels(), maximum=self.curr_watchlist_len, mode='indeterminate')
        self.scorer_pb.grid(row=curr_row, column=0)

        #Add Projector tool button
        curr_row += 1
        self.projector_button = ttk.Button(self.app_frame, text="Projector", command=self.invoke_projector)
        self.projector_button.grid(row=curr_row, column=0)

        #Progress bar for Projector run
        curr_row += 1
        self.projector_pb = ttk.Progressbar(self.app_frame, orient=HORIZONTAL, length=self.get_progress_bar_len_in_pixels(), maximum=(self.curr_watchlist_len+1), mode='indeterminate')
        self.projector_pb.grid(row=curr_row, column=0)

        #Add Historian tool
        curr_row += 1
        self.historian_button = ttk.Button(self.app_frame, text="Historian", command=self.invoke_historian)
        self.historian_button.grid(row=curr_row, column=0)

        #Progress bar for Historian run
        curr_row += 1
        self.historian_pb = ttk.Progressbar(self.app_frame, orient=HORIZONTAL, length=self.get_progress_bar_len_in_pixels(), maximum=self.curr_watchlist_len, mode='indeterminate')
        self.historian_pb.grid(row=curr_row, column=0)

        #Add Backtester tool button
        curr_row += 1
        self.backtester_button = ttk.Button(self.app_frame, text="Backtester", command=self.invoke_backtester)
        self.backtester_button.grid(row=curr_row, column=0)

        #Progress bar for Backtester run
        curr_row += 1
        self.backtester_pb = ttk.Progressbar(self.app_frame, orient=HORIZONTAL, length=self.get_progress_bar_len_in_pixels(), maximum=self.curr_watchlist_len, mode='indeterminate')
        self.backtester_pb.grid(row=curr_row, column=0)

        #Add Screener tool button
        curr_row += 1
        self.screener_button = ttk.Button(self.app_frame, text="Screener", command=self.invoke_screener)
        self.screener_button.grid(row=curr_row, column=0)

        #Progress bar for Screener run
        curr_row += 1
        self.screener_pb = ttk.Progressbar(self.app_frame, orient=HORIZONTAL, length=self.get_progress_bar_len_in_pixels(), mode='indeterminate')
        self.screener_pb.grid(row=curr_row, column=0)

        #Update screen
        self.app_frame.update_idletasks()

    def update_all_buttons_state(self, state):
        #Disable or Enable
        if (state == 'disable'):
            state_value = 'disabled'
        else:
            state_value = '!disabled'

        #Set the desired state
        self.scraper_button.state([state_value])
        self.scorer_button.state([state_value])
        self.projector_button.state([state_value])
        self.historian_button.state([state_value])
        self.backtester_button.state([state_value])
        self.screener_button.state([state_value])

    def get_tool_progress_bar(self, tool):
        #Get progress bar corresponding to the tool
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

        return pb

    def set_buttons_pb_state(self, tool):
        #Disable other invokations
        self.update_all_buttons_state('disable')

        #Get the progress bar
        pb = self.get_tool_progress_bar(tool)

        #Set initial value to 0
        pb['value'] = 0

        #Keep mode to be indeterminate until the final item is done
        pb['mode'] = 'indeterminate'

        #Start the progress bar
        pb.start()

    def invoke_scraper(self):

        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Scraper')

        #Launch GUI interface thread for Scraper tool
        self.launch_gui_tool_if_thread('Scraper', self.msg_queue)

        #Launch Scraper tool thread
        self.gscraper = gsds.GSCRAPER()
        self.gscraper.launch_scraper_thread(self.curr_watchlist, self.msg_queue)

    def invoke_scorer(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Scorer')

        #Launch GUI interface thread for Scorer tool
        self.launch_gui_tool_if_thread('Scorer', self.msg_queue)

        #Launch Analyzer/Scorer tool thread
        self.gscorer = gsas.GSCORER()
        self.gscorer.launch_analyzer_and_scorer_thread(self.curr_watchlist, self.msg_queue)


    def invoke_projector(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Projector')

        #Launch GUI interface thread for Projector tool
        self.launch_gui_tool_if_thread('Projector', self.msg_queue)

        #Launch Projector tool thread
        self.gprojector = gspep.GPROJECTOR()
        self.gprojector.launch_projector_thread(self.curr_watchlist, self.msg_queue)

    def invoke_historian(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Historian')

        #Launch GUI interface thread for Historian tool
        self.launch_gui_tool_if_thread('Historian', self.msg_queue)

        #Launch Historian tool thread
        self.ghistorian = gsgh.GHISTORIAN()
        self.ghistorian.launch_historian_thread(self.curr_watchlist, self.msg_queue)

    def invoke_backtester(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Backtester')

        #Launch GUI interface thread for Backtester tool
        self.launch_gui_tool_if_thread('Backtester', self.msg_queue)

        #Launch Backtester tool thread
        self.gbacktester = gsbt.GBACKTESTER()
        self.gbacktester.launch_backtester_thread(self.curr_watchlist, self.msg_queue)

    def invoke_screener(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Screener')

        #Launch GUI interface thread for Screener tool
        self.launch_gui_tool_if_thread('Screener', self.msg_queue)

        #Launch Screener tool thread
        self.gscreener = gssc.GSCREENER()
        self.gscreener.launch_screener_thread(self.curr_screener, self.msg_queue)

    def gui_tool_if(self, msg_queue):

        progress_data = 0
        while (TRUE):
            msg = msg_queue.get()
            try:
                tool = msg['Tool']
                pb = self.get_tool_progress_bar(tool)
                progress_data = msg['PD']
                if ((progress_data == pb['maximum']) or (progress_data == 0)):
                    pb.stop()
                    #Show actual completion in the progress bar
                    pb['mode'] = 'determinate'
                    pb['value'] = progress_data
                    #Re-enable all tools buttons
                    self.update_all_buttons_state('enable')
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
