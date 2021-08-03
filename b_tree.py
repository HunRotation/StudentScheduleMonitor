'''
참고: https://gist.github.com/mateor/885eb950df7231f178a5
기본 코드는 이 사이트에서 가져오고, 사용하고자 하는 용도에 맞게 코드를 일부 수정함.
'''
class BTree(object):
    """A BTree implementation with search and insert functions. Capable of any order t."""

    class Node(object):
        """A simple B-Tree Node."""

        # 노드 정의
        def __init__(self, t):
            self.keys = []
            self.children = []
            self.leaf = True
            # t is the order of the parent B-Tree. Nodes need this value to define max size and splitting.
            self._t = t

            # (한 노드에 담을 수 있는 키의 수가 t를 초과하는 경우) 노드를 두 자식 노드로 나누는 메소드
        def split(self, parent, payload):
            """Split a node and reassign keys/children."""
            new_node = self.__class__(self._t)

            mid_point = self.size//2
            split_value = self.keys[mid_point]
            parent.add_key(split_value)

            # Add keys and children to appropriate nodes
            new_node.children = self.children[mid_point + 1:]
            self.children = self.children[:mid_point + 1]
            new_node.keys = self.keys[mid_point+1:]
            self.keys = self.keys[:mid_point]

            # If the new_node has children, set it as internal node
            if len(new_node.children) > 0:
                new_node.leaf = False

            parent.children = parent.add_child(new_node)
            if payload < split_value[0]:
                return self
            else:
                return new_node

        # 한 노드에 키가 꽉 찼는지 확인하는 메소드
        @property
        def _is_full(self):
            return self.size == self._t

        # 한 노드에 들어 있는 키의 수를 반환하는 메소드
        @property
        def size(self):
            return len(self.keys)

        # 해당 노드에 키를 추가한 뒤 정렬
        def add_key(self, value, flag=True):
            """Add a key to a node. The node will have room for the key by definition."""
            self.keys.append(value + (flag,) if len(value) is 2 else value)
            self.keys.sort()
            idx = self.keys.index(value + (flag,) if len(value) is 2 else value)
            if (idx>0 and self.keys[idx-1][1] and value[0] < self.keys[idx-1][1]) or (idx<self.size-1 and self.keys[idx+1][0] < value[1]):
                self.keys[idx] = (self.keys[idx][0], self.keys[idx][1], False)
            return self.keys[idx][2]

        # 해당 노드에 자식 노드를 올바른 위치에 연결
        def add_child(self, new_node):
            """
            Add a child to a node. This will sort the node's children, allowing for children
            to be ordered even after middle nodes are split.
            returns: an order list of child nodes
            """
            i = len(self.children) - 1
            while i >= 0 and self.children[i].keys[0] > new_node.keys[0]:
                i -= 1
            return self.children[:i + 1]+ [new_node] + self.children[i + 1:]

  # B-tree의 정의
    def __init__(self, t):
        """
        Create the B-tree. t is the order of the tree. Tree has no keys when created.
        This implementation allows duplicate key values, although that hasn't been checked
        strenuously.
        """
        self._t = t
        if self._t <= 1:
            raise ValueError("B-Tree must have a degree of 2 or more.")
        self.root = self.Node(t)

    # B-tree에 payload 값을 삽입
    def insert(self, payload):
        """Insert a new key of value payload into the B-Tree."""
        try:
            flag = True
            node = self.root
            # Root is handled explicitly since it requires creating 2 new nodes instead of the usual one.
            if node._is_full:
                new_root = self.Node(self._t)
                new_root.children.append(self.root)
                new_root.leaf = False
                # node is being set to the node containing the ranges we want for payload insertion.
                node = node.split(new_root, payload[0])
                self.root = new_root
            while not node.leaf:
                i = node.size - 1
                while i > 0 and payload < node.keys[i] :
                    i -= 1
                if payload > node.keys[i]:
                    i += 1
                if (i>0 and node.keys[i-1][2] and payload[0] < node.keys[i-1][1]) or (i<node.size-1 and node.keys[i][2] and node.keys[i][0] < payload[1]):
                    flag = False

                next = node.children[i]
                if next._is_full:
                    node = next.split(node, payload[0])
                else:
                    node = next
            # Since we split all full nodes on the way down, we can simply insert the payload in the leaf.
            return node.add_key(payload, flag)
        except:
            return False

    # B-tree에서 특정 값(value)이 B-tree에 저장된 어떤 key의 구간 안에 포함되어 있으면 그 구간 및 포함된 노드를 반환
    def search(self, value, node=None):
        """Return the corresponding schedule and the containing node if the B-Tree contains a key that matches the value."""
        if node is None:
            node = self.root
        for k in node.keys:
            if k[0] <= value < k[1]:
                    return k
        if node.leaf:
            # If we are in a leaf, there is no more to check.
            return None
        else:
            i = 0
            while i < node.size and value > node.keys[i][0]:
                i += 1
            return self.search(value, node.children[i])

    # 시간 순서대로 모든 schedule을 리스트에 담아 반환
    def traverse(self, node=None):
        """Print an in-order representation."""
        if node is None:
            node = self.root
        if node.leaf:
            res = []
            for i in node.keys:
                if i[2]:
                    res.append(i)
            return res
        else:
            res = []
            for i in range(len(node.children)):
                res.extend(self.traverse(node.children[i]))
                if i < len(node.keys) and node.keys[i][2]:
                    res.append(node.keys[i])
            return res
    # 레벨 순서대로 모든 schedule을 출력
    def print_order(self):
        res = []
        """Print an level-order representation."""
        this_level = [self.root]
        while this_level:
            next_level = []
            output = ""
            for node in this_level:
                if node.children:
                    next_level.extend(node.children)
                output += str(node.keys) +" "+ str(node.leaf) +" / \n"
                res.extend(node.keys)
            print(output, end="")
            print(" // ")
            this_level = next_level
