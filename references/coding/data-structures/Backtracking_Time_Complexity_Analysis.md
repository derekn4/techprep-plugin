# Backtracking Time Complexity Analysis Guide

Backtracking problems often have complex time complexity equations. This guide will help you systematically analyze and understand them.

---

## Core Framework for Analyzing Backtracking Complexity

### Step 1: Identify the Decision Tree Structure

Ask these questions:
1. **How many choices at each level?** (branches per node)
2. **How deep is the recursion tree?** (maximum depth)
3. **How much work is done at each node?** (operations per recursive call)

**Formula:**
```
Time Complexity = (# of nodes in tree) × (work per node)
```

---

## Common Backtracking Patterns

### Pattern 1: Binary Choices (Include/Exclude)

**Example:** Subsets, Combination Sum

**Structure:**
- Each element has 2 choices: include or exclude
- N elements → tree depth = N
- Each level has 2 branches

**Decision Tree:**
```
                    []
            /                \
        [1]                    []
       /      \              /    \
    [1,2]      [1]        [2]       []
    /   \      / \        / \       / \
[1,2,3][1,2][1,3][1]  [2,3] [2]    [3][]
```

**Analysis:**
- Depth: N (one level per element)
- Branches: 2 per node (include or exclude)
- Total nodes: 2^0 + 2^1 + 2^2 + ... + 2^N = 2^(N+1) - 1 ≈ **O(2^N)**
- Work per node: O(1) for decision, O(N) if copying current path

**Final Complexity:** **O(2^N × N)** if copying paths, **O(2^N)** if just counting

---

### Pattern 2: K-way Choices (Permutations)

**Example:** Permutations, N-Queens

**Structure:**
- First level: N choices
- Second level: N-1 choices (one already used)
- Third level: N-2 choices
- ...
- Last level: 1 choice

**Decision Tree for [1,2,3]:**
```
                    []
          /         |         \
        [1]        [2]        [3]
       /  \       /  \       /  \
    [1,2][1,3] [2,1][2,3] [3,1][3,2]
      |    |     |    |     |    |
   [1,2,3][1,3,2][2,1,3][2,3,1][3,1,2][3,2,1]
```

**Analysis:**
- Level 1: N nodes (N choices)
- Level 2: N × (N-1) nodes
- Level 3: N × (N-1) × (N-2) nodes
- ...
- Level N: N! nodes (all permutations)

**Total nodes:** N + N×(N-1) + N×(N-1)×(N-2) + ... + N!
- This is dominated by the last level: **O(N!)**
- Work per node: O(N) to copy permutation when found

**Final Complexity:** **O(N! × N)**

---

### Pattern 3: Variable Choices (Combination Sum - Unlimited Use)

**Example:** Combination Sum (can reuse elements)

**Structure:**
- Each level can choose any of N elements
- Depth is limited by target sum / min element
- Maximum depth: target / min_value

**Analysis:**
- Branches: N per node (can choose any element)
- Depth: T / M where T = target, M = min element value
- Total nodes: N^0 + N^1 + N^2 + ... + N^(T/M) ≈ **O(N^(T/M))**

**Final Complexity:** **O(N^(T/M))**

---

### Pattern 4: Reducing Choices (Combination Sum II - Use Once)

**Example:** Combination Sum II, Subsets II (with duplicates)

**Structure:**
- First level: N choices
- Second level: N-1 choices (start from next index)
- Third level: N-2 choices
- But we prune duplicates

**Analysis:**
- Without pruning: **O(2^N)** (same as binary choice)
- With duplicate pruning: Still **O(2^N)** worst case
  - Best case with many duplicates: Much better in practice
  - But asymptotic complexity unchanged

**Final Complexity:** **O(2^N × N)** (N for copying paths)

---

## Step-by-Step Analysis Examples

### Example 1: Combination Sum II

**Problem:** Find unique combinations that sum to target, each element used once

**Code Structure:**
```python
def backtrack(start, current, sum):
    if sum == target:
        result.append(current[:])  # O(N) to copy
        return

    for i in range(start, len(candidates)):  # N-start iterations
        if i > start and candidates[i] == candidates[i-1]:
            continue  # Skip duplicates

        current.append(candidates[i])
        backtrack(i+1, current, sum + candidates[i])
        current.pop()
```

**Step 1: Decision Tree Structure**
- Binary choice per element (include or skip)
- Depth: N (at most)
- Branches: 2 per node (but pruned)

