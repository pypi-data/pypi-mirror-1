#   Copyright (c) 2007 Open Source Applications Foundation
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

__parcel__ = "dependency"

from i18n import MessageFactory
_ = MessageFactory("Chandler-DependencyPlugin")
from application import schema

from osaf.framework.blocks import BlockEvent, MenuItem, Menu, BranchSubtree
from osaf.framework.blocks.Block import Block
from osaf.framework.attributeEditors import (ChoiceAttributeEditor,
                                             AttributeEditors)

from osaf.views.detail.detail import DetailSynchronizedContentItemDetailBlock
from osaf.views.detail.detailblocks import (makeArea, makeEditor, RectType,
                                            makeLabel, makeSpacer, SizeType)

from osaf import pim

from Dependency import Dependency, getDependencies
import wx

from osaf.framework.blocks.DragAndDrop import ItemClipboardHandler

ITEM_FORMAT = ItemClipboardHandler().DataObjectFormat()

def makeDependencyMenu(parcel, parentMenu):

    handler = DependencyMenuBlock.update(parcel, None,
        blockName='DependencyMenuHandler')

    addDependencyEvent = BlockEvent.update(parcel, None,
        blockName='AddDependency',
        dispatchEnum='SendToBlockByReference',
        destinationBlockReference=handler)

    dependencyMenu = Menu.update(parcel, None, blockName='DependencyMenu',
        title="Dependencies",
        parentBlock=parentMenu)

    MenuItem.update(parcel, None, blockName='AddDependencyMenu',
        title=_(u"A&dd dependency"),
        accel = _(u'Ctrl+D'),
        helpString=_(u"Add the item in the clipboard as a dependency of the selected item"),
        event=addDependencyEvent,
        parentBlock=dependencyMenu)

class DependencyMenuBlock(Block):

    def onAddDependencyEvent(self, event):
        rv = self.itsView
        
        clipboard = wx.TheClipboard
        if clipboard.Open():
            selected = self.getSelected()
            assert len(selected) == 1
            selected = selected[0]
            data = wx.CustomDataObject(ITEM_FORMAT)
            if clipboard.GetData(data):
                for uuid in data.GetData().split(','):
                    item = rv.findUUID(uuid)
                    if item is not None:
                        annotated = Dependency(item)
                        if not hasattr(annotated, 'blockerFor'):
                            annotated.blockerFor = []
                        annotated.blockerFor.append(selected)
                
            clipboard.Close()

    def onAddDependencyEventUpdateUI(self, event):
        clipboard = wx.TheClipboard
        args = event.arguments
        args['Enable'] = False
        args['Text'] = _(u"Add copied item as dependency")
        
        if clipboard.IsSupported(ITEM_FORMAT):
            sel = self.getSelected()
            if len(sel) != 1:
                return
            
            rv = self.itsView
            if clipboard.Open():
                data = wx.CustomDataObject(ITEM_FORMAT)
                if clipboard.GetData(data):
                    for uuid in data.GetData().split(','):
                        item = rv.findUUID(uuid)
                        if item is not None:
                            txt = {'title' : item.displayName }
                            msg = _(u"Add '%(title)s' as a dependency")
                            args['Text'] = msg % txt
                            args['Enable'] = item not in getDependencies(sel[0])
                            break
                    
                clipboard.Close()
            

    def getSelected(self):
        try:
            return list(self.getFocusBlock().widget.SelectedItems())
        except:
            return []

class DependenciesAreaBlock(DetailSynchronizedContentItemDetailBlock):
    attributeName = Dependency.dependencies.name
    def shouldShow(self, item):
        return (super(DetailSynchronizedContentItemDetailBlock, self).shouldShow(item) 
                and len(getDependencies(item, self.attributeName)) > 0)

class BlockersAreaBlock(DependenciesAreaBlock):
    attributeName = Dependency.blockerFor.name

titles = {Dependency.dependencies.name : _(u"Dependencies:"),
          Dependency.blockerFor.name   : _(u"Blocking:")}

class DependencyAttributeEditor(ChoiceAttributeEditor):

    def onChoice(self, event):
        newChoice = self.GetControlValue(event.GetEventObject())
        if newChoice == 0:
            return # label chosen, nothing to do

        item = list(getattr(self.item, self.attributeName))[newChoice - 1]
        sidebarBPB = Block.findBlockByName("SidebarBranchPointBlock")
        sidebarBPB.childBlocks.first().postEventByName (
           'SelectItemsBroadcast', {'items':[item]}
            )

    def GetAttributeValue(self, item, attributeName):
        # always start from the "Go to" option
        return 0

    def SetAttributeValue(self, item, attributeName, value):
        pass

    def GetControlValue(self, control):
        """
        Get the value for the current selection.
        """ 
        choiceIndex = control.GetSelection()
        return choiceIndex

    def SetControlValue(self, control, value):
        """
        Select the choice that matches this index value.
        """
        # We also take this opportunity to populate the menu
        control.Clear()
        choices = [titles[self.attributeName]]
        choices.extend([i.displayName for i in 
                        getDependencies(self.item, self.attributeName)])
        control.AppendItems(choices)
        control.Select(value)
        
def installDetailBlocks(parcel, oldVersion):
    AttributeEditors.AttributeEditorMapping.update(parcel, 
        'ContentItem+dependencies',
        className=__name__ + '.' + 'DependencyAttributeEditor'
    )

    AttributeEditors.AttributeEditorMapping.update(parcel, 
        'NoneType+dependencies',
        className=__name__ + '.' + 'DependencyAttributeEditor'
    )
    
    dependencyArea = \
        makeArea(parcel, 'DependencyArea',
            viewAttribute=Dependency.dependencies.name,
            baseClass=DependenciesAreaBlock,
            border=RectType(0,0,0,0),
            childBlocks=[
                makeEditor(parcel, 'DependencyEditor',
                           viewAttribute=Dependency.dependencies.name,
                           border=RectType(0,2,2,2),
                           presentationStyle={'format': 'dependencies'},
                           stretchFactor=0.0,
                           minimumSize=SizeType(180, -1))],
            position=0.95).install(parcel)

    blockersArea = \
        makeArea(parcel, 'BlockersArea',
            viewAttribute=Dependency.blockerFor.name,
            baseClass=BlockersAreaBlock,
            border=RectType(0,0,0,0),
            childBlocks=[
                makeEditor(parcel, 'BlockersEditor',
                           viewAttribute=Dependency.blockerFor.name,
                           border=RectType(0,2,2,2),
                           presentationStyle={'format': 'dependencies'},
                           stretchFactor=0.0,
                           minimumSize=SizeType(180, -1))],
            position=0.95).install(parcel)

    
    main_ns = schema.ns('osaf.views.main', parcel.itsView)
    note_uuid = pim.Note.getKind(parcel.itsView).itsUUID
    branch = main_ns.DetailBranchPointDelegateInstance.keyUUIDToBranch[note_uuid]
    branch.childBlocks.extend([dependencyArea, blockersArea])
