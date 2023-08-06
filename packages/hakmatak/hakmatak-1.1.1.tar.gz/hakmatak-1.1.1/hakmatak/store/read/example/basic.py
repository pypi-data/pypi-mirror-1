#****************************************************************
# File:      ./hakmatak/store/read/example/basic.py
# (c) 2010, http://hakmatak.org, MIT License, ALL RIGHTS RESERVED
#****************************************************************
from hakmatak.constant import NAME,VALUE
from hakmatak.node import Node
from hakmatak.leaf import Leaf

from hakmatak.store.read.reader import Reader

# a simple tree expressed in python dict
SIMPLE_TREE = {
"attr0":"attribute 0 for /",
"attr1":"attribute 1 for /",
"leaf0":{
    "attr0":"attribute 0 for /leaf0",
    "attr1":"attribute 1 for /leaf0",
    "data":"data for /leaf0"
},
"leaf1":{
    "attr0":"attribute 0 for /leaf1",
    "attr1":"attribute 1 for /leaf1",
    "data":"data for /leaf1"
},
"node0":{
    "attr0":"attribute 0 for /node0",
    "attr1":"attribute 1 for /node0",
    "leaf0":{
        "attr0":"attribute 0 for /node0/leaf0",
        "attr1":"attribute 1 for /node0/leaf0",
        "data":"data for /node0/leaf0"
    },
},
"node":{
    "attr":"attribute for /node",
    "leaf":{
        "attr":"attribute for /node/leaf",
        "data":"data for /node/leaf"
    },
    "node A":{
        "attr":"attribute for /node/node A",
        "leaf":{
            "attr":"attribute for /node/node A/leaf",
            "data":"data for /node/node A/leaf"
        }
    },
}
}

