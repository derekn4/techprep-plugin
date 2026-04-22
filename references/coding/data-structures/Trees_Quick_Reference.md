# 🌲 Trees Quick Reference Guide

## General Trees
- **N-ary:** Node can have any number of children
- **Common:** File systems, DOM, organization charts
- **Traversal:** Usually DFS or BFS with `for child in node.children`

## Binary Trees

### Properties
- Each node has ≤ 2 children (left, right)
- **Height:** Longest path from root to leaf
- **Depth:** Distance from root to node
- **Complete:** All levels filled except possibly last (filled left-to-right)
- **Perfect:** All internal nodes have 2 children, leaves at same level
- **Full:** Every node has 0 or 2 children

### Traversals
```python
# DFS
def preorder(root):   # Root → Left → Right
def inorder(root):    # Left → Root → Right
def postorder(root):  # Left → Right → Root

# BFS
def levelorder(root): # Level by level, use queue
```

### Common Patterns
- **Recursion:** Pass info down (parameters) or up (return values)
- **Height:** `1 + max(height(left), height(right))`
- **Diameter:** Max path between any two nodes
- **LCA:** Lowest Common Ancestor

## Binary Search Trees (BST)

### Property
`left < node < right` (for all descendants)

### Operations (avg O(log n), worst O(n))
- **Search:** Go left if target < node, right if >
- **Insert:** Search to find position, add as leaf
- **Delete:** 3 cases (leaf, 1 child, 2 children)
- **Min/Max:** Leftmost/rightmost node

### Key Insights
- **Inorder traversal gives sorted sequence**
- **Validation:** Pass min/max bounds, not just parent check
- **Kth smallest:** Inorder traversal, stop at k

## Balanced Trees (AVL, Red-Black)

### Purpose
Guarantee O(log n) height

### AVL Tree
- Balance factor: |height(left) - height(right)| ≤ 1
- More balanced, more rotations

### Red-Black Tree
- Rules about red/black coloring
- Less balanced, fewer rotations
- Used in: Java TreeMap, C++ STL map

**You need to know:** They exist, why they're useful, O(log n) guarantee

## Common Interview Problems

### Binary Tree
- Maximum depth/height
- Level order traversal
- Serialize/deserialize
- Path sum problems
- Tree diameter
- Invert/mirror tree
- Same/symmetric tree

### BST
- Validate BST
- LCA of BST (use BST property!)
- Kth smallest element
- Convert sorted array to BST
- BST iterator

## Key Code Patterns

```python
# Tree node definition
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Check if leaf
if not node.left and not node.right:

# DFS template
def dfs(node):
    if not node: return
    # process node
    dfs(node.left)
    dfs(node.right)

# BFS template
queue = deque([root])
while queue:
    node = queue.popleft()
    # process node
    if node.left: queue.append(node.left)
    if node.right: queue.append(node.right)

# Pass info down
def dfs(node, info):

# Pass info up
def dfs(node):
    return computed_value
```

## Time/Space Complexity
- **Traversal:** O(n) time, O(h) space (h = height)
- **Balanced operations:** O(log n) time
- **Unbalanced worst case:** O(n) time (linked list)

**Remember:** Trees are just graphs with no cycles and one root! 🎯