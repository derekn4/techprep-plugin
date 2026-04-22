# DFS vs BFS: Key Indicators and Decision Guide

## 🔍 Choose DFS When You See These Keywords/Patterns

### 1. "All" or "Every" Solutions
- "Find **all paths** from A to B"
- "Generate **all permutations**"
- "Find **every possible** combination"
- "**All valid** arrangements"

**Why DFS:** Need to explore complete solution space systematically.

### 2. Backtracking Language
- "**Can you reach** the target?"
- "**Is it possible** to..."
- "Find **a valid** configuration"
- Problems involving **constraint satisfaction**

**Why DFS:** Natural fit for try-and-undo exploration.

### 3. Path-Dependent Problems
- "**Root-to-leaf** paths"
- "**Path sum** equals target"
- "**Sequence** of moves"
- Current state depends on **how you got there**

**Why DFS:** Maintains path context naturally through recursion stack.

### 4. Tree/Graph Structure Exploration
- "**Detect cycles** in directed graph"
- "**Topological sort**"
- "**Connected components**"
- "**Validate** binary search tree"

**Why DFS:** Uses recursion stack to track "currently exploring" path.

### 5. Memory Constraints
- Very **wide graphs/trees**
- Need **O(height)** space not **O(width)**
- "**Deep but narrow**" exploration preferred

**Why DFS:** Stack grows with depth, not breadth.

---

## 🌊 Choose BFS When You See These Keywords/Patterns

### 1. "Shortest" or "Minimum" or "Closest"
- "**Shortest path**" (unweighted)
- "**Minimum steps** to reach"
- "**Closest** node to target"
- "**Fewest** moves required"

**Why BFS:** First solution found is guaranteed shortest.

### 2. "Level" or "Layer" Processing
- "**Level-order** traversal"
- "Print nodes **by level**"
- "Process **layer by layer**"
- "**Width** of binary tree"

**Why BFS:** Natural level-by-level exploration.

### 3. "Spread" or "Expansion" Problems
- "**Flood fill**" algorithms
- "**Infection spread**" simulation
- "**Network propagation**"
- "Expanding **outward** from source"

**Why BFS:** Simulates natural spreading pattern.

### 4. Early Termination for "Any" Solution
- "**First** leaf node encountered"
- "**Minimum depth** of tree"
- "**Any** node satisfying condition" (when closer is better)

**Why BFS:** Finds nearby solutions first.

### 5. Unweighted Shortest Path
- "**Steps to transform** A to B"
- "**Minimum jumps** in array"
- "**Word ladder** problems"
- Any **unweighted graph** shortest path

**Why BFS:** Optimal for unweighted shortest path.

---

## 🚩 Red Flags - Choose Carefully

### When You See "Maximum Depth"
```
❌ Wrong intuition: "Deep = DFS"
✅ Correct thinking: 
  - If need to find THE maximum → DFS (must explore all)
  - If checking "depth exceeds limit" → Either works
```

### When You See "Count" Problems
```
❌ Wrong: Always use DFS for counting
✅ Correct:
  - Count all paths → DFS
  - Count nodes at distance K → BFS
```

---

## 📋 Quick Decision Framework

### Ask These Questions:

1. **"Do I need ALL solutions or just ONE?"**
   - ALL → DFS
   - ONE (and closer is better) → BFS

2. **"Does the PATH matter or just the DESTINATION?"**
   - PATH matters → DFS
   - Just DESTINATION → BFS

3. **"Am I looking for SHORTEST or just ANY?"**
   - SHORTEST → BFS
   - ANY → Either (DFS often simpler)

4. **"Do I need to process by LEVELS?"**
   - YES → BFS
   - NO → Either

5. **"Is the graph WIDE or DEEP?"**
   - WIDE → DFS (memory)
   - DEEP → BFS (avoid stack overflow)

---

## 📊 Common Problem Patterns

| Problem Type | Algorithm | Key Indicator |
|--------------|-----------|---------------|
| **Shortest Path (unweighted)** | BFS | "shortest", "minimum steps" |
| **All Paths** | DFS | "all", "every path" |
| **Cycle Detection** | DFS | Need to track current path |
| **Level Order** | BFS | "level", "layer" |
| **Backtracking** | DFS | "can you", "is possible" |
| **Flood Fill** | BFS | "spread", "expand" |
| **Tree Validation** | DFS | Need full tree context |
| **Minimum Depth** | BFS | "minimum", early termination |

