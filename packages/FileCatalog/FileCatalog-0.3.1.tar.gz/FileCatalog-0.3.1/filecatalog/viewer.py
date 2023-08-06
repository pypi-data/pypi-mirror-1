#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File Catalog Viewer
===================

Visualize File Catalog YAML documents as tree.

:copyright: 2006-2008 Jochen Kupperschmidt
:license: GNU General Public License, version 2; see LICENSE for details
"""

from __future__ import with_statement
from functools import partial
import os
import sys

import wx
GetBitmap = wx.ArtProvider.GetBitmap
import yaml

from filecatalog import io, xhtmlizer
from filecatalog.io import DocumentProcessingError


TOOLBAR_ICON_SIZE = (24, 24)
TREE_ICON_SIZE = (16, 16)
FILE_WILDCARD = '|'.join((
    'YAML files (*.yaml, *.yml)|*.yaml;*.yml',
    'All files (*.*)|*.*'))


class MainFrame(wx.Frame):

    def __init__(self):
        """Create the main application frame."""
        wx.Frame.__init__(self, None, title='File Catalog Viewer')
        self.create_toolbar()

        self.tree_panel = TreePanel(self)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelectionChange)

        sizer = wx.GridSizer()
        sizer.Add(self.tree_panel, flag=wx.EXPAND | wx.ALL)
        self.SetSizerAndFit(sizer)
        self.SetDimensions(-1, -1, 500, 500)
        self.Center()

    def create_toolbar(self):
        """Create the toolbar."""
        self.toolbar = tb = self.CreateToolBar(
            wx.NO_BORDER | wx.TB_FLAT | wx.TB_HORZ_TEXT)

        # Define toolbar buttons (and separators).
        get_tb_bitmap = partial(GetBitmap, client=wx.ART_TOOLBAR)
        tb.SetToolBitmapSize(TOOLBAR_ICON_SIZE)
        tb.AddLabelTool(wx.ID_NEW, 'New', get_tb_bitmap(wx.ART_NEW))
        tb.AddLabelTool(wx.ID_OPEN, 'Open', get_tb_bitmap(wx.ART_FILE_OPEN))
        tb.AddSeparator()
        tb.AddLabelTool(wx.ID_SAVEAS, 'Export as XHTML',
            get_tb_bitmap(wx.ART_FILE_SAVE_AS))
        tb.EnableTool(wx.ID_SAVEAS, False)
        tb.AddSeparator()
        tb.AddLabelTool(wx.ID_EXIT, 'Quit', get_tb_bitmap(wx.ART_QUIT))
        tb.Realize()

        # Bind buttons to event handler callables.
        self.Bind(wx.EVT_TOOL, self.OnToolNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_TOOL, self.OnToolOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_TOOL, self.OnToolExportXhtml, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_TOOL, self.OnExit, id=wx.ID_EXIT)

    def OnTreeSelectionChange(self, event):
        id = self.tree_panel.tree.GetSelection()
        data = self.tree_panel.tree.GetItemPyData(id)
        self.toolbar.EnableTool(wx.ID_SAVEAS, data is not None)

    def OnToolNew(self, event):
        """Clear the tree (by removing all children)."""
        self.tree_panel.tree.DeleteChildren(self.tree_panel.root)

    def OnToolOpen(self, event):
        """Show a file selection dialog and load the selected file."""
        dlg = wx.FileDialog(self, message='Choose a file to load',
            defaultDir=os.getcwd(), defaultFile='', wildcard=FILE_WILDCARD,
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
        dlg.Destroy()

        try:
            self.tree_panel.load_file(path)
        except DocumentProcessingError, e:
            # Display an error dialog.
            errdlg = wx.MessageDialog(self, str(e),
                'Error loading data file', wx.OK | wx.ICON_ERROR)
            errdlg.ShowModal()
            errdlg.Destroy()

    def OnToolExportXhtml(self, event):
        """Present a file dialog and export the sub-tree selected in the tree
        panel as XHTML to that file.
        """
        wildcard = 'XHTML files (*.html, *.xhtml)|*.html;*.xhtml|' \
            + FILE_WILDCARD
        dlg = wx.FileDialog(self, message='Choose a filename to save to',
            defaultDir=os.getcwd(), defaultFile='', wildcard=wildcard,
            style=wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            target_path = dlg.GetPath()
        dlg.Destroy()

        # Fetch the selected sub-tree's data and metadata.
        id = self.tree_panel.tree.GetSelection()
        filename, data = self.tree_panel.tree.GetItemPyData(id)

        # Create XHTML and write it to the specified target file.
        xhtml_lines = xhtmlizer.create_xhtml(data, os.path.basename(filename))
        with open(target_path, 'wb') as f:
            f.writelines(list(xhtml_lines))

        # Show an informal message when complete.
        dlg = wx.MessageDialog(self, 'Done.',
            'The tree has been exported as XHTML to "%s".',
            wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        self.Close()


class TreePanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.WANTS_CHARS)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = wx.TreeCtrl(self, wx.NewId(), wx.DefaultPosition,
            wx.DefaultSize, wx.TR_HAS_BUTTONS)

        self.prepare_icons()

        # Set root node.
        self.root = self.tree.AddRoot('data files')
        self.set_item(self.root, 'harddisk')

    def prepare_icons(self):
        """Prepare icons by adding ``Bitmap``s to an ``ImageList``.
        
        The return value of ``ImageList.Add()`` is stored in a dictionary.
        """
        icon_names = ('harddisk', 'report_view', 'folder', 'folder_open',
            'normal_file')
        self.image_list = wx.ImageList(*TREE_ICON_SIZE)
        self.bitmap_ids = {}
        for name in icon_names:
            self.bitmap_ids[name] = self.image_list.Add(
                GetBitmap(getattr(wx, 'ART_%s' % name.upper()),
                wx.ART_OTHER, TREE_ICON_SIZE))
        self.tree.SetImageList(self.image_list)

    def OnSize(self, event):
        """Adjust the tree on panel resizing."""
        width, height = self.GetClientSizeTuple()
        self.tree.SetDimensions(0, 0, width, height)

    def load_file(self, filename):
        """Load a YAML document and add it to the tree."""
        data = io.load_file(filename)

        # Access hash.
        try:
            name, values = data.items()[0]
        except Exception, e:
            raise DocumentProcessingError('Invalid data, hash expected.')

        # Add data to tree.
        item = self.tree.AppendItem(self.root, '%s [%s]' % (name, filename))
        self.set_item(item, 'report_view', data=(filename, data))
        self.append_tree_item(values, item)
        self.tree.Expand(self.root)

    def append_tree_item(self, l, parent):
        """Recursively append items to the tree."""
        if not isinstance(l, list):
            raise DocumentProcessingError('Invalid data.')
        for value in l:
            if isinstance(value, dict):
                for key in value.iterkeys():
                    item = self.tree.AppendItem(parent, key)
                    self.set_item(item, 'folder', 'folder_open')
                    self.append_tree_item(value[key], item)
            else:
                item = self.tree.AppendItem(parent, value)
                self.set_item(item, 'normal_file')

    def set_item(self, item, image_key_normal, image_key_expanded=None, data=None):
        """For a tree item, set new data and open/collapsed icons."""
        if image_key_expanded is None:
            image_key_expanded = image_key_normal
        self.tree.SetPyData(item, data)
        self.tree.SetItemImage(item, self.bitmap_ids[image_key_normal],
            wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(item, self.bitmap_ids[image_key_expanded],
            wx.TreeItemIcon_Expanded)


def main(filenames=None):
    app = wx.App()
    frame = MainFrame()
    frame.Show()

    # Load files.
    if filenames:
        for fn in filenames:
            frame.tree_panel.load_file(fn)

    app.MainLoop()

if __name__ == '__main__':
    main(sys.argv[1:])
