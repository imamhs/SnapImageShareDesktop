import os
import sys
import math
import re

import json
import requests
import requests.exceptions
import urllib.request
import threading
import io
import random
import time

import wx
import wx.lib.agw.hyperlink as hl


class SnapImageShare():
    def __init__(self):
        self.sis_app = wx.App()
        self.main_window = MainWindow()
        self.back_image = wx.Bitmap("./data/back.png", wx.BITMAP_TYPE_PNG)
    def run(self):
        self.sis_app.MainLoop()

class MainWindow(wx.Frame):
    def __init__(self):
        self.main_window_screen = None
        self.main_window_title = "Snap Image Share Desktop (New possibilities)"
        self.main_window_width = 820
        self.main_window_height = 700
        self.main_window_icon_file = './data/logo.png'
        self.main_window_icon = wx.Icon(self.main_window_icon_file, wx.BITMAP_TYPE_PNG)
        super(MainWindow, self).__init__(None, title=self.main_window_title, size=(self.main_window_width, self.main_window_height))
        self.SetSizeHints((self.main_window_width, self.main_window_height), maxSize=(self.main_window_width, self.main_window_height))
        self.SetIcon(self.main_window_icon)
        if self.main_window_screen == None:
            self.main_window_screen = SplashScreen(self)
        else:
            self.main_window_screen = MainScreen(self)
        self.Center()
        self.Show()

class SplashScreen():
    def __init__(self, _window):
        self.main_window = _window
        self.splash_screen_panel = wx.Panel(self.main_window, size=(self.main_window.Size[0], self.main_window.Size[1]))
        self.splash_screen_panel.SetBackgroundColour(wx.Colour(250, 250, 250))
        self.splash_screen_vbox = wx.BoxSizer(wx.VERTICAL)
        self.splash_screen_panel.SetSizer(self.splash_screen_vbox)
        self.splash_screen_intro_image = wx.StaticBitmap(self.splash_screen_panel, wx.ID_ANY, wx.Bitmap('./data/intro.png', wx.BITMAP_TYPE_PNG))
        self.splash_screen_vbox.Add(self.splash_screen_intro_image, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=80)
        self.splash_screen_intro_text = wx.StaticText(self.splash_screen_panel, style=wx.ALIGN_CENTER)
        self.splash_screen_intro_text.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_SLANT, wx.FONTWEIGHT_LIGHT))
        self.splash_screen_intro_text.SetLabel("Share file without Sign Up\nLimit file download\nSafe and secure free file sharing")
        self.splash_screen_intro_text.SetForegroundColour((103, 103, 103))
        #self.splash_screen_intro_text.SetSize(self.splash_screen_intro_text.GetTextExtent(self.splash_screen_intro_text.GetLabel()))
        self.splash_screen_vbox.Add(self.splash_screen_intro_text, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=100)
        self.splash_screen_intro_message_text = wx.StaticText(self.splash_screen_panel, style=wx.ALIGN_CENTER)
        self.splash_screen_intro_message_text.SetLabel("Click to continue")
        self.splash_screen_intro_message_text.SetForegroundColour((105, 105, 105))
        self.splash_screen_intro_message_text.Bind(wx.EVT_LEFT_DOWN, self.mouse_click_callback)
        self.splash_screen_vbox.Add(self.splash_screen_intro_message_text, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=20)
        #self.splash_screen_panel.Layout()
        #self.splash_screen_panel.SetSizerAndFit(self.splash_screen_vbox)

    def mouse_click_callback(self, e):
        self.splash_screen_panel.Hide()
        self.main_window.main_window_screen = MainScreen(self.main_window)

class MainScreen():
    def __init__(self, _window):
        self.main_window = _window
        self.main_screen_panel = wx.Notebook(self.main_window, size=(self.main_window.Size[0], self.main_window.Size[1]), style=wx.NB_TOP)
        self.main_screen_panel.SetBackgroundColour((120, 150, 150))
        self.main_screen_panel.SetFont(wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.main_screen_panel.SetForegroundColour((250, 250, 200))
        self.main_screen_panel.AddPage(SharePage(self.main_screen_panel).share_panel, "Share")
        self.main_screen_panel.AddPage(DownloadPage(self.main_screen_panel).download_panel, "Download")
        self.main_screen_panel.AddPage(AboutPage(self.main_screen_panel).about_panel, "About")
        self.main_screen_panel.SetPadding((80,-1))

        #self.main_screen_panel.Layout()
        #self.main_screen_panel.SetSizerAndFit(self.main_screen_vbox)

class SharePage():
    def __init__(self, _window):
        self.main_window = _window
        self.share_panel = wx.Panel(self.main_window, size=(self.main_window.Size[0], self.main_window.Size[1]))
        self.share_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.share_panel.SetSizer(self.share_panel_vbox)
        self.share_panel_vbox.Add(ShareSettingPage(self.share_panel, self.share_panel_vbox).share_setting_panel, flag=wx.EXPAND)
        self.share_panel.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)

    def on_erase_background(self, e):

        global snap_image_share

        dc = e.GetDC()

        if not dc:
            dc = wx.ClientDC(self.share_panel)
            rect = self.share_panel.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        dc.Clear()
        dc.DrawBitmap(snap_image_share.back_image, 0, 0)

