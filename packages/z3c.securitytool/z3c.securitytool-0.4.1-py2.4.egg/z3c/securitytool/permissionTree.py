
class PermissionTree(object):
    """ The permission traversal object stores the location information on
        where permissions are attained and at what level. This is not a true
        tree object. just a vertical slice from the current context level to
        the root.
    """

    def __init__(self):
        self.name = None
        self.child = None
        self.parent = None        
        self.permissons = None

    def __repr__(self):
        return self.__class__.__name__
        
    def __iter__(self):
        node = self
        while node:
            yield node
            node = node.child


    def __call__(self,pMatrix, item, prinPerms):
        """ method responsible for creating permission tree """
        self.contextIndex = []
        self.pMatrix = pMatrix
        self.item = item
        self.prinPerms = prinPerms

        permTree = self.pMatrix['permissionTree']

        import pdb; pdb.set_trace()
        key = self.item.get('uid')


        keys =  [x.keys()[0] for x in permTree]

        # Each key is unique so we just get the list index to edit
        if key in keys:
            listIdx = keys.index(key)
        else:
            permTree.append({key:{}})
            listIdx = -1

        permTree[listIdx][key]['parentList'] = item.get('parentList')
        permTree[listIdx][key]['name'] = item.get('name')
        permTree[listIdx][key].setdefault('permissions',[])

        if prinPerms not in permTree[listIdx][key]['permissions']:
              permTree[listIdx][key]['permissions'].append(self.prinPerms)
                     
