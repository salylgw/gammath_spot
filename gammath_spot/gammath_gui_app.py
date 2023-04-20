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
from tkinter import font
from tkinter import filedialog
import threading, queue
import os
from pathlib import Path
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
        self.gui_tool_if_thread = None
        self.gscraper = None
        self.gscorer = None
        self.gprojector = None
        self.ghistorian = None
        self.gbacktester = None
        self.gscreener = None

        #Revisit if/when scrollbar works well
        self.MAX_WL_ENTRIES = 12
        self.curr_watchlist = None
        self.curr_watchlist_len = 0
        self.wl_fp_list = gut.get_watchlist_list()

        if (len(self.wl_fp_list)):
            curr_watchlist = self.wl_fp_list[0]
            try:
                self.curr_watchlist_len = len(pd.read_csv(curr_watchlist))
                self.curr_watchlist = curr_watchlist
            except:
                print('Failed to read watchlist')

        #Check if screener info file exists
        screener_file = os.getcwd() + '/' + 'screener.csv'
        if (Path(screener_file).exists()):
            #Set screener to existing one
            self.curr_screener = screener_file
        else:
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

        #Save windowing system string for reference
        #Could be used for portability nuance
        self.windowing_system_string = self.root.tk.call('tk', 'windowingsystem')

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

        #Add watchlist widget
        self.add_watchlist_widget()

        #Load default watchlist (if any)
        self.load_watchlist(self.curr_watchlist)

        #Add a close button callback for main window
        #We want to check if any tool is running before closing GUI app
        self.root.protocol("WM_DELETE_WINDOW", self.checked_exit)

        #Start the event loop
        self.root.mainloop()

    def is_any_if_thread_alive(self):
        any_thread_alive = False
        tool = ''

        #Check if Tool IF thread is running
        if (self.gui_tool_if_thread_is_alive()):
            any_thread_alive = True

        #Check if Scraper is running
        if (self.gscraper != None):
            if (self.gscraper.scraper_thread_is_alive()):
                any_thread_alive = True
                tool = 'Scraper'

        #Check if Analyzer/Scorer is running
        if (self.gscorer != None):
            if (self.gscorer.analyzer_and_scorer_thread_is_alive()):
                any_thread_alive = True
                tool = 'Scorer'

        #Check if Projector is running
        if (self.gprojector != None):
            if (self.gprojector.projector_thread_is_alive()):
                any_thread_alive = True
                tool = 'Projector'

        #Check if Historian is running
        if (self.ghistorian != None):
            if (self.ghistorian.historian_thread_is_alive()):
                any_thread_alive = True
                tool = 'Historian'

        #Check if Backtester is running
        if (self.gbacktester != None):
            if (self.gbacktester.backtester_thread_is_alive()):
                any_thread_alive = True
                tool = 'Backtester'

        #Check if Screener is running
        if (self.gscreener != None):
            if (self.gscreener.screener_thread_is_alive()):
                any_thread_alive = True
                tool = 'Screener'

        return any_thread_alive, tool

    def show_tool_running_message(self, tool):
        #Create a window for screener info entry
        self.tool_running_msg_window = Toplevel(self.app_frame)

        #Disable window resizing
        self.tool_running_msg_window.resizable(FALSE, FALSE)

        #Give a title to the window
        self.tool_running_msg_window.title('Active run')

        #Create a frame for showing active tool msg
        self.tool_running_frame = ttk.Frame(self.tool_running_msg_window, padding=10)
        self.tool_running_frame.grid(row=0, column=0, rowspan=3)
        curr_row_num = 1

        #Label with helpful text
        #For now suggest closing console window that launched this GUI
        self.tool_running_label = ttk.Label(self.tool_running_frame, text=f'{tool} is still running.\nExiting the app in the middle can cause undesired results.\nIf you must exit then please close the window from which this app was launched.', font=self.app_frame_label_font)
        self.tool_running_label.grid(row=curr_row_num, column=0)

    def checked_exit(self):
        #Check if any tools is running
        alive, tool = self.is_any_if_thread_alive()

        #If none running then okay to close this app
        if (alive == False):
            #OK to close the GUI app
            self.root.destroy()
        else:
            #Show a message showing tool still active
            #Prompt msg that if the user must, just close the console window
            #from where this GUI was launched
            self.show_tool_running_message(tool)

    def get_canvas_dimensions_in_inches(self):
        return 8, 1.2

    def get_app_frame_dimensions_in_inches(self):
        return 8, 8

    def get_progress_bar_len_in_pixels(self):
        return 200

    def set_curr_watchlist(self, wl_name):
        #Setup all watchlist items for current watchlist
        self.curr_watchlist_len = 0
        wl_label = 'Watchlist. Save before using'

        self.curr_watchlist = wl_name

        if (wl_name != None):
            try:
                curr_watchlist_len = len(pd.read_csv(wl_name))
                self.curr_watchlist_len =  curr_watchlist_len
                loaded_wl_name = os.path.basename(wl_name).split('.')[0]
                #Update the label in watchlist widget
                wl_label = f'Watchlist Name: {loaded_wl_name}'
            except:
                print('Failed to set watchlist')

        self.wl_label_text.set(wl_label)

    def create_new_watchlist(self):
        #Disable all buttons until watchlist is saved
        self.update_all_buttons_state('disable')

        #Just clear up the watchist widget for new entries
        for i in range(self.MAX_WL_ENTRIES):
            self.table_entry[i].set('')

        #Reset watchlist label
        self.set_curr_watchlist(None)

    def load_watchlist(self, wl_name):
        #Load an existing watchlist
        if (wl_name != None):
            try:
                #Read the contents into dataframe
                df = pd.read_csv(wl_name)
                df_len = len(df)
                self.set_curr_watchlist(wl_name)

                #Fill up the table entries
                for i in range(min(df_len, self.MAX_WL_ENTRIES)):
                    self.table_entry[i].set(df.Symbol[i])

                #Keep remaining fields (if any) cleared
                if (df_len < self.MAX_WL_ENTRIES):
                    for i in range(df_len, self.MAX_WL_ENTRIES):
                        self.table_entry[i].set('')
            except:
                print('Failed to open watchlist file')

    def save_watchlist(self):

        if (self.curr_watchlist == None):
            #Need watchlist name
            self.get_save_as_watchlist_name()

        count = 0
        df = pd.DataFrame(columns=['Symbol'], index=range(self.MAX_WL_ENTRIES))
        for i in range(self.MAX_WL_ENTRIES):
            #Read the data from table
            sym = self.table_entry[i].get()
            if (sym != ''):
                df.Symbol[count] = sym
                count += 1

        if (count):
            try:
                #Save watchlist
                df.truncate(after=(count-1)).to_csv(self.curr_watchlist, index=False)
                #Set current watchlist to this watchlist
                self.set_curr_watchlist(self.curr_watchlist)
            except:
                print('Failed to save and set current watchlist')


    def save_watchlist_as(self, wl_name):
        #Check if there was a name entered
        if (len(wl_name)):
            #Convert the name to a full path filename
            self.curr_watchlist = os.getcwd() + '/' + wl_name + '.csv'

        #Save the contents to CSV file
        self.save_watchlist()

        #Delete old list of loadable watchlist
        self.menu_wls.delete(0, 'end')

        #Update loadable watchlist list
        self.update_loadable_watchlist_list()

        #Delete the window
        self.wl_name_window.destroy()

        self.update_all_buttons_state('enable')

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

    def update_loadable_watchlist_list(self):

        #Update watchlist file list to show in the menu
        #Init list of latest existing watchlists
        self.wl_fp_list = gut.get_watchlist_list()

        #Show list of existing watchlists
        if (len(self.wl_fp_list)):
            for f in self.wl_fp_list:
                self.menu_wls.add_command(label=(os.path.basename(f).split('.')[0]), command=lambda f=f: self.load_watchlist(f))
        else:
            self.menu_wl.entryconfigure('Load Watchlist', state=DISABLED)

    def add_screener_entry_widget(self, starting_row):
        #Widget to enter micro-gScore filtering criteria
        self.screener_entry = []
        self.screener_entry_handle = []

        #Check how many micro-gScores exist
        num_micro_gscores = len(gut.get_gscores_screening_df_columns())

        #Create a table for micro-gScore entry using the Entry widget
        for i in range(num_micro_gscores):
            #Input var
            self.screener_entry.append(StringVar())
            self.screener_entry_handle.append(ttk.Entry(self.screener_frame, width=5, textvariable=self.screener_entry[i]))
            self.screener_entry_handle[i].grid(row=starting_row+i, column=1)

    def save_screener_info(self):
        #Create a dataframe to read in the data from Entry widget
        df = pd.DataFrame(columns=gut.get_gscores_screening_df_columns(), index=range(1))

        #Fill the dataframe
        df.Price[0] = self.screener_entry[0].get()
        df.RSI[0] = self.screener_entry[1].get()
        df.BBANDS[0] = self.screener_entry[2].get()
        df.MACD[0] = self.screener_entry[3].get()
        df.KF[0] = self.screener_entry[4].get()
        df.OLS[0] = self.screener_entry[5].get()
        df.MFI[0] = self.screener_entry[6].get()
        df.Stoch[0] = self.screener_entry[7].get()
        df.Options[0] = self.screener_entry[8].get()
        df.Reco[0] = self.screener_entry[9].get()
        df.Senti[0] = self.screener_entry[10].get()

        #Only one screener file
        screener_info_file = os.getcwd() + '/' + 'screener.csv'

        try:
            #Save screener into a CSV file
            df.to_csv(screener_info_file, index=False)

            #Set the screener
            self.curr_screener = screener_info_file
        except:
            print('Failed to save and set current screener')

        #Remove the window
        self.screener_window.destroy()

    def add_screener_info_widget(self):
        #Create a window for screener info entry
        self.screener_window = Toplevel(self.app_frame)

        #Disable window resizing
        self.screener_window.resizable(FALSE, FALSE)

        #Give a title to the window
        self.screener_window.title('Screener')

        #Create a frame for micro-gScore filtering entries
        self.screener_frame = ttk.Frame(self.screener_window)
        self.screener_frame.grid(row=0, column=0, columnspan=2)
        curr_row_num = 1

        #Label with helpful text
        self.screener_main_label = ttk.Label(self.screener_frame, text='Enter micro-gScores screening info', font=self.app_frame_label_font)
        self.screener_main_label.grid(row=curr_row_num, column=0, padx=5, columnspan=2)

        curr_row_num += 1
        starting_row = curr_row_num

        #Create labels for each micro-gScore
        self.screener_price_label = ttk.Label(self.screener_frame, text='Price', font=self.app_frame_label_font)
        self.screener_price_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_rsi_label = ttk.Label(self.screener_frame, text='RSI', font=self.app_frame_label_font)
        self.screener_rsi_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_BB_label = ttk.Label(self.screener_frame, text='BB', font=self.app_frame_label_font)
        self.screener_BB_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_macd_label = ttk.Label(self.screener_frame, text='MACD', font=self.app_frame_label_font)
        self.screener_macd_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_kf_label = ttk.Label(self.screener_frame, text='KF', font=self.app_frame_label_font)
        self.screener_kf_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_ols_label = ttk.Label(self.screener_frame, text='OLS', font=self.app_frame_label_font)
        self.screener_ols_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_mfi_label = ttk.Label(self.screener_frame, text='MFI', font=self.app_frame_label_font)
        self.screener_mfi_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_stoch_label = ttk.Label(self.screener_frame, text='Stoch', font=self.app_frame_label_font)
        self.screener_stoch_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_od_label = ttk.Label(self.screener_frame, text='Options', font=self.app_frame_label_font)
        self.screener_od_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_reco_label = ttk.Label(self.screener_frame, text='Reco', font=self.app_frame_label_font)
        self.screener_reco_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1
        self.screener_senti_label = ttk.Label(self.screener_frame, text='Senti', font=self.app_frame_label_font)
        self.screener_senti_label.grid(row=curr_row_num, column=0)

        #Add widget to enter data
        self.add_screener_entry_widget(starting_row)

        curr_row_num += 1

        if (self.curr_screener != None):
            #Read in existing screener (if it exists)
            try:
                df = pd.read_csv(self.curr_screener)

                self.screener_entry[0].set(df.Price[0])
                self.screener_entry[1].set(df.RSI[0])
                self.screener_entry[2].set(df.BBANDS[0])
                self.screener_entry[3].set(df.MACD[0])
                self.screener_entry[4].set(df.KF[0])
                self.screener_entry[5].set(df.OLS[0])
                self.screener_entry[6].set(df.MFI[0])
                self.screener_entry[7].set(df.Stoch[0])
                self.screener_entry[8].set(df.Options[0])
                self.screener_entry[9].set(df.Reco[0])
                self.screener_entry[10].set(df.Senti[0])
            except:
                df = []

        #Add a cancel button
        wl_name_cancel_button = ttk.Button(self.screener_frame, text="Cancel", command=lambda: self.screener_window.destroy())

        #Place it under the label widgets
        wl_name_cancel_button.grid(row=curr_row_num, column=0, sticky=(E))

        #Add OK button
        wl_name_ok_button = ttk.Button(self.screener_frame, text="OK", command=self.save_screener_info)

        #Place it next to cancel button
        wl_name_ok_button.grid(row=curr_row_num, column=1, sticky=(W))

    def results_window_cleanup(self):
        #Cleanup the fields used for results widget
        del self.results_column_name_entry
        del self.results_column_name_entry_handle
        del self.results_column_value_entry
        del self.results_column_value_entry_handle

        #Remove the results window
        self.results_window.destroy()

    def add_results_info_widget(self):

        #Create a window for results info
        self.results_window = Toplevel(self.app_frame)

        #Add a cleanup function for results window
        self.results_window.protocol("WM_DELETE_WINDOW", self.results_window_cleanup)

        #Disable window resizing
        self.results_window.resizable(FALSE, FALSE)

        detailed_results_text = None

        #Get current watchlist name
        if (self.curr_watchlist == None):
            wl_text = 'None'
            detailed_results_dir = ''
        else:
            #Extract name of the watchlist
            wl_text = os.path.basename(self.curr_watchlist).split('.')[0]

            #Get full path to make it easier for use to locate the results dir
            detailed_results_dir = os.getcwd() + '/' + 'tickers'

        #Give a title to the window
        window_title = f'Results info for watchlist {wl_text}'
        self.results_window.title(window_title)

        #Create a frame for results entries
        self.results_frame = ttk.Frame(self.results_window)
        self.results_frame.grid(row=0, column=0, columnspan=5)

        #Create a widget to display overall gScore summary
        self.add_results_table_widget()

        #Get full path file name of overall gScores summary
        overall_results_file = detailed_results_dir + '/' + f'{wl_text}_overall_gscores.csv'

        try:
            df = pd.read_csv(overall_results_file)

            #We need the dataframe len for number of entries
            df_len = len(df)

            #Only show max entries until the scrollbar works well
            display_items_len = min(df_len, self.MAX_WL_ENTRIES)

            #Get columns info for the results
            results_main_columns = gut.get_gscores_results_df_columns()
            num_of_columns = len(results_main_columns)
            for i in range(num_of_columns):
                #Column index for entry placement
                column_name_index = (self.MAX_WL_ENTRIES*i)
                #Create a table for column values using the Entry widget
                for j in range(display_items_len):
                    #Input var
                    self.results_column_value_entry[column_name_index+j].set(df[results_main_columns[i]][j])

                #Clear the fields that are empty
                for j in range(display_items_len, self.MAX_WL_ENTRIES):
                    self.results_column_value_entry[column_name_index+j].set('')

            for i in range(num_of_columns):
                #Display column headers
                self.results_column_name_entry_handle[i].grid(row=0, column=i)
                column_name_index = (self.MAX_WL_ENTRIES*i)
                #Create a table for column values using the Entry widget
                for j in range(self.MAX_WL_ENTRIES):
                    #Input var
                    self.results_column_value_entry_handle[j + column_name_index].grid(row=(1+j), column=i)

        except:
            detailed_results_text = 'Scorer not run yet for current watchlist'

        #Check if Analyzer/Scorer is running
        if (self.gscorer != None):
            if (self.gscorer.analyzer_and_scorer_thread_is_alive()):
                detailed_results_text = 'Analyzer and Scorer run in progress'

        if (detailed_results_text != None):
            #Message showing scorer status with respect to current watchlist
            self.results_label2 = ttk.Label(self.results_frame, text=detailed_results_text, font=self.app_frame_label_font)

            #Display the path after the table
            self.results_label2.grid(row=(self.MAX_WL_ENTRIES+1), column=0, columnspan=5)
        else:
            #Assume browsing will work on all platforms and show dir path if it doesn't
            #Show browse results button
            self.browse_results_button = ttk.Button(self.results_frame, text="Browse results", command=self.launch_browse_thread)
            self.browse_results_button.grid(row=self.MAX_WL_ENTRIES+2, column=2, columnspan=2, sticky=(E))


    def show_dir_path_info(self):
        #Create a window for showing results path
        self.dir_path_window = Toplevel(self.app_frame)

        #Disable window resizing
        self.dir_path_window.resizable(FALSE, FALSE)

        #Title showing what it is
        self.dir_path_window.title('Results directory info')

        #Create a frame for results dir info
        self.dir_path_frame = ttk.Frame(self.dir_path_window, padding=10)
        self.dir_path_frame.grid(row=0, column=0, columnspan=5)

        #Get the full path of base dir where results are stored
        dir_string = os.getcwd() + '/' + 'tickers'

        #Create a label showing where to browse for results
        self.dir_path_label = ttk.Label(self.dir_path_frame, text=f'Detailed Results can be found in: \n{dir_string}', font=self.app_frame_label_font, justify='center')
        self.dir_path_label.grid(row=0, column=0, columnspan=5)

    def show_gssw_info(self):

        #Create a window for screener info entry
        self.about_window = Toplevel(self.app_frame)

        #Disable window resizing
        self.about_window.resizable(FALSE, FALSE)

        #Give a title to the window
        self.about_window.title('Stock Price Opining Toolset')

        #Create a frame for About data
        self.about_frame = ttk.Frame(self.about_window, padding=10)
        self.about_frame.grid(row=0, column=0, rowspan=3)
        curr_row_num = 1

        #Label with helpful text
        self.about_version_label = ttk.Label(self.about_frame, text=f'{gut.get_gammath_spot_version_string()}', font=self.app_frame_label_font)
        self.about_version_label.grid(row=curr_row_num, column=0)
        curr_row_num += 1

        self.about_copyright_label = ttk.Label(self.about_frame, text='(c) Gammath Works', font=self.app_frame_label_font)
        self.about_copyright_label.grid(row=curr_row_num, column=0)

        curr_row_num += 1

        self.about_website_label = ttk.Label(self.about_frame, text='https://www.gammathworks.com', font=self.app_frame_label_font)
        self.about_website_label.grid(row=curr_row_num, column=0)

    def add_menus(self):
        self.menubar = Menu(self.root)
        self.root['menu'] = self.menubar

        #Item for Watchlist
        self.menu_wl = Menu(self.menubar)

        #Item for Screener
        self.menu_screener = Menu(self.menubar)

        #Item for Results
        self.menu_results = Menu(self.menubar)

        #Item for About
        self.menu_about = Menu(self.menubar)

        #Watchlist menu item details
        self.menubar.add_cascade(menu=self.menu_wl, label='Watchlist')
        self.menu_wl.add_command(label='Create Watchlist', command=self.create_new_watchlist)
        self.menu_wls = Menu(self.menu_wl)
        self.menu_wl.add_cascade(menu=self.menu_wls, label='Load Watchlist')

        #Add watchlist list to loadable watchlist menu
        self.update_loadable_watchlist_list()

        #Save watchlist menu item
        self.menu_wl.add_command(label='Save Watchlist', command=self.save_watchlist)

        #Save As watchlist menu item
        self.menu_wl.add_command(label='Save Watchlist As', command=self.get_save_as_watchlist_name)

        #Add menu item to enter screening info
        self.menubar.add_cascade(menu=self.menu_screener, label='Screener')
        self.menu_screener.add_command(label='Screener Info', command=self.add_screener_info_widget)

        #Add menu item to show results info
        self.menubar.add_cascade(menu=self.menu_results, label='Results')
        self.menu_results.add_command(label='Results Info', command=self.add_results_info_widget)

        #Menu item to show info software info
        self.menubar.add_cascade(menu=self.menu_about, label='About')
        self.menu_about.add_command(label='Gammath SPOT', command=self.show_gssw_info)

    def create_canvas(self):

        width_in_inches, height_in_inches = self.get_canvas_dimensions_in_inches()

        #Convert inches into number of pixels
        self.canvas_width_in_pixels = (width_in_inches*self.pixels_per_inch)
        self.canvas_height_in_pixels = (height_in_inches*self.pixels_per_inch)

        #Create and position the canvas
        self.canvas = Canvas(self.root, width=self.canvas_width_in_pixels, height=self.canvas_height_in_pixels, background='white', borderwidth = 3, relief='solid')

        #Span it over two columns to facilitate placing widgets in the app frame
        self.canvas.grid(column=0, row=0, columnspan=2)

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
        self.app_frame = ttk.Frame(self.root, width=self.app_frame_width_in_pixels, height=self.app_frame_height_in_pixels, padding="50 30 0 30")
        self.app_frame.grid(row=self.starting_row_for_app_frame, column=0)

        #Use a font for app frame labels
        self.app_frame_label_font = font.Font(family='TimesNewRoman', name='appFrameLabelFont', size=16, weight='bold')

        #Create Toolset label
        self.toolset_label = ttk.Label(self.app_frame, text='Toolset', font=self.app_frame_label_font)
        self.toolset_label.grid(row=1, column=0)

        #Create Watchlist label
        self.wl_label_text = StringVar()
        self.wl_label = ttk.Label(self.app_frame, textvariable=self.wl_label_text, font=self.app_frame_label_font)
        self.wl_label_text.set('Watchlist')
        self.wl_label.grid(row=1, column=1)


    def add_tool_buttons_and_progress_bars(self):
        #Add Scraper tool button
        curr_row = (self.starting_row_for_app_frame + 2)
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

        #Screener doesn't use watchlist
        if (tool != 'Screener'):
            #Update the max count for progress bar to match current watchlist length
            pb['maximum'] = self.curr_watchlist_len
            if (tool == 'Projector'):
                pb['maximum'] += 1
        else:
            #Default value
            pb['maximum'] = 100

        #Keep mode to be indeterminate until the final item is done
        pb['mode'] = 'indeterminate'

        #Start the progress bar
        pb.start()

    def invoke_scraper(self):

        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Scraper')

        #Disable updating the watchlist while scraper is running
        self.set_watchlist_entry_widget_state('disable')

        #Launch GUI interface thread for Scraper tool
        self.launch_gui_tool_if_thread('Scraper', self.msg_queue)

        #Launch Scraper tool thread
        self.gscraper = gsds.GSCRAPER()
        base_file_name = os.path.basename(self.curr_watchlist)
        self.gscraper.launch_scraper_thread(base_file_name, self.msg_queue)

    def invoke_scorer(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Scorer')

        #Disable updating the watchlist while analyzer/scorer is running
        self.set_watchlist_entry_widget_state('disable')

        #Launch GUI interface thread for Scorer tool
        self.launch_gui_tool_if_thread('Scorer', self.msg_queue)

        #Launch Analyzer/Scorer tool thread
        self.gscorer = gsas.GSCORER()
        base_file_name = os.path.basename(self.curr_watchlist)
        self.gscorer.launch_analyzer_and_scorer_thread(base_file_name, self.msg_queue)


    def invoke_projector(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Projector')

        #Launch GUI interface thread for Projector tool
        self.launch_gui_tool_if_thread('Projector', self.msg_queue)

        #Launch Projector tool thread
        self.gprojector = gspep.GPROJECTOR()
        base_file_name = os.path.basename(self.curr_watchlist)
        self.gprojector.launch_projector_thread(base_file_name, self.msg_queue)

    def invoke_historian(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Historian')

        #Launch GUI interface thread for Historian tool
        self.launch_gui_tool_if_thread('Historian', self.msg_queue)

        #Launch Historian tool thread
        self.ghistorian = gsgh.GHISTORIAN()
        base_file_name = os.path.basename(self.curr_watchlist)
        self.ghistorian.launch_historian_thread(base_file_name, self.msg_queue)

    def invoke_backtester(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Backtester')

        #Launch GUI interface thread for Backtester tool
        self.launch_gui_tool_if_thread('Backtester', self.msg_queue)

        #Launch Backtester tool thread
        self.gbacktester = gsbt.GBACKTESTER()
        base_file_name = os.path.basename(self.curr_watchlist)
        self.gbacktester.launch_backtester_thread(base_file_name, self.msg_queue)

    def invoke_screener(self):
        #Disable tools buttons and start progress bar
        self.set_buttons_pb_state('Screener')

        #Launch GUI interface thread for Screener tool
        self.launch_gui_tool_if_thread('Screener', self.msg_queue)

        #Launch Screener tool thread
        self.gscreener = gssc.GSCREENER()
        self.gscreener.launch_screener_thread(self.curr_screener, self.msg_queue)


    def browse_results_dir(self):

        #We should show detailed results if platform supports it
        try:
            #Allow user to browse into specific sub-directory
            file_name = filedialog.askopenfilename(initialdir='tickers')

            #NOTE: Using filedialog on Mac shows a "python + CATransaction syncronize called within transaction" message.
            #Linux and Windows don't have this message.
            #Need to debug this for Mac to see if it is causing any problems

            #It will be empty string if user cancelled so check for that
            if (file_name != ''):
                #Run a command in a subshell
                #Open and associating with correct program will work on Mac; Linux and Windows with different utilities.
                #'open' works on Mac, 'xdg-open' works on Linux and on Windows, just full path with file name works.
                #Compose the shell command string
                if (os.name != 'posix'):
                    #Just full path with filename and extension for Windows
                    shell_cmd = f'{file_name}'
                else:
                    if (os.uname().sysname == 'Linux'):
                        #Need xdg-utils on Linux
                        shell_cmd = f'xdg-open {file_name}'
                    else:
                        #open is supported by default on Mac
                        shell_cmd = f'open {file_name}'

                #Run the shell command to open the chosen file
                os.system(shell_cmd)

        except:
            #In case any step for opening the file doesn't work on some platform
            #then show the results dir info to make it easier for user to browse using native
            #OS tools
            self.show_dir_path_info()

        return

    def launch_browse_thread(self):
        #Create a thread to browse results dir
        self.browse_dir_thread = threading.Thread(name=f'Browse_dir_thread', target=self.browse_results_dir, args=())
        self.browse_dir_thread.start()

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
                    #Re-enable watchlist entry widget
                    self.set_watchlist_entry_widget_state('enable')
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

    def gui_tool_if_thread_is_alive(self):
        #Check if thread is alive
        if (self.gui_tool_if_thread != None):
            alive = self.gui_tool_if_thread.is_alive()
        else:
            alive = False

        return alive

    def set_watchlist_entry_widget_state(self, state):
        #Set the correct state for ticker symbols entry widget
        for i in range(self.MAX_WL_ENTRIES):
            #Input var
            if (state == 'disable'):
                self.table_entry_handle[i]['state'] = 'readonly'
            else:
                self.table_entry_handle[i]['state'] = 'normal'

    def add_watchlist_widget(self):
        self.table_entry = []
        self.table_entry_handle = []

        #Create a table for symbol entry using the Entry widget
        for i in range(self.MAX_WL_ENTRIES):
            #Input var
            self.table_entry.append(StringVar())
            self.table_entry_handle.append(ttk.Entry(self.app_frame, width=20, textvariable=self.table_entry[i], justify='center'))
            self.table_entry_handle[i].grid(row=(4+i), column=1, padx=70, sticky=(E))

    def add_results_table_widget(self):
        #Placeholders for results window entry fields
        self.results_column_name_entry = []
        self.results_column_name_entry_handle = []
        self.results_column_value_entry = []
        self.results_column_value_entry_handle = []

        #Get column headers
        results_main_columns = gut.get_gscores_results_df_columns()
        num_of_columns = len(results_main_columns)

        #Create a table to show results
        for i in range(num_of_columns):
            column_name_index = (self.MAX_WL_ENTRIES*i)
            if (results_main_columns[i] != 'Note'):
                entry_width = 10
            else:
                #Notes needs more space
                entry_width = 30

            #Compose column headers
            self.results_column_name_entry.append(StringVar())
            self.results_column_name_entry_handle.append(ttk.Entry(self.results_frame, width=entry_width, justify='center', textvariable=self.results_column_name_entry[i]))
            self.results_column_name_entry[i].set(results_main_columns[i])
            #Not editable
            self.results_column_name_entry_handle[i]['state'] = 'readonly'

            #Create a table for column values using the Entry widget
            for j in range(self.MAX_WL_ENTRIES):
                #Input var
                self.results_column_value_entry.append(StringVar())
                self.results_column_value_entry_handle.append(ttk.Entry(self.results_frame, width=entry_width, justify='center', textvariable=self.results_column_value_entry[j + column_name_index]))
                #Not editable
                self.results_column_value_entry_handle[j + column_name_index]['state'] = 'readonly'

            #Display to be done after filling in values so grid is invoked in the caller


def main():
    #Start/Instantiate GUI. Won't return until app is closed
    Gammath_SPOT_GUI()

if __name__ == '__main__':
    main()