**Step 2: Count Nodes**
- Worst case: No pruning, all elements considered
- Nodes at depth d: 2^d
- Total nodes: 2^0 + 2^1 + ... + 2^N = **2^(N+1) - 1 ≈ O(2^N)**

**Step 3: Work Per Node**
- Decision: O(1)
- Copying path when found: O(N)
- How often do we copy? At most 2^N leaf nodes

**Step 4: Combine**
- Nodes: O(2^N)
- Work per node: O(N) for copying
- **Total: O(2^N × N)**

**Space Complexity:**
- Recursion stack: O(N) depth
- Current path: O(N)
- Result storage: O(2^N × N) - not counted in auxiliary space
- **Auxiliary Space: O(N)**

---

### Example 2: Permutations

**Problem:** Generate all permutations of [1,2,3,...,N]

**Code Structure:**
```python
def backtrack(current, remaining):
    if not remaining:
        result.append(current[:])  # O(N) to copy
        return

    for i in range(len(remaining)):  # N, then N-1, then N-2, ...
        backtrack(
            current + [remaining[i]],
            remaining[:i] + remaining[i+1:]
        )
```

**Step 1: Decision Tree Structure**
- K-way choice: N choices at level 1, N-1 at level 2, etc.
- Depth: N

**Step 2: Count Nodes**
- Level 0: 1 node (root)
- Level 1: N nodes
- Level 2: N × (N-1) nodes
- Level 3: N × (N-1) × (N-2) nodes
- ...
- Level N: N! nodes (leaf permutations)

**Total nodes:** 1 + N + N×(N-1) + ... + N!
- Sum is dominated by last term
- **Nodes ≈ O(N!)**

**Step 3: Work Per Node**
- At each node, we create new lists (current + remaining)
- Copying current: O(N)
- Creating remaining: O(N)
- **Work per node: O(N)**

**Step 4: Combine**
- Nodes: O(N!)
- Work per node: O(N)
- **Total: O(N! × N)**

---

### Example 3: Subsets

**Problem:** Generate all subsets of [1,2,3,...,N]

**Code Structure:**
```python
def backtrack(start, current):
    result.append(current[:])  # O(N) - called at EVERY node!

    for i in range(start, len(nums)):
        current.append(nums[i])
        backtrack(i+1, current)
        current.pop()
```

**Step 1: Decision Tree Structure**
- Binary choice: include or exclude each element
- Depth: N

**Step 2: Count Nodes**
- This visits EVERY node in the tree, not just leaves
- Total nodes: 2^0 + 2^1 + 2^2 + ... + 2^N = **2^(N+1) - 1 ≈ O(2^N)**

**Step 3: Work Per Node**
- We copy at EVERY node (not just leaves)
- Average subset size: N/2
- **Work per node: O(N/2) ≈ O(N)**

**Step 4: Combine**
- Nodes: O(2^N)
- Work per node: O(N) on average
- **Total: O(2^N × N)**

**Key Insight:**
- Subsets problem adds result at every node
- Most backtracking problems only add at leaves
- But complexity is similar because there are many more leaves than internal nodes

---

### Example 4: N-Queens

**Problem:** Place N queens on N×N board

**Code Structure:**
```python
def backtrack(row, board):
    if row == n:
        result.append(convert_board(board))  # O(N^2)
        return

    for col in range(n):  # N choices per row
        if is_safe(row, col, board):  # O(N) to check
            board[row][col] = 'Q'
            backtrack(row+1, board)
            board[row][col] = '.'
```

**Step 1: Decision Tree Structure**
- N choices per row (which column to place queen)
- N rows (depth)
- But heavily pruned by `is_safe` check

**Step 2: Count Nodes**
- Without pruning: N^N nodes (N choices, N levels)
- With pruning: Much less, but hard to calculate exactly
- **Worst case: O(N^N)** but in practice much better

**Step 3: Work Per Node**
- is_safe check: O(N) to check row/col/diagonals
- Converting board when found: O(N^2)

**Step 4: Combine**
- Nodes: O(N!) in practice (one queen per row, reducing choices)
- Work per node: O(N)
- **Practical: O(N! × N)**
- **Worst case: O(N^N × N)**

---

## Quick Reference Table

