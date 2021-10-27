from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import methods
import bisect

class Outline(QWidget):
    def __init__(self, parent=None):
        super(Outline, self).__init__(parent)
        methods.registerObject(self)
        self.tree = QTreeWidget()
        v = QVBoxLayout(self)
        v.setContentsMargins(0,0,0,0)
        v.addWidget(self.tree)
        self.actualSymbols = ('', {})
        self.docstrings = {}
        self.collapsedItems = {}
        self.icons = {
            "function": QIcon("Images/Icons/iconFuncDark.png"),
            "class": QIcon("Images/Icons/iconClassDark.png"),
            "attribute": QIcon("Images/Icons/iconAttrDark.png")
        }
        self.symbols_index = []
        self.tree.setFrameShape(0)
        self.tree.header().setHidden(True)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.header().setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(False)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tree.itemClicked.connect(self.__onClicked)
        self.tree.itemActivated.connect(self.__onClicked)
    def update_symbols_tree(self, symbols, filename='', parent=None):
        """Method to Update the symbols on the Tree"""
        if not parent:
            if filename == self.actualSymbols[0] and \
                    self.actualSymbols[1] and not symbols:
                return
            if symbols == self.actualSymbols[1]:
                return
            self.tree.clear()
            self.actualSymbols = (filename, symbols)
            self.docstrings = symbols.get('docstrings', {})
            parent = self.tree
        if 'attributes' in symbols:
            globalAttribute = ItemTree(parent, ["Attributes"])
            globalAttribute.isClickable = False
            globalAttribute.isAttribute = True
            globalAttribute.setExpanded(self.getExpand(globalAttribute))
            for glob in symbols['attributes']:
                globItem = ItemTree(globalAttribute, [glob],
                                    lineno=symbols['attributes'][glob])
                globItem.isAttribute = True
                globItem.setIcon(0, self.icons["attribute"])
                globItem.setExpanded(self.getExpand(globItem))

        if 'functions' in symbols and symbols['functions']:
            functionsItem = ItemTree(parent, ["Functions"])
            functionsItem.isClickable = False
            functionsItem.isMethod = True
            functionsItem.setExpanded(self.getExpand(functionsItem))
            for func in symbols['functions']:
                item = ItemTree(functionsItem, [func],
                                lineno=symbols['functions'][func]['lineno'])
                item.isMethod = True
                item.setIcon(0, self.icons["function"])
                # item.setIcon(
                #    0, ui_tools.colored_icon(":img/function", "#9FA8DA"))
                item.setExpanded(self.getExpand(item))
                self.update_symbols_tree(
                    symbols['functions'][func]['functions'], parent=item)
        if 'classes' in symbols and symbols['classes']:
            classItem = ItemTree(parent, ["Classes"])
            classItem.isClickable = False
            classItem.isClass = True
            classItem.setExpanded(self.getExpand(classItem))
            for claz in symbols['classes']:
                line_number = symbols['classes'][claz]['lineno']
                item = ItemTree(classItem, [claz], lineno=line_number)
                item.isClass = True
                item.setIcon(0, self.icons["class"])
                item.setExpanded(self.getExpand(item))
                self.update_symbols_tree(symbols['classes'][claz]['members'],
                                         parent=item)
    def getExpand(self, item):
        """
        Returns True or False to be used as setExpanded() with the items
        It method is based on the click that the user made in the tree
        """
        name = self.getUniqueName(item)
        filename = self.actualSymbols[0]
        collapsed_items = self.collapsedItems.get(filename, [])
        can_check = (not item.isClickable) or item.isClass or item.isMethod
        if can_check and name in collapsed_items:
            return False
        return True
    @staticmethod
    def getUniqueName(item):
        """
        Returns a string used as unique name
        """
        # className_Attributes/className_Functions
        parent = item.parent()
        if parent:
            return "%s_%s" % (parent.text(0), item.text(0))
        return "_%s" % item.text(0)
    def focusInEvent(self, event):
        self.parent.btn7.setText("Outline")
        super().focusInEvent(event)
    def __onClicked(self, item):
        """ Takes and item object and goes to definition on the editor """
        if item.isClickable and self.parent.tabWidget.currentWidget():
            self.parent.tabWidget.currentWidget().setCursorPosition(item.lineno - 1, 0)
            self.parent.tabWidget.currentWidget().setFocus()
            self.tree.clearSelection()
class ItemTree(QTreeWidgetItem):
    """Item Tree widget items"""
    def __init__(self, parent, name, lineno=None):
        super(ItemTree, self).__init__(parent, name)
        self.lineno = lineno
        self.isClickable = True
        self.isAttribute = False
        self.isClass = False
        self.isMethod = False