# Complete Guide to Recursive Paradigms

## Core Recursive Paradigms

### 1. **Backtracking**
**Purpose:** Generate all valid solutions by exploring possibilities systematically
**Pattern:** Try → Recurse → Undo (if invalid)
**Key Insight:** Explore all paths, backtrack when constraints violated

**When to Use:**
- "Generate all combinations/permutations"
- "Find all solutions"
- Constraint satisfaction problems
- Combinatorial generation

**Template:**
```python
def backtrack(current_state, remaining_choices):
    if is_complete(current_state):
        results.append(current_state[:])  # Copy
        return

    for choice in get_valid_choices(remaining_choices):
        # Make choice
        current_state.append(choice)
        # Recurse
        backtrack(current_state, updated_choices)
        # Undo choice (backtrack)
        current_state.pop()
```

**Examples:** Generate Parentheses, Permutations, N-Queens, Sudoku Solver

---

### 2. **Divide and Conquer**
**Purpose:** Break problem into smaller independent subproblems
**Pattern:** Divide → Conquer → Combine
**Key Insight:** Split problem, solve parts independently, merge solutions

**When to Use:**
- Problem can be split into independent subproblems
- Optimal substructure exists
- "Sort", "search", "find maximum/minimum"

**Template:**
```python
def divide_and_conquer(problem, left, right):
    # Base case
    if left >= right:
        return base_case_solution

    # Divide
    mid = (left + right) // 2
    left_result = divide_and_conquer(problem, left, mid)
    right_result = divide_and_conquer(problem, mid + 1, right)

    # Combine
    return combine_results(left_result, right_result, problem, left, mid, right)
```

**Examples:** Merge Sort, Quick Sort, Maximum Subarray, Binary Search

---

### 3. **Binary Choice Recursion**
**Purpose:** Make include/exclude decisions for each element
**Pattern:** Include path + Exclude path
**Key Insight:** Two recursive calls per element covering all possibilities

**When to Use:**
- "All possible subsets"
- "Include or exclude" decisions
- Power set generation
- Binary decisions at each step

**Template:**
```python
def binary_choice(arr, index, current):
    if index == len(arr):
        results.append(current[:])
        return

    # Include current element
    current.append(arr[index])
    binary_choice(arr, index + 1, current)
    current.pop()

    # Exclude current element
    binary_choice(arr, index + 1, current)
```

**Examples:** Subsets, Combination Sum, 0/1 Knapsack

---

### 4. **Tree/Graph Recursion**
**Purpose:** Traverse or process tree/graph structures
**Pattern:** Process node → Recurse on children/neighbors
**Key Insight:** Recursive structure matches data structure

**When to Use:**
- Tree traversals
- Graph exploration
- Hierarchical data processing
- Path finding in trees/graphs

**Tree Template:**
```python
def tree_recursion(node):
    if not node:
        return base_case

    # Process current node
    result = process_node(node)

    # Recurse on children
    left_result = tree_recursion(node.left)
    right_result = tree_recursion(node.right)

    # Combine results
    return combine(result, left_result, right_result)
```

**Graph Template:**
```python
def graph_dfs(node, visited):
    if node in visited:
        return

    visited.add(node)
    process_node(node)

    for neighbor in node.neighbors:
        graph_dfs(neighbor, visited)
```

**Examples:** Binary Tree Traversals, DFS, Path Sum, Clone Graph

---

### 5. **Constraint-Based Recursion**
**Purpose:** Generate solutions following specific rules/constraints
**Pattern:** Valid choice → Recurse → Backtrack
**Key Insight:** Use problem constraints to guide valid choices

**When to Use:**
- Problems with specific validity rules
- "Well-formed" requirements
- Constraint satisfaction with rules

**Template:**
```python
def constraint_recursion(current_state, constraints):
    if is_complete(current_state):
        results.append(build_solution(current_state))
        return

    for choice in get_valid_choices(constraints):
        if is_valid_choice(choice, current_state, constraints):
            make_choice(current_state, choice)
            updated_constraints = update_constraints(constraints, choice)
            constraint_recursion(current_state, updated_constraints)
            undo_choice(current_state, choice)
```

**Examples:** Generate Parentheses, Word Search, N-Queens

---

