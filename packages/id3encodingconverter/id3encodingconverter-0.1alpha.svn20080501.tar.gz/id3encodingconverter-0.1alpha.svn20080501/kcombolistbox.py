from PyQt4.QtCore import SIGNAL
from PyKDE4.kdeui import KEditListBox, KComboBox, KLineEdit

class KComboListBox(KEditListBox):
    """
    A KEditListBox with a KComboBox as a custom editor that is not editable.
    See the feature request on kde-devel:
    [http://lists.kde.org/?l=kde-devel&m=120859565230461&w=2]
    """

    def __init__(self, parent, title=''):
        self.combo = KComboBox(True, parent)
        # as only writable comboboxes are allowed, we'll fake an editable first,
        #   reset to another line edit and disable editing afterwards
        self.lineEdit = KLineEdit(parent)
        self.lineEdit.setVisible(False)
        self.connect(self.combo, SIGNAL("activated(const QString &)"),
            self.lineEdit.setText),
        customEditor = KEditListBox.CustomEditor(self.combo)
        customEditor.setLineEdit(self.lineEdit)
        self.combo.setEditable(False)
        KEditListBox.__init__(self, title, customEditor, parent)

    def addItems(self, itemList):
        curIdx = self.combo.currentIndex()
        self.combo.addItems(itemList)
        if curIdx == -1:
            # select first element on first addition
            self.lineEdit.setText(self.combo.currentText())

    def comboBox(self):
        return self.combo