class Basic(Reader):

    def _get_meta_root_node(self):
        node = Node('')

        d = SIMPLE_TREE

        for key in d.keys():
            # set attributes
            if key[:4] == "attr":
                node.attrs.append({NAME:key,VALUE:d[key]})
            # set leaves
            if key[:4] == "leaf":
                node.leaves.append({NAME:key})
            # set subnodes
            if key[:4] == "node":
                node.nodes.append({NAME:key})

        return node.get_meta()

    def _get_meta_level1_leaf(self,leafName):
        if not SIMPLE_TREE.has_key(leafName):
            raise Exception("Unknown leaf %s at level 1" % leafName)

        d = SIMPLE_TREE[leafName]

        leaf = Leaf(leafName)

        for key in d.keys():
            # set attributes
            if key[:4] == "attr":
                leaf.attrs.append({NAME:key,VALUE:d[key]})

        return leaf.get_meta()

    def _get_data_level1_leaf(self,leafName):
        if not SIMPLE_TREE.has_key(leafName):
            raise Exception("Unknown leaf %s at level 1" % leafName)

        d = SIMPLE_TREE[leafName]

        leaf = Leaf(leafName)

        for key in d.keys():
            # set attributes
            if key[:4] == "attr":
                leaf.attrs.append({NAME:key,VALUE:d[key]})
            # set data
            if key == "data":
                leaf.data = d[key]

        return leaf.get_data()

    def _get_meta_level1_node(self,nodeName):
        if not SIMPLE_TREE.has_key(nodeName):
            raise Exception("Unknown node %s at level 1" % nodeName)

        d = SIMPLE_TREE[nodeName]

        node = Node(nodeName)

        for key in d.keys():
            # set attributes
            if key[:4] == "attr":
                node.attrs.append({NAME:key,VALUE:d[key]})
            # set leaves
            if key[:4] == "leaf":
                node.leaves.append({NAME:key})
            # set subnodes
            if key[:4] == "node":
                node.nodes.append({NAME:key})

        return node.get_meta()

    def _get_meta_level2_leaf(self,parentNode,leafName):
        if not SIMPLE_TREE.has_key(parentNode):
            raise Exception("Unknown node %s at level 1" % parentNode)

        d = SIMPLE_TREE[parentNode]

        if not d.has_key(leafName):
            raise Exception("Unknown leaf %s at level 2" % leafName)

        d = SIMPLE_TREE[parentNode][leafName]

        leaf = Leaf(leafName)

        for key in d.keys():
            # set attributes
            if key[:4] == "attr":
                leaf.attrs.append({NAME:key,VALUE:d[key]})

        return leaf.get_meta()

    def _get_data_level2_leaf(self,parentNode,leafName):
        if not SIMPLE_TREE.has_key(parentNode):
            raise Exception("Unknown node %s at level 1" % parentNode)

        d = SIMPLE_TREE[parentNode]

        if not d.has_key(leafName):
            raise Exception("Unknown leaf %s at level 2" % leafName)

        d = SIMPLE_TREE[parentNode][leafName]

        leaf = Leaf(leafName)

        for key in d.keys():
            # set attributes
            if key[:4] == "attr":
                leaf.attrs.append({NAME:key,VALUE:d[key]})
            # set data
            if key == "data":
                leaf.data = d[key]

        return leaf.get_data()

    def _get_meta_level2_node(self,parentNode,nodeName):
        if not SIMPLE_TREE.has_key(parentNode):
            raise Exception("Unknown node %s at level 1" % parentNode)

        d = SIMPLE_TREE[parentNode]

        if not d.has_key(nodeName):
            raise Exception("Unknown node %s at level 2" % nodeName)

        d = SIMPLE_TREE[parentNode][nodeName]

        node = Node(nodeName)

        for key in d.keys():
            # set attributes
            if key[:4] == "attr":
                node.attrs.append({NAME:key,VALUE:d[key]})
            # set leaves
            if key[:4] == "leaf":
                node.leaves.append({NAME:key})
            # set subnodes
            if key[:4] == "node":
                node.nodes.append({NAME:key})

        return node.get_meta()

    def _get_meta_level3_leaf(self,level1Node,level2Node,leafName):
        if not SIMPLE_TREE.has_key(level1Node):
            raise Exception("Unknown node %s at level 1" % level1Node)

        d = SIMPLE_TREE[level1Node]

        if not d.has_key(level2Node):
            raise Exception("Unknown node %s at level 2" % level2Node)

        d = SIMPLE_TREE[level1Node][level2Node]

        if not d.has_key(leafName):
            raise Exception("Unknown leaf %s at level 3" % leafName)

        d = SIMPLE_TREE[level1Node][level2Node][leafName]

        leaf = Leaf(leafName)

        for key in d.keys():
            # set attributes
            if key[:4] == "attr":
                leaf.attrs.append({NAME:key,VALUE:d[key]})

        return leaf.get_meta()

    def _get_data_level3_leaf(self,level1Node,level2Node,leafName):
        if not SIMPLE_TREE.has_key(level1Node):
            raise Exception("Unknown node %s at level 1" % level1Node)

        d = SIMPLE_TREE[level1Node]

        if not d.has_key(level2Node):
            raise Exception("Unknown node %s at level 2" % level2Node)

        d = SIMPLE_TREE[level1Node][level2Node]

        if not d.has_key(leafName):
            raise Exception("Unknown leaf %s at level 3" % leafName)

        d = SIMPLE_TREE[level1Node][level2Node][leafName]

        leaf = Leaf(leafName)

        for key in d.keys():
            # set attributes
            if key[:4] == "attr":
                leaf.attrs.append({NAME:key,VALUE:d[key]})
            # set data
            if key == "data":
                leaf.data = d[key]

        return leaf.get_data()

    def get_meta(self,name,traverse=False):
        if traverse == True:
            raise Exception("Traverse not supported")

        # handle root
        if name == "":
            return self._get_meta_root_node()

        a = name[1:].split('/') # remove leading '/' and split

        # handle level 1
        if len(a) == 1:
            x = a[0]
            if x[:4] == "leaf":
                return self._get_meta_level1_leaf(x)
            if x[:4] == "node":
                return self._get_meta_level1_node(x)
            raise Exception("%s is neither leaf nor node at level 1." % name)

        # handle level 2
        if len(a) == 2:
            pNode = a[0] # parent node
            x = a[1]
            if x[:4] == "leaf":
                return self._get_meta_level2_leaf(pNode,x)
            if x[:4] == "node":
                return self._get_meta_level2_node(pNode,x)
            raise Exception("%s is neither leaf nor node at level 2." % name)

        # handle level 3
        if len(a) == 3:
            level1Node = a[0]
            level2Node = a[1]
            x = a[2]
            if x[:4] == "leaf":
                return self._get_meta_level3_leaf(level1Node,level2Node,x)
            if x[:4] == "node":
                raise Exception("No node at level 3.")
            raise Exception("%s is not leaf at level 3." % name)

        # no other levels
        raise Exception("No level beyond level 3.")

    def get_data(self,name,indexer=None,flatten=False):
        if indexer == None:
            raise Exception("Indexer is missing.")

        if indexer != '':
            raise Exception("Sub-indexer is not supported.")

        # handle root
        if name == '/':
            raise Exception("Data is not supported for node %s." % name)

        a = name[1:].split('/') # remove leading '/' and split

        # handle level 1
        if len(a) == 1:
            x = a[0]
            if x[:4] == "leaf":
                return self._get_data_level1_leaf(x)
            if x[:4] == "node":
                raise Exception("Data is not supported for node %s." % name)
            raise Exception("%s is neither leaf nor node at level 1." % name)

        # handle level 2
        if len(a) == 2:
            pNode = a[0] # parent node
            x = a[1]
            if x[:4] == "leaf":
                return self._get_data_level2_leaf(pNode,x)
            if x[:4] == "node":
                raise Exception("Data is not supported for node %s." % name)
            raise Exception("%s is neither leaf nor node at level 2." % name)

        # handle level 3
        if len(a) == 3:
            level1Node = a[0]
            level2Node = a[1]
            x = a[2]
            if x[:4] == "leaf":
                return self._get_data_level3_leaf(level1Node,level2Node,x)
            if x[:4] == "node":
                raise Exception("No node at level 3.")
            raise Exception("%s is not leaf at level 3." % name)

        # no other levels
        raise Exception("No level beyond level 3.")
