# Data Structures Implementation Guide

## 1. Binary Tree Node

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Common traversals
def inorder(root):
    if not root:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def preorder(root):
    if not root:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def postorder(root):
    if not root:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]

# Iterative level-order (BFS)
def levelOrder(root):
    if not root:
        return []
    result, queue = [], [root]
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.pop(0)
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

## 2. Binary Search Tree (BST)

```python
class BST:
    def __init__(self):
        self.root = None

    def insert(self, val):
        def _insert(node, val):
            if not node:
                return TreeNode(val)
            if val < node.val:
                node.left = _insert(node.left, val)
            else:
                node.right = _insert(node.right, val)
            return node

        self.root = _insert(self.root, val)

    def search(self, val):
        def _search(node, val):
            if not node:
                return False
            if node.val == val:
                return True
            if val < node.val:
                return _search(node.left, val)
            return _search(node.right, val)

        return _search(self.root, val)

    def delete(self, val):
        def _findMin(node):
            while node.left:
                node = node.left
            return node

        def _delete(node, val):
            if not node:
                return None

            if val < node.val:
                node.left = _delete(node.left, val)
            elif val > node.val:
                node.right = _delete(node.right, val)
            else:
                # Node with only one child or no child
                if not node.left:
                    return node.right
                elif not node.right:
                    return node.left

                # Node with two children
                successor = _findMin(node.right)
                node.val = successor.val
                node.right = _delete(node.right, successor.val)

            return node

        self.root = _delete(self.root, val)
```

## 3. Min Heap

```python
class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, val):
        self.heap.append(val)
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        min_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._bubble_down(0)
        return min_val

    def peek(self):
        return self.heap[0] if self.heap else None

    def _bubble_up(self, idx):
        parent = (idx - 1) // 2
        if idx > 0 and self.heap[idx] < self.heap[parent]:
            self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
            self._bubble_up(parent)

    def _bubble_down(self, idx):
        left = 2 * idx + 1
        right = 2 * idx + 2
        smallest = idx

        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left
        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right

        if smallest != idx:
            self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
            self._bubble_down(smallest)

    def heapify(self, arr):
        """Build heap from array in O(n) time"""
        self.heap = arr[:]
        # Start from last non-leaf node
        for i in range(len(self.heap) // 2 - 1, -1, -1):
            self._bubble_down(i)
```

## 4. Max Heap

```python
class MaxHeap:
    def __init__(self):
        self.heap = []

    def push(self, val):
        self.heap.append(val)
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        max_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._bubble_down(0)
        return max_val

    def _bubble_up(self, idx):
        parent = (idx - 1) // 2
        if idx > 0 and self.heap[idx] > self.heap[parent]:
            self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
            self._bubble_up(parent)

    def _bubble_down(self, idx):
        left = 2 * idx + 1
        right = 2 * idx + 2
        largest = idx

        if left < len(self.heap) and self.heap[left] > self.heap[largest]:
            largest = left
        if right < len(self.heap) and self.heap[right] > self.heap[largest]:
            largest = right

        if largest != idx:
            self.heap[idx], self.heap[largest] = self.heap[largest], self.heap[idx]
            self._bubble_down(largest)
```