---

## 🎯 Real Examples

**"Find if there's a path with sum = target"** → **DFS**
- Key: "path" (sequence matters), backtracking

**"Find shortest path between two cities"** → **BFS**
- Key: "shortest", unweighted

**"Print all permutations of array"** → **DFS**
- Key: "all", backtracking needed

**"Find minimum number of steps to solve puzzle"** → **BFS**
- Key: "minimum steps", shortest path

**"Detect cycle in directed graph"** → **DFS**
- Key: Need to track current exploration path

**"Find width of binary tree"** → **BFS**
- Key: Level-by-level processing

---

## 🧠 Memory Tips

### DFS is like exploring a maze:
- Go as **deep** as possible
- **Backtrack** when you hit a dead end
- Remember where you've **been** (recursion stack)
- Good for finding **all possible paths**

### BFS is like ripples in a pond:
- **Expand outward** from the source
- **Closest first**, then farther away
- Good for finding the **nearest** or **shortest** solution
- Process **level by level**

---

## ⚡ Quick Reference

**See these words? Use DFS:**
- all, every, possible, can you, is it possible, paths, backtrack, validate

**See these words? Use BFS:**
- shortest, minimum, closest, first, level, layer, spread, flood

**The key is pattern recognition** - once you identify these indicators, the choice becomes almost automatic!

---

## 🔄 Converting Between DFS and BFS

### The Core Difference: Data Structure

The **only structural difference** between DFS and BFS is the data structure used:
- **DFS**: Uses a **Stack** (LIFO - Last In, First Out)
- **BFS**: Uses a **Queue** (FIFO - First In, First Out)

**Everything else stays the same!** Same visited set, same neighbor exploration, same graph structure.

---

## 🔁 BFS → DFS Conversion

### Step-by-Step Conversion:

1. **Replace Queue with Stack**
   ```python
   # BFS
   queue = deque([start])

   # DFS
   stack = [start]  # or deque() works too
   ```

2. **Change pop operation**
   ```python
   # BFS
   node = queue.popleft()  # Pop from front

   # DFS
   node = stack.pop()      # Pop from back
   ```

3. **Keep everything else the same**
   - Visited set
   - Neighbor exploration
   - Early termination conditions
   - Return values

### Example: Finding if Path Exists

**BFS Version:**
```python
def hasPath_BFS(graph, start, end):
    queue = deque([start])
    visited = set([start])

    while queue:
        node = queue.popleft()  # ← Queue: FIFO

        if node == end:
            return True

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return False
```

**DFS Version (Iterative):**
```python
def hasPath_DFS(graph, start, end):
    stack = [start]         # ← Stack instead of queue
    visited = set([start])

    while stack:
        node = stack.pop()  # ← Stack: LIFO (only change!)

        if node == end:
            return True

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)  # Same append!

    return False
```

**The ONLY change:** `queue.popleft()` → `stack.pop()`

---

## 🔁 DFS → BFS Conversion

### Step-by-Step Conversion:

1. **If DFS is recursive, first convert to iterative** (using explicit stack)
2. **Replace Stack with Queue**
3. **Change pop to popleft**

### Example: Level Order Traversal

**DFS Version (Recursive - with level tracking):**
```python
def levelOrder_DFS(root):
    result = []

    def dfs(node, level):
        if not node:
            return

        if len(result) == level:
            result.append([])

        result[level].append(node.val)
        dfs(node.left, level + 1)
        dfs(node.right, level + 1)

    dfs(root, 0)
    return result
```

**BFS Version:**
```python
def levelOrder_BFS(root):
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        current_level = []

        for _ in range(level_size):
            node = queue.popleft()
            current_level.append(node.val)

            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        result.append(current_level)

    return result
```

---

## 📝 Conversion Cheat Sheet

### Iterative DFS ↔ BFS Conversion

| Component | DFS (Stack) | BFS (Queue) |
|-----------|-------------|-------------|
| **Data Structure** | `stack = [start]` | `queue = deque([start])` |
| **Import** | None needed | `from collections import deque` |
| **Pop operation** | `node = stack.pop()` | `node = queue.popleft()` |
| **Add operation** | `stack.append(neighbor)` | `queue.append(neighbor)` |
| **Visited tracking** | Same | Same |
| **Neighbor loop** | Same | Same |

---

## 🔄 Recursive DFS → Iterative DFS (First Step for Conversion)

### Template:

**Recursive DFS:**
```python
def dfs_recursive(node, visited):
    if node in visited:
        return

    visited.add(node)
    # Process node

    for neighbor in graph[node]:
        dfs_recursive(neighbor, visited)
```

**Iterative DFS (using explicit stack):**
```python
def dfs_iterative(start):
    stack = [start]
    visited = set()

    while stack:
        node = stack.pop()

        if node in visited:
            continue

        visited.add(node)
        # Process node

        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)
```

**Then convert to BFS:** Just change `stack.pop()` to `queue.popleft()` and use `deque`!

---

## ⚠️ Important Differences in Behavior

### 1. Order of Exploration

**DFS:** Explores deepest first
```
Graph:    1
         / \
        2   3
       / \
      4   5

DFS order: 1 → 3 → 2 → 5 → 4  (goes deep on right first)
```

**BFS:** Explores level by level
```
Same graph:

BFS order: 1 → 2 → 3 → 4 → 5  (level by level)
```

### 2. When Results Differ

**Finding "any" path:** Both work, may find different paths
- DFS might find a deeper path first
- BFS might find a shallower path first

**Finding "shortest" path:** Results can differ!
- DFS: May not find shortest (finds first complete path)
- BFS: Always finds shortest (in unweighted graphs)

### 3. Memory Usage

**DFS:** O(depth) - stack grows with depth
**BFS:** O(width) - queue grows with level width

Converting doesn't change this fundamental difference!

---

## 🎯 Practical Conversion Examples

### Example 1: Clone Graph

**BFS Version:**
```python
def cloneGraph_BFS(node):
    if not node:
        return None

    clones = {node: Node(node.val)}
    queue = deque([node])

    while queue:
        curr = queue.popleft()

        for neighbor in curr.neighbors:
            if neighbor not in clones:
                clones[neighbor] = Node(neighbor.val)
                queue.append(neighbor)

            clones[curr].neighbors.append(clones[neighbor])

    return clones[node]
```

**DFS Version (just change data structure):**
```python
def cloneGraph_DFS(node):
    if not node:
        return None

    clones = {node: Node(node.val)}
    stack = [node]  # ← Changed from queue

    while stack:
        curr = stack.pop()  # ← Changed from popleft()

        for neighbor in curr.neighbors:
            if neighbor not in clones:
                clones[neighbor] = Node(neighbor.val)
                stack.append(neighbor)  # ← Same append

            clones[curr].neighbors.append(clones[neighbor])

    return clones[node]
```

### Example 2: Number of Islands

**DFS Version (Recursive):**
```python
def numIslands_DFS(grid):
    if not grid:
        return 0

    count = 0

    def dfs(i, j):
        if i < 0 or i >= len(grid) or j < 0 or j >= len(grid[0]):
            return
        if grid[i][j] == '0':
            return

        grid[i][j] = '0'  # Mark as visited
        dfs(i+1, j)
        dfs(i-1, j)
        dfs(i, j+1)
        dfs(i, j-1)

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '1':
                dfs(i, j)
                count += 1

    return count
```

**BFS Version:**
```python
def numIslands_BFS(grid):
    if not grid:
        return 0

    count = 0

    def bfs(i, j):
        queue = deque([(i, j)])
        grid[i][j] = '0'

        while queue:
            x, y = queue.popleft()

            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                    if grid[nx][ny] == '1':
                        grid[nx][ny] = '0'
                        queue.append((nx, ny))

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == '1':
                bfs(i, j)
                count += 1

    return count
```

---

## 🔑 Key Takeaways

1. **DFS and BFS are structurally identical** except for the data structure (Stack vs Queue)

2. **To convert BFS → DFS:**
   - Replace `queue = deque()` with `stack = []`
   - Replace `queue.popleft()` with `stack.pop()`
   - Everything else stays the same!

3. **To convert DFS → BFS:**
   - If recursive, first make it iterative with explicit stack
   - Replace stack with queue
   - Replace `pop()` with `popleft()`

4. **The conversion is mechanical, but results may differ:**
   - Exploration order changes
   - DFS won't guarantee shortest path
   - BFS won't explore all paths efficiently

5. **When to actually convert:**
   - You realize mid-interview you need shortest path (BFS)
   - You realize you need all paths (DFS)
   - Memory constraints change
   - You're more comfortable with one implementation

**Remember:** The algorithm choice matters more than the implementation style. Choose the right tool for the problem, then implement it in the style you're most comfortable with!