### 6. **Memoized Recursion (Top-Down DP)**
**Purpose:** Solve overlapping subproblems efficiently
**Pattern:** Check cache → Compute if not cached → Store result
**Key Insight:** Cache results to avoid recomputation

**When to Use:**
- Overlapping subproblems
- Optimal substructure
- "Find optimal solution"
- Can be solved recursively but has repeated calls

**Template:**
```python
def memoized_recursion(state, memo={}):
    # Check cache
    if state in memo:
        return memo[state]

    # Base case
    if is_base_case(state):
        return base_result

    # Recursive case
    result = compute_result(state)

    # Store in cache
    memo[state] = result
    return result
```

**Examples:** Fibonacci, Climbing Stairs, Longest Common Subsequence

---

### 7. **Tail Recursion**
**Purpose:** Optimize recursive calls by making recursion the last operation
**Pattern:** Accumulate result → Tail recursive call
**Key Insight:** Can be optimized to iterative by compiler

**When to Use:**
- Simple accumulation problems
- When stack overflow is a concern
- Linear recursive processes

**Template:**
```python
def tail_recursion(n, accumulator=initial_value):
    if n == base_case:
        return accumulator

    return tail_recursion(n - 1, update_accumulator(accumulator, n))
```

**Examples:** Factorial (tail version), Sum of numbers, List reversal

---

### 8. **Mutual Recursion**
**Purpose:** Two or more functions call each other recursively
**Pattern:** Function A calls Function B, Function B calls Function A
**Key Insight:** Models problems with alternating states/roles

**When to Use:**
- State machines
- Alternating processes
- Grammar parsing
- Game theory (player turns)

**Template:**
```python
def function_a(state):
    if base_case_a(state):
        return base_result_a

    # Process and call function_b
    new_state = transform_state_a(state)
    return function_b(new_state)

def function_b(state):
    if base_case_b(state):
        return base_result_b

    # Process and call function_a
    new_state = transform_state_b(state)
    return function_a(new_state)
```

**Examples:** Even/Odd checkers, Game playing algorithms, Parser states

---

### 9. **Nested Recursion**
**Purpose:** Recursive calls with recursive parameters
**Pattern:** Recurse on result of another recursion
**Key Insight:** Complex recursive relationships

**When to Use:**
- Ackermann function
- Complex mathematical sequences
- Nested data structures

**Template:**
```python
def nested_recursion(n, m):
    if base_case(n, m):
        return base_result

    # Recursive call with recursive parameter
    return nested_recursion(n - 1, nested_recursion(n, m - 1))
```

**Examples:** Ackermann function, Some tree operations

---

### 10. **Linear Recursion**
**Purpose:** Single recursive call per function execution
**Pattern:** Process → Single recursive call
**Key Insight:** Simplest form of recursion

**When to Use:**
- List processing
- Simple sequences
- Tree paths
- Linear data structures

**Template:**
```python
def linear_recursion(data, index=0):
    if index >= len(data):
        return base_result

    # Process current element
    current_result = process(data[index])

    # Single recursive call
    remaining_result = linear_recursion(data, index + 1)

    return combine(current_result, remaining_result)
```

**Examples:** List sum, Tree height, Binary search

---

## Quick Reference Guide

### Problem Type → Paradigm Mapping
- **"Generate all X"** → Backtracking
- **"Find optimal X"** → Memoized Recursion (DP)
- **"Sort/Search"** → Divide and Conquer
- **"Include/Exclude decisions"** → Binary Choice
- **"Tree/Graph problems"** → Tree/Graph Recursion
- **"Valid/Well-formed"** → Constraint-based
- **"Process list/sequence"** → Linear Recursion

### Complexity Patterns
- **Backtracking:** O(b^d) where b=branching factor, d=depth
- **Divide & Conquer:** Often O(n log n)
- **Binary Choice:** O(2^n)
- **Tree Recursion:** O(n) where n=nodes
- **Memoized:** O(unique subproblems)

### Common Mistakes to Avoid
1. **Forgetting base cases** → Infinite recursion
2. **Not making copies** → Reference issues in backtracking
3. **Missing backtrack step** → State pollution
4. **Incorrect state updates** → Wrong solutions
5. **No memoization for overlapping subproblems** → Exponential complexity