## 5. Trie (Prefix Tree)

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def startsWith(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
```

## 6. Linked List

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def append(self, val):
        if not self.head:
            self.head = ListNode(val)
        else:
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = ListNode(val)
        self.size += 1

    def prepend(self, val):
        new_node = ListNode(val)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def delete(self, val):
        if not self.head:
            return False

        if self.head.val == val:
            self.head = self.head.next
            self.size -= 1
            return True

        curr = self.head
        while curr.next:
            if curr.next.val == val:
                curr.next = curr.next.next
                self.size -= 1
                return True
            curr = curr.next
        return False

    def find(self, val):
        curr = self.head
        while curr:
            if curr.val == val:
                return True
            curr = curr.next
        return False

    def reverse(self):
        prev = None
        curr = self.head
        while curr:
            next_temp = curr.next
            curr.next = prev
            prev = curr
            curr = next_temp
        self.head = prev
```

## 7. Doubly Linked List

```python
class DLLNode:
    def __init__(self, val=0, prev=None, next=None):
        self.val = val
        self.prev = prev
        self.next = next

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, val):
        new_node = DLLNode(val)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def prepend(self, val):
        new_node = DLLNode(val)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1

    def delete(self, node):
        if node == self.head:
            self.head = node.next
        if node == self.tail:
            self.tail = node.prev
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        self.size -= 1
```

## 8. Deque (Double-ended Queue)

```python
class Deque:
    def __init__(self):
        self.items = []

    def append(self, val):
        """Add to right"""
        self.items.append(val)

    def appendleft(self, val):
        """Add to left"""
        self.items.insert(0, val)

    def pop(self):
        """Remove from right"""
        if not self.items:
            raise IndexError("Deque is empty")
        return self.items.pop()

    def popleft(self):
        """Remove from left"""
        if not self.items:
            raise IndexError("Deque is empty")
        return self.items.pop(0)

    def peek(self):
        """View rightmost"""
        return self.items[-1] if self.items else None

    def peekleft(self):
        """View leftmost"""
        return self.items[0] if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
```

## 9. Stack

```python
class Stack:
    def __init__(self):
        self.items = []

    def push(self, val):
        self.items.append(val)

    def pop(self):
        if not self.items:
            raise IndexError("Stack is empty")
        return self.items.pop()

    def peek(self):
        return self.items[-1] if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
```

## 10. Queue

```python
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, val):
        self.items.append(val)

    def dequeue(self):
        if not self.items:
            raise IndexError("Queue is empty")
        return self.items.pop(0)

    def peek(self):
        return self.items[0] if self.items else None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

# More efficient queue using deque
from collections import deque

class EfficientQueue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, val):
        self.items.append(val)

    def dequeue(self):
        if not self.items:
            raise IndexError("Queue is empty")
        return self.items.popleft()  # O(1) instead of O(n)
```

## 11. Graph - Adjacency List

```python
class Graph:
    def __init__(self, directed=False):
        self.graph = {}
        self.directed = directed

    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = []

    def add_edge(self, v1, v2, weight=1):
        if v1 not in self.graph:
            self.add_vertex(v1)
        if v2 not in self.graph:
            self.add_vertex(v2)

        self.graph[v1].append((v2, weight))
        if not self.directed:
            self.graph[v2].append((v1, weight))

    def get_neighbors(self, vertex):
        return self.graph.get(vertex, [])

    def bfs(self, start):
        visited = set()
        queue = [start]
        result = []

        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.add(vertex)
                result.append(vertex)
                for neighbor, _ in self.get_neighbors(vertex):
                    if neighbor not in visited:
                        queue.append(neighbor)

        return result

    def dfs(self, start):
        visited = set()
        result = []

        def _dfs(vertex):
            visited.add(vertex)
            result.append(vertex)
            for neighbor, _ in self.get_neighbors(vertex):
                if neighbor not in visited:
                    _dfs(neighbor)

        _dfs(start)
        return result

    def has_cycle(self):
        """Detect cycle in directed graph"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {v: WHITE for v in self.graph}

        def visit(v):
            if color[v] == GRAY:
                return True  # Back edge found
            if color[v] == BLACK:
                return False  # Already processed

            color[v] = GRAY
            for neighbor, _ in self.get_neighbors(v):
                if visit(neighbor):
                    return True
            color[v] = BLACK
            return False

        for vertex in self.graph:
            if color[vertex] == WHITE:
                if visit(vertex):
                    return True
        return False
```

## 12. Graph - Adjacency Matrix

```python
class GraphMatrix:
    def __init__(self, num_vertices, directed=False):
        self.num_vertices = num_vertices
        self.directed = directed
        self.matrix = [[0] * num_vertices for _ in range(num_vertices)]

    def add_edge(self, v1, v2, weight=1):
        if 0 <= v1 < self.num_vertices and 0 <= v2 < self.num_vertices:
            self.matrix[v1][v2] = weight
            if not self.directed:
                self.matrix[v2][v1] = weight

    def remove_edge(self, v1, v2):
        if 0 <= v1 < self.num_vertices and 0 <= v2 < self.num_vertices:
            self.matrix[v1][v2] = 0
            if not self.directed:
                self.matrix[v2][v1] = 0

    def has_edge(self, v1, v2):
        if 0 <= v1 < self.num_vertices and 0 <= v2 < self.num_vertices:
            return self.matrix[v1][v2] != 0
        return False

    def get_neighbors(self, vertex):
        neighbors = []
        if 0 <= vertex < self.num_vertices:
            for i in range(self.num_vertices):
                if self.matrix[vertex][i] != 0:
                    neighbors.append((i, self.matrix[vertex][i]))
        return neighbors
```

## 13. Union Find (Disjoint Set)

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # Number of disjoint sets

    def find(self, x):
        """Find with path compression"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        """Union by rank"""
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # Already in same set

        # Attach smaller tree to larger tree

        # If root_x is smaller tree, then set parent of root_x = root_y
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        # If root_y is smaller tree, then set parent of root_y = root_x
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        
        # ELSE: Both trees have the SAME RANK (aka HEIGHT)
        # When ranks/height are equal, you can attach either tree to the other, BUT you MUST increase the rank by 1 because the tree gets taller
        else:
            self.parent[root_y] = root_x # set PARENT of root_y = root_x
            self.rank[root_x] += 1       # INCREMENT rank/height of root_x (has a new child node)

        self.count -= 1
        return True

    def is_connected(self, x, y):
        return self.find(x) == self.find(y)

    def get_count(self):
        """Get number of disjoint sets"""
        return self.count
```

## 14. LRU Cache

```python
class LRUNode:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> node
        self.head = LRUNode()  # Dummy head
        self.tail = LRUNode()  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key):
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self.remove(node)
        self.add(node)
        return node.val

    def put(self, key, value):
        if key in self.cache:
            prev_node = self.cache[key]
            self.remove(prev_node)
        
        node = Node(key, value)
        self.cache[key] = node
        self.add(node)

        if len(self.cache) > self.size:
            lruNode = self.head.next
            self.remove(lruNode)
            del self.cache[lruNode.key]

    def remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def add(self, node):
        prev_end = self.tail.prev
        prev_end.next = node
        node.prev = prev_end
        node.next = self.tail
        self.tail.prev = node
```

## Time Complexity Summary

| Data Structure | Insert | Delete | Search | Access |
|---------------|--------|--------|--------|--------|
| Array/List | O(n) | O(n) | O(n) | O(1) |
| Linked List | O(1)* | O(n) | O(n) | O(n) |
| Stack | O(1) | O(1) | O(n) | O(n) |
| Queue | O(1) | O(1) | O(n) | O(n) |
| Binary Tree | O(n) | O(n) | O(n) | O(n) |
| BST | O(log n)** | O(log n)** | O(log n)** | O(log n)** |
| Heap | O(log n) | O(log n) | O(n) | O(1) for min/max |
| Hash Table | O(1)*** | O(1)*** | O(1)*** | N/A |
| Trie | O(m)**** | O(m) | O(m) | N/A |
| Graph (Adj List) | O(1) | O(V+E) | O(V) | N/A |
| Union Find | O(α(n))† | N/A | O(α(n)) | N/A |

\* At head/tail
\** Average case, O(n) worst case
\*** Average case, O(n) worst case
\**** m = length of string
† α(n) = inverse Ackermann function, practically constant

## Interview Tips

1. **Know when to use each structure:**
   - Stack: Matching parentheses, function calls, undo operations
   - Queue: BFS, level-order traversal, sliding window
   - Heap: Top K problems, running median, merge K sorted lists
   - Trie: Autocomplete, spell checker, word search
   - Union Find: Connected components, cycle detection in undirected graph
   - LRU Cache: Caching with eviction policy

2. **Common patterns:**
   - Two pointers for linked lists (slow/fast for cycle detection)
   - Dummy nodes for linked list edge cases
   - Parent pointers for tree problems
   - Visited set for graph traversal

3. **Edge cases to consider:**
   - Empty structure
   - Single element
   - Cycles in graphs/linked lists
   - Null pointers in trees