| Problem Type | Choices per Level | Depth | Nodes | Work per Node | Time Complexity |
|--------------|-------------------|-------|-------|---------------|-----------------|
| **Subsets** | 2 (include/exclude) | N | 2^N | O(N) copy | **O(2^N × N)** |
| **Combinations** | 2 (include/skip) | N | 2^N | O(N) copy | **O(2^N × N)** |
| **Permutations** | N, N-1, N-2, ... | N | N! | O(N) copy | **O(N! × N)** |
| **Combination Sum** (reuse) | N (any element) | T/M | N^(T/M) | O(1) | **O(N^(T/M))** |
| **Partition Problems** | Varies | N | 2^N | O(N) | **O(2^N × N)** |
| **N-Queens** | N (pruned) | N | N! | O(N) check | **O(N!)** |

Where:
- N = number of elements
- T = target sum
- M = minimum element value

---

## How to Quickly Estimate in Interviews

### 1. Identify the Pattern

**Ask:** "What choices do I have at each step?"
- **2 choices** (include/exclude) → O(2^N)
- **K choices decreasing** (N, N-1, ...) → O(N!)
- **K constant choices** → O(K^depth)

### 2. Calculate Depth

**Ask:** "When does recursion stop?"
- Fixed depth (one per element) → O(N)
- Sum-based depth → O(target/min)
- All elements used → O(N)

### 3. Estimate Work Per Node

**Ask:** "What operations happen at each recursive call?"
- Just decisions → O(1)
- Copying array/list → O(N)
- Checking validity → O(N) or O(1) depending on problem

### 4. Combine Using Multiplication

```
Time = (# of nodes) × (work per node)
```

### 5. Don't Forget Space Complexity

**Recursion stack:** Same as tree depth
**Current path:** O(N) for most problems
**Result storage:** Don't count in auxiliary space (it's output)

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Forgetting the Copy Cost

```python
# WRONG analysis: "Just O(2^N) because binary choices"
result.append(current[:])  # This is O(N) work!
# CORRECT: O(2^N × N)
```

### ❌ Mistake 2: Overcounting Pruned Branches

```python
# Saying O(N^N) for N-Queens
# Reality: Heavy pruning makes it closer to O(N!)
```

### ❌ Mistake 3: Confusing Nodes with Leaves

- **Subsets:** Adds at every node → 2^N nodes
- **Combinations:** Adds only at leaves with sum==target → fewer nodes
- Still O(2^N) for complexity (all nodes explored)

### ❌ Mistake 4: Not Considering Best/Average/Worst Cases

- Backtracking can vary wildly based on input
- Always state: "Worst case O(2^N)" not just "O(2^N)"

---

## Interview Communication Template

When asked about backtracking time complexity, use this structure:

```
"Let me analyze the decision tree:

1. **Choices per level:** [describe: 2, N, N-1, etc.]

2. **Tree depth:** [N, target/min, etc.]

3. **Number of nodes:** [2^N, N!, etc.]
   - This comes from [branches]^[depth]
   - [mention any pruning]

4. **Work per node:** [O(1), O(N) for copying, etc.]

5. **Total time complexity:** [nodes] × [work] = O(...)

For space:
- Recursion stack: O([depth])
- Current path: O([size])
- Total auxiliary space: O(...)
"
```

---

## Practice Problems by Complexity

### O(2^N × N) - Binary Choice
- ✓ Subsets
- ✓ Subsets II
- ✓ Combination Sum II
- ✓ Partition Equal Subset Sum

### O(N! × N) - Permutation
- ✓ Permutations
- ✓ Permutations II
- ✓ N-Queens
- ✓ Sudoku Solver (O(9^(n×n)) worst case)

### O(N^(T/M)) - Unlimited Reuse
- ✓ Combination Sum
- ✓ Coin Change II (DP is better, but backtracking possible)

### O(2^N × N^2) - Extra Work Per Node
- ✓ Palindrome Partitioning (checking palindrome is O(N))
- ✓ Word Search II (trie traversal adds cost)

---

## Summary

**Three Steps to Analyze Any Backtracking Problem:**

1. **Draw the decision tree** (even if just mentally)
   - What choices at each level?
   - How deep does it go?

2. **Count nodes in tree**
   - Binary choice → 2^N
   - K-way decreasing → N!
   - K-way constant → K^depth

3. **Multiply by work per node**
   - Usually O(N) for copying
   - Sometimes O(1) for just counting
   - Sometimes O(N) for validation

**Most backtracking problems fall into these categories:**
- **O(2^N)** for subset/combination problems
- **O(N!)** for permutation problems
- **Multiply by O(N)** if copying paths/results

When in doubt, say: **"The decision tree has [branches] choices and [depth] levels, giving O([branches]^[depth]) nodes, with O([work]) work per node, so total is O([final answer])"**

This systematic approach will help you confidently analyze any backtracking problem in interviews!