class ShareSettingPage():
    def __init__(self, _window, _box):
        global share_goals
        self.main_window = _window
        self.main_window_box = _box
        self.share_setting_panel = wx.Panel(self.main_window, size=(self.main_window.Size[0], self.main_window.Size[1]))
        self.share_setting_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.share_setting_panel.SetSizer(self.share_setting_panel_vbox)
        self.share_setting_panel_vbox.AddSpacer(50)
        self.share_setting_name_message = wx.StaticText(self.share_setting_panel, style=wx.ALIGN_CENTER)
        self.share_setting_name_message.SetFont(wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.share_setting_name_message.SetLabel("Enter a title for your file")
        self.share_setting_name_message.SetForegroundColour((100, 100, 100))
        self.share_setting_panel_vbox.Add(self.share_setting_name_message, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.share_setting_panel_vbox.AddSpacer(30)
        self.share_setting_name_text = wx.TextCtrl(self.share_setting_panel, style=wx.TE_LEFT | wx.TE_NO_VSCROLL | wx.TE_BESTWRAP)
        self.share_setting_name_text.SetFont(wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))
        self.share_setting_name_text.SetForegroundColour((105, 105, 105))
        self.share_setting_name_text.SetValue(share_goals.title)
        self.share_setting_panel_vbox.Add(self.share_setting_name_text, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.share_setting_panel_vbox.AddSpacer(60)
        self.share_setting_downloads_message = wx.StaticText(self.share_setting_panel, style=wx.ALIGN_CENTER)
        self.share_setting_downloads_message.SetFont(wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.share_setting_downloads_message.SetLabel("Limit number of downloads")
        self.share_setting_downloads_message.SetForegroundColour((100, 100, 100))
        self.share_setting_panel_vbox.Add(self.share_setting_downloads_message, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.share_setting_panel_vbox.AddSpacer(30)
        self.share_setting_downloads_select = wx.Slider(self.share_setting_panel, value=share_goals.downloads, minValue=1, maxValue=1000, style=wx.SL_HORIZONTAL)
        self.share_setting_panel_vbox.Add(self.share_setting_downloads_select, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.share_setting_downloads_select.Bind(wx.EVT_SCROLL, self.on_downloads_scroll)
        self.share_setting_panel_vbox.AddSpacer(20)
        self.share_setting_downloads_number = wx.StaticText(self.share_setting_panel, style=wx.ALIGN_LEFT)
        self.share_setting_downloads_number.SetFont(wx.Font(12, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.share_setting_downloads_number.SetForegroundColour((50, 50, 50))
        self.share_setting_downloads_number.SetLabel(self.get_downloads_text(self.share_setting_downloads_select.GetValue()))
        self.share_setting_panel_vbox.Add(self.share_setting_downloads_number, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.share_setting_panel_vbox.AddSpacer(60)
        self.share_setting_time_message = wx.StaticText(self.share_setting_panel, style=wx.ALIGN_CENTER)
        self.share_setting_time_message.SetFont(wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.share_setting_time_message.SetLabel("Limit time to expiry")
        self.share_setting_time_message.SetForegroundColour((100, 100, 100))
        self.share_setting_panel_vbox.Add(self.share_setting_time_message, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.share_setting_panel_vbox.AddSpacer(30)
        self.share_setting_time_select = wx.Slider(self.share_setting_panel, value=share_goals.time, minValue=1, maxValue=10080, style=wx.SL_HORIZONTAL)
        self.share_setting_panel_vbox.Add(self.share_setting_time_select, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.share_setting_time_select.Bind(wx.EVT_SCROLL, self.on_time_scroll)
        self.share_setting_panel_vbox.AddSpacer(20)
        self.share_setting_time_number = wx.StaticText(self.share_setting_panel, style=wx.ALIGN_LEFT)
        self.share_setting_time_number.SetFont(wx.Font(12, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.share_setting_time_number.SetForegroundColour((50, 50, 50))
        self.share_setting_time_number.SetLabel(self.get_time_text(self.share_setting_time_select.GetValue()))
        self.share_setting_panel_vbox.Add(self.share_setting_time_number, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.share_setting_panel_vbox.AddSpacer(60)
        self.share_setting_select_file = wx.Button(self.share_setting_panel, label='Next')
        self.share_setting_select_file.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.share_setting_panel_vbox.Add(self.share_setting_select_file, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.share_setting_select_file.Bind(wx.EVT_BUTTON, self.on_select_file_click)

    def get_downloads_text(self, v):

        if v > 1:
            return str(v) + " times"
        else:
            return str(v) + " time"

    def on_downloads_scroll(self, e):

        global share_goals

        obj = e.GetEventObject()

        vald = obj.GetValue()

        self.share_setting_downloads_number.SetLabel(self.get_downloads_text(vald))

        share_goals.downloads = vald

    def get_time_text(self, v):

        time_m = v

        days_value = (time_m / 60) / 24
        hr_value = (days_value % 1) * 24
        min_value = (hr_value % 1) * 60

        days_value = int(round(days_value, 3))
        hr_value = int(round(hr_value, 3))
        min_value = int(round(min_value, 3))

        time_text = ""

        if (days_value > 0):
            if (days_value > 1):
                time_text += str(days_value) + " days"
            else:
                time_text += str(days_value) + " day"

        if (hr_value > 0):
            if (days_value > 0):
                time_text += ", "
            if (hr_value > 1):
                time_text += str(hr_value) + " hours"
            else:
                time_text += str(hr_value) + " hour"

        if (min_value > 0):
            if (days_value == 0 and hr_value > 0):
                time_text += ", "
            if (days_value > 0 and hr_value == 0):
                time_text += ", "
            if (days_value > 0 and hr_value > 0):
                time_text += ", "
            if (min_value > 1):
                time_text += str(min_value) + " minutes"
            else:
                time_text += str(min_value) + " minute"

        return time_text

    def on_time_scroll(self, e):

        global share_goals

        obj = e.GetEventObject()

        valt = obj.GetValue()

        self.share_setting_time_number.SetLabel(self.get_time_text(valt))

        share_goals.time = valt

    def on_select_file_click(self, e):

        global share_goals

        share_goals.title = self.share_setting_name_text.GetValue()

        self.share_setting_panel.Hide()
        self.main_window_box.Clear()
        self.main_window_box.Add(FileSelectionPage(self.main_window, self.main_window_box).file_selection_panel, flag=wx.EXPAND)

class FileSelectionPage():
    def __init__(self, _window, _box):
        global files_selection
        self.main_window = _window
        self.main_window_box = _box
        self.file_selection_panel = wx.Panel(self.main_window, size=(self.main_window.Size[0], self.main_window.Size[1]))
        self.file_selection_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.file_selection_panel.SetSizer(self.file_selection_panel_vbox)
        self.file_selection_panel_vbox.AddSpacer(50)
        self.file_selection_browse_file = wx.Button(self.file_selection_panel, label='Browse files to share')
        self.file_selection_browse_file.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.file_selection_panel_vbox.Add(self.file_selection_browse_file, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.file_selection_browse_file.Bind(wx.EVT_BUTTON, self.on_select_browse_click)
        self.file_selection_panel_vbox.AddSpacer(60)
        self.file_selection_selection_message = wx.StaticText(self.file_selection_panel, style=wx.ALIGN_CENTER)
        self.file_selection_selection_message.SetFont(wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.file_selection_selection_message.SetLabel("The following files are selected")
        self.file_selection_selection_message.SetForegroundColour((100, 100, 100))
        self.file_selection_panel_vbox.Add(self.file_selection_selection_message, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.file_selection_panel_vbox.AddSpacer(30)
        self.file_selection_selected_files = wx.ListCtrl(self.file_selection_panel, style = wx.LC_REPORT, size=(-1, 220))
        self.file_selection_selected_files.InsertColumn(0, 'File name', width=200)
        self.file_selection_selected_files.InsertColumn(1, 'Size (MB)', wx.LIST_FORMAT_LEFT, 100)
        self.file_selection_selected_files.InsertColumn(2, 'Location', wx.LIST_FORMAT_LEFT, 300)
        self.file_selection_selected_files.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        for i in range(files_selection.files_count):
            list_row = self.file_selection_selected_files.InsertItem(i, files_selection.files[i][0])
            self.file_selection_selected_files.SetItem(list_row, 1, str(files_selection.files[i][1]))
            self.file_selection_selected_files.SetItem(list_row, 2, files_selection.files[i][2])

        self.file_selection_panel_vbox.Add(self.file_selection_selected_files, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.file_selection_panel_vbox.AddSpacer(5)
        self.file_selection_selected_statistics = wx.StaticText(self.file_selection_panel, style=wx.ALIGN_LEFT)
        self.file_selection_selected_statistics.SetFont(wx.Font(12, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.file_selection_selected_statistics.SetForegroundColour((50, 50, 50))

        if files_selection.files_count == 0:
            self.file_selection_selected_statistics.SetLabel("No file selected")
        elif files_selection.files_count > 1:
            self.file_selection_selected_statistics.SetLabel("A total of " + str(round(files_selection.total_size, 2)) + " MB for " + str(
                files_selection.files_count) + " selected files")
        else:
            self.file_selection_selected_statistics.SetLabel("A total of " + str(round(files_selection.total_size, 2)) + " MB for " + str(
                files_selection.files_count) + " selected file")

        self.file_selection_panel_vbox.Add(self.file_selection_selected_statistics, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.file_selection_droped_files = FileDrop(self.file_selection_selected_files, self.file_selection_selected_statistics)
        self.file_selection_selected_files.SetDropTarget(self.file_selection_droped_files)
        self.file_selection_panel_vbox.AddSpacer(60)
        self.file_selection_clear_selections = wx.Button(self.file_selection_panel, label='Empty file selection')
        self.file_selection_clear_selections.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.file_selection_panel_vbox.Add(self.file_selection_clear_selections, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.file_selection_clear_selections.Bind(wx.EVT_BUTTON, self.on_clear_selection_click)
        self.file_selection_upload_selections = wx.Button(self.file_selection_panel, label='Upload files')
        self.file_selection_upload_selections.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.file_selection_panel_vbox.Add(self.file_selection_upload_selections, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.file_selection_upload_selections.Bind(wx.EVT_BUTTON, self.on_upload_selection_click)
        self.file_selection_panel_vbox.AddSpacer(10)
        self.file_selection_share_settings = wx.Button(self.file_selection_panel, label='Change share settings')
        self.file_selection_share_settings.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.file_selection_panel_vbox.Add(self.file_selection_share_settings, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.file_selection_share_settings.Bind(wx.EVT_BUTTON, self.on_share_settings_click)

    def on_select_browse_click(self, e):

        global files_selection

        FileBrowser = wx.FileDialog(self.file_selection_panel, "Open", "", "", "All files (*.*)|*.*", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        FileBrowser.SetDirectory(os.path.expanduser('~'))

        if FileBrowser.ShowModal() == wx.ID_OK:
            filenames = FileBrowser.GetFilenames()
            pathname = os.path.abspath(FileBrowser.GetDirectory())
            for i in range(len(filenames)):
                filepath = os.path.join(pathname, filenames[i])
                message_buffer = None
                file_s = round((os.path.getsize(filepath) / float(1 << 20)), 2)
                if file_s > 99.99:
                    wx.MessageBox("A file larger than " + str(files_selection.FILE_SIZE_LIMIT) + " MB is not accepted by the server", 'Information', wx.OK | wx.ICON_INFORMATION)
                    continue
                list_row = self.file_selection_selected_files.InsertItem(files_selection.files_count, filenames[i])
                self.file_selection_selected_files.SetItem(list_row, 1, str(file_s))
                self.file_selection_selected_files.SetItem(list_row, 2, pathname)
                files_selection.files[files_selection.files_count] = [filenames[i], file_s, pathname]
                files_selection.files_count += 1
                files_selection.total_size += file_s
                if files_selection.files_count > 1:
                    message_buffer = "A total of " + str(round(files_selection.total_size, 2)) + " MB for " + str(files_selection.files_count) + " selected files"
                else:
                    message_buffer = "A total of " + str(round(files_selection.total_size, 2)) + " MB for " + str(files_selection.files_count) + " selected file"
                self.file_selection_selected_statistics.SetLabel(message_buffer)

        FileBrowser.Destroy()

    def on_clear_selection_click(self, e):

        global files_selection

        self.file_selection_selected_files.DeleteAllItems()
        files_selection.total_size = 0
        files_selection.files_count = 0
        files_selection.files.clear()
        self.file_selection_selected_statistics.SetLabel("No file selected")

    def on_share_settings_click(self, e):

        self.file_selection_panel.Hide()
        self.main_window_box.Clear()
        self.main_window_box.Add(ShareSettingPage(self.main_window, self.main_window_box).share_setting_panel, flag=wx.EXPAND)

    def on_upload_selection_click(self, e):

        global files_selection

        if files_selection.files_count:

            self.file_selection_panel.Hide()
            self.main_window_box.Clear()
            self.main_window_box.Add(UploadPage(self.main_window, self.main_window_box).upload_panel, flag=wx.EXPAND)

        else:

            wx.MessageBox("Please select one or more files to upload", 'Information', wx.OK | wx.ICON_INFORMATION)

class UploadPage():
    def __init__(self, _window, _box):
        global files_selection
        self.main_window = _window
        self.main_window_box = _box
        self.upload_panel = wx.Panel(self.main_window, size=(self.main_window.Size[0], self.main_window.Size[1]))
        self.upload_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.upload_panel.SetSizer(self.upload_panel_vbox)
        self.upload_panel_vbox.AddSpacer(50)
        self.upload_file_message = wx.StaticText(self.upload_panel, style=wx.ALIGN_CENTER)
        self.upload_file_message.SetFont(wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.upload_file_message.SetForegroundColour((100, 100, 100))
        if files_selection.files_count > 1:
            self.upload_file_message.SetLabel("Trying to upload " + str(files_selection.files_count) + " files to cloud")
        else:
            self.upload_file_message.SetLabel("Trying to upload one file to cloud")
        self.upload_panel_vbox.Add(self.upload_file_message, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.upload_panel_vbox.AddSpacer(30)
        self.upload_progress_bar = wx.Gauge(self.upload_panel, range=100)
        self.upload_panel_vbox.Add(self.upload_progress_bar, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.upload_panel_vbox.AddSpacer(60)
        self.upload_files_report = wx.ListCtrl(self.upload_panel, style = wx.LC_REPORT, size=(-1, 220))
        self.upload_files_report.InsertColumn(0, 'File', width=200)
        self.upload_files_report.InsertColumn(1, 'Upload status', wx.LIST_FORMAT_LEFT, 220)
        self.upload_files_report.InsertColumn(2, 'Share code', wx.LIST_FORMAT_LEFT, 300)
        self.upload_files_report.InsertColumn(3, 'Share name', wx.LIST_FORMAT_LEFT, 200)
        self.upload_files_report.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.upload_panel_vbox.Add(self.upload_files_report, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.upload_panel_vbox.AddSpacer(20)
        self.upload_files_statistics = wx.StaticText(self.upload_panel, style=wx.ALIGN_LEFT)
        self.upload_files_statistics.SetFont(wx.Font(12, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.upload_files_statistics.SetForegroundColour((50, 50, 50))
        self.upload_files_statistics.SetLabel("Uploaded zero files")
        self.upload_panel_vbox.Add(self.upload_files_statistics, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.upload_panel_vbox.AddSpacer(60)
        self.upload_stop = wx.Button(self.upload_panel, label='Stop uploading')
        self.upload_stop.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.upload_panel_vbox.Add(self.upload_stop, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.upload_stop.Bind(wx.EVT_BUTTON, self.on_stop_upload_click)
        self.upload_stopped = False
        self.upload_copy_link = wx.Button(self.upload_panel, label='Copy the sharing links')
        self.upload_copy_link.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.upload_panel_vbox.Add(self.upload_copy_link, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.upload_copy_link.Bind(wx.EVT_BUTTON, self.on_upload_copy_link_click)
        self.upload_copy_link.Disable()
        self.upload_panel_vbox.AddSpacer(10)
        self.upload_share_new = wx.Button(self.upload_panel, label='Share new files')
        self.upload_share_new.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.upload_panel_vbox.Add(self.upload_share_new, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.upload_share_new.Bind(wx.EVT_BUTTON, self.on_share_new_click)

        self.file_uploads_required = files_selection.files_count
        self.file_upload_number = 0
        self.file_upload_thread = None

        self.upload_timer = wx.Timer(self.upload_panel)
        self.upload_panel.Bind(wx.EVT_TIMER, self.on_upload_timer, self.upload_timer)
        self.upload_timer.Start(1000)

    def on_upload_timer(self, event):

        global server_error

        if self.file_upload_number == 0:

            self.file_upload_thread = threading.Thread(target=self.upload_file, name='file_upload_thread' + str(self.file_upload_number + 1), args=(self.file_upload_number,))
            self.file_upload_thread.daemon = True
            self.file_upload_thread.start()
            self.file_upload_number += 1
            self.upload_stop.Enable()
        else:
            if self.file_upload_thread.isAlive() == False:

                if server_error.occured == True:
                    wx.MessageBox(server_error.last_message, 'Error', wx.OK | wx.ICON_ERROR)

                if self.file_upload_number < self.file_uploads_required:
                    self.file_upload_thread = threading.Thread(target=self.upload_file, name='file_upload_thread' + str(self.file_upload_number + 1), args=(self.file_upload_number,))
                    self.file_upload_thread.daemon = True
                    self.file_upload_thread.start()
                    self.file_upload_number += 1
                else:
                    self.upload_timer.Stop()
                    self.file_upload_number = 0
                    self.file_upload_thread = None
                    self.upload_stop.Disable()
                    self.upload_file_message.SetLabel("Uploading completed")
                    self.upload_progress_bar.SetValue(100)

    def on_stop_upload_click(self, e):

        if self.upload_stopped == False:
            self.upload_timer.Stop()
            self.upload_stop.SetLabel("Resume uploading")
            self.upload_stopped = True
        else:
            self.upload_timer.Start(1000)
            self.upload_stop.SetLabel("Stop uploading")
            self.upload_stopped = False

    def on_upload_copy_link_click(self, e):

        global files_selection, share_server_link

        copy_link_buffer = ""

        count = self.upload_files_report.GetItemCount()

        if count == 1:
            file_c = self.upload_files_report.GetItem(0, col=2)
            if file_c.GetText() != "":
                file_n = self.upload_files_report.GetItem(0, col=0)
                copy_link_buffer += file_n.GetText() + " : " + share_server_link + file_c.GetText()
        else:
            for row in range(count):
                file_c = self.upload_files_report.GetItem(row, col=2)
                if file_c.GetText() != "":
                    file_n = self.upload_files_report.GetItem(row, col=0)
                    copy_link_buffer += file_n.GetText() + " : " + share_server_link + file_c.GetText() + "\n"

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(copy_link_buffer))
            wx.TheClipboard.Close()
            wx.MessageBox("Copied share links to the clipboard", 'Information', wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Can not access the system clipboard", 'Error', wx.OK | wx.ICON_ERROR)

    def on_share_new_click(self, e):

        if self.file_upload_thread == None:

            global share_goals, files_selection

            share_goals.upload_completed = 0
            share_goals.upload_size = 0
            share_goals.upload_threads_count = 0

            files_selection.total_size = 0
            files_selection.files_count = 0
            files_selection.files.clear()

            self.upload_panel.Hide()
            self.main_window_box.Clear()
            self.main_window_box.Add(FileSelectionPage(self.main_window, self.main_window_box).file_selection_panel,flag=wx.EXPAND)

        else:
            wx.MessageBox("Please wait for the uploading process to finish", 'Information', wx.OK | wx.ICON_INFORMATION)

    def upload_file(self, _file_index):

        global share_goals, files_selection, server_error

        server_url = 'https://snapshare.salhosengineering.com/shareimage_upload_image.php'
        upload_data = {'image_data': (files_selection.files[_file_index][0], open(os.path.join(files_selection.files[_file_index][2], files_selection.files[_file_index][0]), 'rb').read())}
        file_n = files_selection.files[_file_index][0]
        file_s = files_selection.files[_file_index][1]
        files_count = files_selection.files_count

        share_title = None

        if files_count > 1:
            share_title = str(share_goals.title) + " file " + str(_file_index+1)
            upload_data['title'] = share_title
            upload_data['number_of_downloads'] = str(share_goals.downloads)
            upload_data['availability'] = str(share_goals.time)
        else:
            share_title = str(share_goals.title)
            upload_data['title'] = share_title
            upload_data['number_of_downloads'] = str(share_goals.downloads)
            upload_data['availability'] = str(share_goals.time)

        share_code = None

        (data, ctype) = requests.packages.urllib3.filepost.encode_multipart_formdata(upload_data)

        post_headers = {
            "Content-Type": ctype
        }

        post_data = BufferReader(data, upload_progress, progressbar=self.upload_progress_bar)

        try:
            r = requests.post(server_url, data=post_data, headers=post_headers, timeout=30)

            if r.status_code == requests.codes.ok:
                if len(r.text) > 0:
                    server_reply = r.text.split('.')
                    if int(server_reply[0]) == 0:
                        share_code = str(server_reply[2])
                        job_status = "Completed"
                        server_error.occured = False
                        server_error.last_message = "Upload completed"
                    else:
                        share_code = ""
                        share_title = ""
                        server_error.occured = False
                        server_error.last_message = str(server_reply[1])
            else:
                share_code = ""
                share_title = ""
                server_error.occured = True
                server_error.last_message = str("Can not reach to Snap Image Share server")

            job_status = server_error.occured == False and server_error.last_message == "Upload completed"

            if job_status:
                share_goals.upload_size += file_s
                share_goals.upload_completed += 1
            upload_size = share_goals.upload_size
            upload_completed = share_goals.upload_completed

            list_row = self.upload_files_report.InsertItem(0, file_n)
            if job_status:
                self.upload_files_report.SetItem(list_row, 1, "Completed")
                self.upload_files_report.SetItem(list_row, 2, share_code)
                self.upload_files_report.SetItem(list_row, 3, share_title)
            else:
                self.upload_files_report.SetItem(list_row, 1, server_error.last_message)
                self.upload_files_report.SetItem(list_row, 2, share_code)
                self.upload_files_report.SetItem(list_row, 3, share_title)

            if upload_completed > 1:
                self.upload_files_statistics.SetLabel("Uploaded " + str(round(upload_size, 2)) + " MB of data from " + str(upload_completed) + " files")
            else:
                self.upload_files_statistics.SetLabel("Uploaded " + str(round(upload_size, 2)) + " MB of data from " + str(upload_completed) + " file")

            if upload_completed > 0:
                self.upload_copy_link.Enable()

        except Exception as e:
            server_error.occured = True
            server_error.last_message = str(e)
            return False

        return True

class DownloadPage():
    def __init__(self, _window):

        global download_selection

        self.main_window = _window
        self.download_panel = wx.Panel(self.main_window, size=(self.main_window.Size[0], self.main_window.Size[1]))
        self.download_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.download_panel.SetSizer(self.download_panel_vbox)
        self.download_panel_vbox.AddSpacer(50)
        self.download_file_message = wx.StaticText(self.download_panel, style=wx.ALIGN_CENTER)
        self.download_file_message.SetFont(wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.download_file_message.SetForegroundColour((100, 100, 100))
        self.download_file_message.SetLabel("Downloads will be saved in the following directory")
        self.download_panel_vbox.Add(self.download_file_message, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.download_panel_vbox.AddSpacer(30)
        self.download_file_save_location = wx.TextCtrl(self.download_panel, style=wx.TE_LEFT | wx.TE_READONLY | wx.TE_NO_VSCROLL | wx.BORDER_SIMPLE)
        self.download_file_save_location.SetFont(wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))
        self.download_file_save_location.SetForegroundColour((100, 100, 100))
        self.download_file_save_location.SetBackgroundColour((250, 250, 250))
        self.download_file_save_location.SetCursor(wx.STANDARD_CURSOR)
        self.download_file_save_location.SetValue(download_selection.download_directory)
        self.download_panel_vbox.Add(self.download_file_save_location, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.download_save_location_select = wx.DirPickerCtrl(self.download_panel, path=download_selection.download_directory, message="Select a directory where the downloads will be saved", pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DIRP_DEFAULT_STYLE, validator=wx.DefaultValidator)
        self.download_save_location_select.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.download_panel_vbox.Add(self.download_save_location_select, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.download_save_location_select.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_location_select_click)
        # self.download_panel_vbox.AddSpacer(20)
        # self.download_save_location_select = wx.Button(self.download_panel, label='Select different download destination')
        # self.download_save_location_select.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        # self.download_panel_vbox.Add(self.download_save_location_select, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        # self.download_save_location_select.Bind(wx.EVT_BUTTON, self.on_location_select_click)
        self.download_panel_vbox.AddSpacer(5)
        self.download_paste_links = wx.Button(self.download_panel, label='Paste share links')
        self.download_paste_links.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.download_panel_vbox.Add(self.download_paste_links, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.download_paste_links.Bind(wx.EVT_BUTTON, self.on_paste_links_click)
        self.download_panel_vbox.AddSpacer(60)
        self.download_paste_message = wx.StaticText(self.download_panel, style=wx.ALIGN_CENTER)
        self.download_paste_message.SetFont(wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.download_paste_message.SetLabel("The following files are available to download")
        self.download_paste_message.SetForegroundColour((100, 100, 100))
        self.download_panel_vbox.Add(self.download_paste_message, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.download_panel_vbox.AddSpacer(30)
        self.download_available_files = wx.ListCtrl(self.download_panel, style=wx.LC_REPORT, size=(-1, 140))
        self.download_available_files.InsertColumn(0, 'File title', width=200)
        self.download_available_files.InsertColumn(1, 'Downloads remaining', wx.LIST_FORMAT_LEFT, 200)
        self.download_available_files.InsertColumn(2, 'Time to expiry', wx.LIST_FORMAT_LEFT, 150)
        self.download_available_files.InsertColumn(3, 'Share code', wx.LIST_FORMAT_LEFT, 200)
        self.download_available_files.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.download_panel_vbox.Add(self.download_available_files, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.download_panel_vbox.AddSpacer(10)
        self.download_statistics = wx.StaticText(self.download_panel, style=wx.ALIGN_LEFT)
        self.download_statistics.SetFont(wx.Font(12, wx.FONTFAMILY_DECORATIVE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.download_statistics.SetForegroundColour((50, 50, 50))
        self.download_statistics.SetLabel("No file downloaded yet")
        self.download_panel_vbox.Add(self.download_statistics, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=100)
        self.download_panel_vbox.AddSpacer(60)
        self.download_empty_selection = wx.Button(self.download_panel, label='Empty downloads selection')
        self.download_empty_selection.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.download_panel_vbox.Add(self.download_empty_selection, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.download_empty_selection.Bind(wx.EVT_BUTTON, self.on_empty_selection_click)
        self.download_panel_vbox.AddSpacer(10)
        self.download_the_selection = wx.Button(self.download_panel, label='Download')
        self.download_the_selection.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.download_panel_vbox.Add(self.download_the_selection, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, border=120)
        self.download_the_selection.Bind(wx.EVT_BUTTON, self.on_download_click)

        self.download_timer = wx.Timer(self.download_panel)
        self.download_panel.Bind(wx.EVT_TIMER, self.on_download_info_timer, self.download_timer)

        self.download_panel.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)

    def on_download_timer(self, event):

        global server_error, download_selection


        if self.file_download_number < self.downloads_required:

            if self.file_download_thread == None:
                self.file_download_thread = threading.Thread(target=self.file_download, name='file_download_thread' + str(self.file_download_number + 1), args=(self.file_download_number,))
                self.file_download_thread.daemon = True
                self.file_download_thread.start()
                self.file_download_number += 1
            else:
                if self.file_download_thread.isAlive() == False:

                    if server_error.occured == True:
                        wx.MessageBox(server_error.last_message, 'Error', wx.OK | wx.ICON_ERROR)

                    self.file_download_thread = threading.Thread(target=self.file_download, name='file_download_thread' + str(self.file_download_number + 1), args=(self.file_download_number,))
                    self.file_download_thread.daemon = True
                    self.file_download_thread.start()
                    self.file_download_number += 1

        else:
            self.download_timer.Stop()
            self.download_panel.Bind(wx.EVT_TIMER, self.on_download_info_timer, self.download_timer)
            self.download_the_selection.SetLabel("Download")
            self.download_the_selection.Enable()
            self.download_paste_links.Enable()
            self.download_save_location_select.Enable()


    def on_download_info_timer(self, event):

        global server_error
        # urllib.request.urlopen("https://snapshare.salhosengineering.com/").getcode()

        if self.link_thread.isAlive() == False:

            if server_error.occured == True:
                wx.MessageBox(server_error.last_message, 'Error', wx.OK | wx.ICON_ERROR)

            self.download_paste_links.SetLabel("Paste share links")
            self.download_paste_links.Enable()
            self.download_timer.Stop()

    def file_download(self, _file_index):

        global download_selection, server_error

        if download_selection.files[_file_index][4] == False:
            return False

        try:

            r = requests.get('https://snapshare.salhosengineering.com/shareimage_image_download.php', params={'urlcode': str(download_selection.files[_file_index][0])}, stream=True)
            if (r.status_code == requests.codes.ok):
                if (r.headers.get('content-type') == 'application/octet-stream'):
                    filename = re.findall(r'"(.*?)"', r.headers.get('content-disposition'))
                    file_size = float(r.headers.get('content-length'))
                    downloaded = 0.0
                    print(download_selection.download_directory + filename[0])
                    with open(download_selection.download_directory + filename[0], 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=4096):
                            fd.write(chunk)
                            downloaded += float(len(chunk))
                            percent = int((downloaded / file_size) * 100)
                            #self.download_statistics.SetLabel("Hello")
            else:
                server_error.occured = True
                server_error.last_message = "Can not reach to Snap Image Share server"

        except Exception as e:
            server_error.occured = True
            server_error.last_message = str(e)
            return False

        return True

    def on_download_click(self, e):

        global download_selection

        self.file_download_number = 0
        self.downloads_required = download_selection.files_count
        self.file_download_thread = None
        self.download_paste_links.Disable()
        self.download_save_location_select.Disable()
        self.download_the_selection.Disable()
        self.download_the_selection.SetLabel("Downloading...")
        self.download_panel.Bind(wx.EVT_TIMER, self.on_download_timer, self.download_timer)
        self.download_timer.Start(1000)

    def on_empty_selection_click(self, e):
        global download_selection

        download_selection.files.clear()
        download_selection.files_count = 0

        self.download_available_files.DeleteAllItems()

    def on_paste_links_click(self, e):
        text_data = wx.TextDataObject()
        if wx.TheClipboard.Open():
            success = wx.TheClipboard.GetData(text_data)
            wx.TheClipboard.Close()
        if success:
            self.links = text_data.GetText().splitlines()
            if len(self.links) > 0:
                self.link_thread = threading.Thread(target=self.link_information, name='link_information_thread')
                self.link_thread.daemon = True
                self.link_thread.start()
                self.download_paste_links.Disable()
                self.download_paste_links.SetLabel("Retrieving link details...")
                self.download_timer.Start(1000)
            else:
                wx.MessageBox("Please copy one or more sharing links to the Clipboard", 'Information', wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Can't paste from the Clipboard\nPlease check the clipboard", 'Error', wx.OK | wx.ICON_ERROR)

    def link_information(self):

        global download_selection, server_error, max_int

        files_found = 0

        for i in range(len(self.links)):
            share_code = ""
            if (len(self.links[i]) == 55):
                share_code = self.links[i]
            elif (len(self.links[i]) == 110):
                share_code = self.links[i][55:]
            else:
                continue

            if share_code != "":

                try:
                    r = requests.post('https://snapshare.salhosengineering.com/shareimage_image_link.php', data={'urlcode': str(share_code)}, timeout=30)
                    if (r.status_code == requests.codes.ok):
                        server_reply = json.loads(r.text)
                        if (server_reply['response_code'] == '1'):
                            download_selection.files[i] = [share_code, str(server_reply['response']), 0, 0, False]
                            download_selection.files_count += 1
                            files_found += 1
                        else:
                            download_selection.files[i] = [share_code, str(server_reply['title']), int(server_reply['downloads']), round(float(server_reply['time_remaining']) / 60, 2) * (60 * 1000), True]
                            download_selection.files_count += 1
                            files_found += 1
                    else:
                        server_error.occured = True
                        server_error.last_message = "Can not reach to Snap Image Share server"

                except Exception as e:
                    server_error.occured = True
                    server_error.last_message = str(e)
                    return False


        for i in range(files_found):
            list_row = self.download_available_files.InsertItem(max_int, download_selection.files[i][1])
            self.download_available_files.SetItem(list_row, 1, str(download_selection.files[i][2]))
            et_m = int(download_selection.files[i][3] / 60000)
            et_s = math.ceil(((download_selection.files[i][3] / 60000) % 1) * 60)
            self.download_available_files.SetItem(list_row, 2, str(int(et_m)) + ":" + str(int(et_s)))
            self.download_available_files.SetItem(list_row, 3, download_selection.files[i][0])

        return True

    def on_location_select_click(self, e):

        global download_selection, platform

        download_selection.download_directory = self.download_save_location_select.GetPath()

        if platform == "posix":
            download_selection.download_directory += "/"
        else:
            download_selection.download_directory += "\\"

        self.download_file_save_location.SetValue(download_selection.download_directory)

    def on_erase_background(self, e):

        global snap_image_share

        dc = e.GetDC()

        if not dc:
            dc = wx.ClientDC(self.share_panel)
            rect = self.share_panel.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        dc.Clear()
        dc.DrawBitmap(snap_image_share.back_image, 0, 0)

class AboutPage():
    def __init__(self, _window):
        global snap_image_share
        self.main_window = _window
        self.about_panel = wx.Panel(self.main_window, size=(self.main_window.Size[0], self.main_window.Size[1]))
        self.about_panel.SetBackgroundColour(wx.WHITE)
        self.about_panel_vbox = wx.BoxSizer(wx.VERTICAL)
        self.about_panel.SetSizer(self.about_panel_vbox)
        self.about_panel_vbox.AddSpacer(50)
        self.about_panel_name_text = wx.StaticText(self.about_panel, style=wx.ALIGN_CENTER)
        self.about_panel_name_text.SetFont(wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.about_panel_name_text.SetLabel(snap_image_share.main_window.main_window_title)
        self.about_panel_name_text.SetForegroundColour((50, 50, 50))
        self.about_panel_vbox.Add(self.about_panel_name_text, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=40)
        self.about_panel_about_text = wx.StaticText(self.about_panel, style=wx.ALIGN_CENTER)
        self.about_panel_about_text.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))
        self.about_panel_about_text.SetLabel("Snap Image Share is a secure file sharing service provided by\n SALHOS Engineering for easy file sharing")
        self.about_panel_about_text.SetForegroundColour((105, 105, 105))
        self.about_panel_vbox.Add(self.about_panel_about_text, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM, border=60)
        self.about_panel_license_text = wx.TextCtrl(self.about_panel, style=wx.TE_LEFT | wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_NO_VSCROLL | wx.TE_BESTWRAP | wx.BORDER_NONE, size=(-1, 120))
        self.about_panel_license_text.SetFont(wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))
        self.about_panel_license_text.SetForegroundColour((105, 105, 105))
        self.about_panel_license_text.SetBackgroundColour((250, 250, 250))
        self.about_panel_license_text.SetCursor(wx.STANDARD_CURSOR)
        self.about_panel_license_text.SetValue("File hosting online service provided by Snap Image Share is provided for use \"as is\" and is without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall Snap Image Share be liable to any party for any direct or indirect damages.")
        self.about_panel_vbox.Add(self.about_panel_license_text, flag=wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=60)
        self.about_panel_vbox.AddSpacer(100)
        self.about_panel_contact_line = wx.BoxSizer(wx.HORIZONTAL)
        self.about_panel_contact_textA = wx.StaticText(self.about_panel, style=wx.ALIGN_CENTER)
        self.about_panel_contact_textA.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        self.about_panel_contact_textA.SetLabel('Please use ')
        self.about_panel_contact_textA.SetForegroundColour((105, 105, 105))
        self.about_panel_salhos_email = hl.HyperLinkCtrl(self.about_panel, -1, "salhosengineering@gmail.com", URL="mailto:salhosengineering@gmail.com")
        self.about_panel_salhos_email.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        self.about_panel_contact_textB = wx.StaticText(self.about_panel, style=wx.ALIGN_CENTER)
        self.about_panel_contact_textB.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        self.about_panel_contact_textB.SetLabel(' to reach out to us.')
        self.about_panel_contact_textB.SetForegroundColour((105, 105, 105))
        self.about_panel_contact_line.Add(self.about_panel_contact_textA)
        self.about_panel_contact_line.Add(self.about_panel_salhos_email)
        self.about_panel_contact_line.Add(self.about_panel_contact_textB)
        self.about_panel_vbox.Add(self.about_panel_contact_line, flag=wx.RESERVE_SPACE_EVEN_IF_HIDDEN | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

class FileDrop(wx.FileDropTarget):

    def __init__(self, _window, _message):
        wx.FileDropTarget.__init__(self)
        self.main_window = _window
        self.message = _message

    def OnDropFiles(self, x, y, filenames):

        global files_selection

        for name in filenames:

            try:

                if os.path.getsize(name)/float(1<<17) > 99.99:
                    wx.MessageBox("A file larger than " + str(files_selection.FILE_SIZE_LIMIT) + " MB is not accepted by the server", 'Information', wx.OK | wx.ICON_INFORMATION)
                    continue

                if os.path.isfile(name):
                    file_n = os.path.basename(name)
                    file_s = round((os.path.getsize(name)/float(1<<20)), 2)
                    file_l = os.path.dirname(name)
                    message_buffer = None
                    list_row = self.main_window.InsertItem(files_selection.files_count, file_n)
                    self.main_window.SetItem(list_row, 1, str(file_s))
                    self.main_window.SetItem(list_row, 2, file_l)
                    files_selection.files[files_selection.files_count] = [file_n, file_s, file_l]
                    files_selection.files_count += 1
                    files_selection.total_size += file_s
                    if files_selection.files_count > 1:
                        message_buffer = "A total of " + str(round(files_selection.total_size, 2)) + " MB for " + str(files_selection.files_count) + " selected files"
                    else:
                        message_buffer = "A total of " + str(round(files_selection.total_size, 2)) + " MB for " + str(files_selection.files_count) + " selected file"
                    self.message.SetLabel(message_buffer)
                else:
                    wx.MessageBox("Only files can be selected", 'Information', wx.OK | wx.ICON_INFORMATION)

            except IOError as error:
                msg = "Error opening file\n {}".format(str(error))
                print('Error', msg)

                return False

        return True

class CancelledError(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg

    __repr__ = __str__

class BufferReader(io.BytesIO):
    def __init__(self, buf=b'', callback=None, cb_args=(), cb_kwargs={}, progressbar=None):
        self._callback = callback
        self._cb_args = cb_args
        self._cb_kwargs = cb_kwargs
        self._progress = 0
        self._len = len(buf)
        self._progressbar = progressbar
        io.BytesIO.__init__(self, buf)

    def __len__(self):
        return self._len

    def read(self, n=-1):
        chunk = io.BytesIO.read(self, n)
        self._progress += int(len(chunk))
        self._cb_kwargs.update({
            'size': self._len,
            'progress': self._progress
        })
        if self._callback:
            try:
                self._callback(*self._cb_args, **self._cb_kwargs, progressbar=self._progressbar)
            except Exception as e: # catches exception from the callback
                print(str(e))

        return chunk

def upload_progress(size=None, progress=None, progressbar=None):
    progressbar.SetValue(round(((progress/size)*100),1))

class ShareGoals():
    def __init__(self):
        self.title = "Untitled"
        self.downloads = 10
        self.time = 30
        self.upload_completed = 0
        self.upload_size = 0

class FilesSelection():
    def __init__(self):
        self.files = dict()
        self.total_size = 0
        self.files_count = 0
        self.FILE_SIZE_LIMIT = 100 # in megabytes

class DownloadSelection():
    def __init__(self):
        global platform

        self.files = dict()
        self.files_count = 0

        if platform == "posix":
            self.download_directory = os.path.expanduser('~') + "/"
        else:
            self.download_directory = os.path.expanduser('~') + "\\"

class ServerError():
    def __init__(self):
        self.occured = False
        self.last_message = ""

if __name__ == '__main__':
    max_int = sys.maxsize
    platform = os.name
    share_server_link = 'https://snapshare.salhosengineering.com/image.php?file='
    share_goals = ShareGoals()
    files_selection = FilesSelection()
    download_selection = DownloadSelection()
    server_error = ServerError()
    snap_image_share = SnapImageShare()
    snap_image_share.run()