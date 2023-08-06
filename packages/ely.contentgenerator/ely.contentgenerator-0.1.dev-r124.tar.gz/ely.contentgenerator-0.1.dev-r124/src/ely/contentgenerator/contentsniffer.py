

class PloneContentSniffer:

    def __init__(self, rootzopeobject):
        self._root = rootzopeobject

    def _walkTree(self, parent):
        newlist = [parent]
        for node in parent.getChildNodes():
            newlist.append(self._walkTree(node))
        return newlist

    def _generateTree(self):
        return self._walkTree(self._root)
    tree = property(_generateTree)
