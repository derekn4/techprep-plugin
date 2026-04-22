# Stack (LIFO) Problem Patterns - Interview Guide

## When to Use Stack/LIFO

### 1. **Matching/Balancing Problems**
**Key Identifiers:** "valid parentheses", "matching brackets", "balanced", "nested pairs"
- Valid parentheses/brackets validation
- HTML/XML tag matching
- **Why LIFO:** The last opened bracket must be the first one closed
- **Example:** `"([)]"` is invalid, `"([])"` is valid

### 2. **Backtracking/Undo Operations**
**Key Identifiers:** "backtrack", "undo", "reverse last action", "path finding with retreat"
- Function call stack simulation
- Undo/redo functionality
- Maze solving with backtracking
- **Why LIFO:** Need to reverse the most recent action first
- **Example:** Browser back button, text editor undo

### 3. **Nested Structure Processing**
**Key Identifiers:** "nested", "recursive structure", "expression evaluation", "inner before outer"
- Expression evaluation (infix to postfix)
- Calculator with parentheses
- Tree traversal (iterative DFS)
- **Why LIFO:** Inner/deeper elements must be processed before outer ones
- **Example:** `"2 * (3 + 4)"` - must evaluate `(3 + 4)` first

### 4. **Monotonic Stack Problems**
**Key Identifiers:** "next greater/smaller", "previous greater/smaller", "maintaining order"
- Next greater element
- Daily temperatures (days until warmer)
- Stock span problems
- Largest rectangle in histogram
- **Why LIFO:** Maintain elements in decreasing/increasing order, pop when condition breaks
- **Example:** For array `[73, 74, 75, 71, 69, 72]`, find days until warmer temperature

### 5. **Reversal Problems**
**Key Identifiers:** "reverse", "last becomes first", "flip order"
- Reverse a string/array
- Palindrome validation
- **Why LIFO:** First elements in become last elements out
- **Example:** Reverse `"hello"` → `"olleh"`

## Code Pattern Examples

### Pattern 1: Matching Brackets
```python
def isValid(s):
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}

    for char in s:
        if char in pairs:  # Opening bracket
            stack.append(char)
        elif not stack or pairs[stack.pop()] != char:  # Closing bracket
            return False

    return len(stack) == 0
```

### Pattern 2: Monotonic Stack (Next Greater Element)
```python
def nextGreaterElement(nums):
    stack = []
    result = [-1] * len(nums)

    for i, num in enumerate(nums):
        while stack and nums[stack[-1]] < num:
            idx = stack.pop()
            result[idx] = num
        stack.append(i)

    return result
```

### Pattern 3: DFS with Stack (Tree Traversal)
```python
def inorderTraversal(root):
    stack, result = [], []
    current = root

    while stack or current:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right

    return result
```

## When NOT to Use Stack (Use Queue Instead)

### Use Queue for:
- **Level-order traversal:** Process nodes level by level (BFS)
- **Task scheduling:** First task in should be first processed
- **Moving average:** Sliding window with FIFO removal
- **Producer-consumer:** Process items in arrival order

### Key Differentiators:
| Problem Type | Stack (LIFO) | Queue (FIFO) |
|-------------|--------------|--------------|
| Tree Traversal | DFS (depth-first) | BFS (breadth-first) |
| Processing Order | Last In, First Out | First In, First Out |
| Problem Keywords | "nested", "matching", "backtrack" | "level", "order", "sequence" |
| Space Complexity | O(height) for trees | O(width) for trees |

## Interview Communication Tips

When choosing Stack in an interview:
1. **Be Decisive:** "I'll use a stack here because the LIFO property handles the matching brackets naturally"
2. **Show Understanding:** "The stack maintains the opening brackets in order, and we can validate each closing bracket against the most recent opening"
3. **Mention Alternatives:** "While we could track this with recursion, an explicit stack is more memory efficient and clearer"
4. **Identify Pattern:** "This is a classic monotonic stack problem - we maintain decreasing order and pop when we find a greater element"