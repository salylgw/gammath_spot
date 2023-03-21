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

class Gammath_SPOT_GUI:

    def __init__(self, root):
        self.tool_if_thread = None
        self.msg_queue = queue.Queue()
        self.scraper_pb = None
        self.scorer_pb = None
        self.projector_pb = None
        self.historian_pb = None
        self.backtester_pb = None
        self.screener_pb = None

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

    root = Tk()
    #Disable tear-off menus
    root.option_add('*tearOff', FALSE)

    #Set title for the main window
    root.title("Gammath SPOT")

    #Start/Instantiate GUI
    Gammath_SPOT_GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
