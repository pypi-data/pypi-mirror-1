#   Copyright (c) 2007-2008 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import wx

from application import schema, dialogs
from i18n import MessageFactory
from osaf.framework.blocks.Block import Block
from osaf.framework.blocks import BlockEvent, ChoiceEvent, MenuItem, Menu

from debug.generate import GenerateAllItems
from debug.GenerateItemsFromFile import GenerateItems
from debug.mail import loadMailTests
from wx import xrc
import debug.generate_dialog.ItemGenerator as itemGenerator

_ = MessageFactory("Chandler-debugPlugin")


class TestMenuHandler(Block):

    def setStatusMessage(self, msg):
        Block.findBlockByName('StatusBar').setStatusMessage(msg)

    def on_debug_GenerateDataEvent(self, event):
        # triggered from "Tools | Test | Generate Data" and
        #                "Tools | Test | Generate Lots of Data" menu items

        if event.arguments['sender'].blockName == '_debug_GenerateMuchDataItem':
            count = 100
        else:
            count = 4

        view = self.itsView
        sidebarCollection = schema.ns("osaf.app", view).sidebarCollection

        return GenerateAllItems(view, count, sidebarCollection)

    def on_debug_GenerateDataFromFileEvent(self, event):
        # triggered from "Tools | Test | Generate Items from a File" menu

        res = dialogs.Util.showFileDialog(wx.GetApp().mainFrame,
                                          _(u"Choose a file to import"), "",
                                          _(u"import.csv"),
                                          _(u"CSV files|*.csv"),
                                          wx.OPEN)
        cmd, dir, filename = res
        if cmd != wx.ID_OK:
            self.setStatusMessage(_(u"Import aborted."))
            return

        self.setStatusMessage(_(u"Importing from %(filename)s.")
                              %{'filename': filename})

        return GenerateItems(self.itsView, os.path.join(dir, filename))
    
    def on_debug_GenerateDataFromDialogEvent(self, event):
        # triggered from "Tools | Test | Generate Items from dialog" menu
        itemGenerator.show()
    
    def on_debug_MimeTestEvent(self, event):
        loadMailTests(self.itsView, "mime_tests")

    def on_debug_i18nMailTestEvent(self, event):
        loadMailTests(self.itsView, "i18n_tests")


def makeTestMenu(parcel, toolsMenu):

    handler = TestMenuHandler.update(parcel, None,
                                     blockName='_debug_TestMenuHandler')

    generateDataEvent = \
        BlockEvent.update(parcel, None,
                          blockName='_debug_GenerateData',
                          dispatchEnum='SendToBlockByReference',
                          destinationBlockReference=handler)
    generateDataFromFileEvent = \
        BlockEvent.update(parcel, None,
                          blockName='_debug_GenerateDataFromFile',
                          dispatchEnum='SendToBlockByReference',
                          destinationBlockReference=handler)
    generateDataFromDialogEvent = \
        BlockEvent.update(parcel, None,
                          blockName='_debug_GenerateDataFromDialog',
                          dispatchEnum='SendToBlockByReference',
                          destinationBlockReference=handler)
    mimeTestEvent = \
        BlockEvent.update(parcel, None,
                          blockName='_debug_MimeTest',
                          dispatchEnum='SendToBlockByReference',
                          destinationBlockReference=handler)
    i18nMailTestEvent = \
        BlockEvent.update(parcel, None,
                          blockName='_debug_i18nMailTest',
                          dispatchEnum='SendToBlockByReference',
                          destinationBlockReference=handler)

    testMenu = Menu.update(parcel, None,
                           blockName='_debug_testMenu',
                           title=_(u'&Test'),
                           parentBlock=toolsMenu)

    MenuItem.update(parcel, None,
                    blockName='_debug_GenerateSomeDataItem',
                    title=_(u'&Generate Data'),
                    helpString=_(u'generates a few items of each kind'),
                    event=generateDataEvent,
                    parentBlock=testMenu)
    MenuItem.update(parcel, None,
                    blockName='_debug_GenerateMuchDataItem',
                    title=_(u'G&enerate Lots of Data'),
                    helpString=_(u'generates many items of each kind'),
                    event=generateDataEvent,
                    parentBlock=testMenu)
    MenuItem.update(parcel, None,
                    blockName='_debug_GenerateDataItemFromFile',
                    title=_(u'Generate Items from a &File'),
                    helpString=_(u'generates items from a file'),
                    event=generateDataFromFileEvent,
                    parentBlock=testMenu)
    MenuItem.update(parcel, None,
                    blockName='_debug_GenerateDataFromDialog',
                    title=_(u'Generate Items from a &Dialog'),
                    helpString=_(u'choose items to generate from a dialog'),
                    event=generateDataFromDialogEvent,
                    parentBlock=testMenu)
    MenuItem.update(parcel, None,
                    blockName='_debug_test_separator_1',
                    menuItemKind='Separator',
                    parentBlock=testMenu)

    MenuItem.update(parcel, None,
                    blockName='_debug_MimeTest',
                    title=_(u'Load MIME &Torture Tests'),
                    helpString=_(u'Loads real world complex / broken mime message examples provided by Anthony Baxter'),
                    event=mimeTestEvent,
                    parentBlock=testMenu)
    MenuItem.update(parcel, None,
                    blockName='_debug_i18nMailTest',
                    title=_(u'Load i18n &Mail Tests'),
                    helpString=_(u'Loads mail messages containing a variety of Charsets and Languages'),
                    event=i18nMailTestEvent,
                    parentBlock=testMenu)
