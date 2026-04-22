# Backtracking and Dynamic Programming Guide

## Backtracking

### What is Backtracking?
Backtracking is a systematic method for solving problems by trying partial solutions and abandoning them if they don't lead to a complete solution. Think of it as "try, and if it doesn't work, undo and try something else."

### Backtracking Template
```python
def backtrack(path, options):
    # Base case: found a complete solution
    if is_valid_solution(path):
        result.append(path[:])  # Make a copy!
        return

    # Try each possible choice
    for choice in options:
        # Make choice
        path.append(choice)

        # Recurse with remaining options
        backtrack(path, get_next_options(choice))

        # Undo choice (backtrack)
        path.pop()
```

### Common Backtracking Problems

#### 1. Permutations
```python
def permute(nums):
    result = []

    def backtrack(path):
        # Base case: path is complete
        if len(path) == len(nums):
            result.append(path[:])
            return

        # Try each unused number
        for num in nums:
            if num not in path:  # Check if available
                path.append(num)  # Choose
                backtrack(path)   # Explore
                path.pop()        # Unchoose

    backtrack([])
    return result
```

#### 2. Combinations
```python
def combine(n, k):
    result = []

    def backtrack(path, start):
        # Base case: combination is complete
        if len(path) == k:
            result.append(path[:])
            return

        # Try numbers from start to n
        for i in range(start, n + 1):
            path.append(i)        # Choose
            backtrack(path, i + 1) # Explore (i+1 to avoid duplicates)
            path.pop()            # Unchoose

    backtrack([], 1)
    return result
```

#### 3. Subsets
```python
def subsets(nums):
    result = []

    def backtrack(path, start):
        # Every path is a valid subset
        result.append(path[:])

        # Try adding each remaining element
        for i in range(start, len(nums)):
            path.append(nums[i])     # Choose
            backtrack(path, i + 1)   # Explore
            path.pop()               # Unchoose

    backtrack([], 0)
    return result
```

#### 4. N-Queens
```python
def solveNQueens(n):
    result = []
    board = [['.' for _ in range(n)] for _ in range(n)]

    def is_safe(row, col):
        # Check column
        for i in range(row):
            if board[i][col] == 'Q':
                return False

        # Check diagonal (top-left to bottom-right)
        i, j = row - 1, col - 1
        while i >= 0 and j >= 0:
            if board[i][j] == 'Q':
                return False
            i -= 1
            j -= 1

        # Check diagonal (top-right to bottom-left)
        i, j = row - 1, col + 1
        while i >= 0 and j < n:
            if board[i][j] == 'Q':
                return False
            i -= 1
            j += 1

        return True

    def backtrack(row):
        # Base case: placed all queens
        if row == n:
            result.append([''.join(row) for row in board])
            return

        # Try placing queen in each column of current row
        for col in range(n):
            if is_safe(row, col):
                board[row][col] = 'Q'    # Choose
                backtrack(row + 1)       # Explore
                board[row][col] = '.'    # Unchoose

    backtrack(0)
    return result
```

#### 5. Word Search
```python
def exist(board, word):
    if not board or not board[0]:
        return False

    m, n = len(board), len(board[0])

    def backtrack(row, col, index):
        # Base case: found complete word
        if index == len(word):
            return True

        # Check bounds and character match
        if (row < 0 or row >= m or col < 0 or col >= n or
            board[row][col] != word[index] or board[row][col] == '#'):
            return False

        # Mark as visited
        temp = board[row][col]
        board[row][col] = '#'

        # Explore all 4 directions
        found = (backtrack(row + 1, col, index + 1) or
                backtrack(row - 1, col, index + 1) or
                backtrack(row, col + 1, index + 1) or
                backtrack(row, col - 1, index + 1))

        # Restore original value (backtrack)
        board[row][col] = temp

        return found

    # Try starting from each cell
    for i in range(m):
        for j in range(n):
            if backtrack(i, j, 0):
                return True
    return False
```

#### 6. Generate Parentheses
```python
def generateParenthesis(n):
    result = []

    def backtrack(path, open_count, close_count):
        # Base case: used all parentheses
        if len(path) == 2 * n:
            result.append(path)
            return

        # Add opening parenthesis if we have quota
        if open_count < n:
            backtrack(path + '(', open_count + 1, close_count)

        # Add closing parenthesis if it would be valid
        if close_count < open_count:
            backtrack(path + ')', open_count, close_count + 1)

    backtrack('', 0, 0)
    return result
```

### Backtracking Tips

1. **Identify the choices:** What decisions can you make at each step?
2. **Define constraints:** When is a partial solution invalid?
3. **Recognize base case:** When have you found a complete solution?
4. **Make and unmake:** Always undo your choice after exploring
5. **Avoid duplicate work:** Use start indices or visited sets appropriately

### Common Backtracking Patterns

- **Permutations:** Use all elements, different orders
- **Combinations:** Choose k elements from n, order doesn't matter
- **Subsets:** All possible combinations (k from 0 to n)
- **Constraint satisfaction:** N-Queens, Sudoku
- **Path finding:** Word search, maze solving

## Dynamic Programming

### What is Dynamic Programming?
Dynamic Programming solves complex problems by breaking them into simpler subproblems, solving each subproblem once, and storing the results. It's optimization through **memoization** (avoiding recomputation).

### The DP Mindset - Visualization Strategy

#### 1. **Think Recursively First**
Before jumping to DP, think: "How would I solve this with pure recursion?"
- What's the base case?
- What's the recursive relationship?
- What parameters change between recursive calls?

#### 2. **Identify the Subproblems Visually**
Draw out the recursion tree to see overlapping subproblems:

**Example: Fibonacci**
```
                    fib(5)
                   /      \
               fib(4)      fib(3)
              /     \     /      \
          fib(3)  fib(2) fib(2)  fib(1)
         /     \
     fib(2)  fib(1)
```
Notice: fib(3) and fib(2) are computed multiple times!

#### 3. **The DP State Visualization Process**

**Step 1: Identify what changes**
- What parameters does the recursive function take?
- These become your DP state dimensions

**Step 2: Draw the DP table**
- 1D problem → 1D array
- 2D problem → 2D matrix
- Each cell represents a subproblem's answer

**Step 3: Find the direction**
- How do you fill the table?
- What cells do you need to compute current cell?

### The 5-Step DP Process

#### Step 1: Identify if it's DP
**Two key properties:**
1. **Optimal Substructure:** Solution can be built from optimal solutions to subproblems
2. **Overlapping Subproblems:** Same subproblems are solved multiple times

**Signals it might be DP:**
- "Maximum/minimum" with choices
- "How many ways" to do something
- "Can you reach" a target
- Problem has recursive structure

#### Step 2: Define the State
**Ask: What information do I need to solve any subproblem?**

Examples:
- `dp[i]` = answer for first i elements
- `dp[i][j]` = answer for range [i,j] or using first i items with weight limit j
- `dp[i][j][k]` = answer at position (i,j) with k moves left

#### Step 3: Find the Recurrence Relation
**Ask: How does the current state relate to previous states?**

Common patterns:
- **Choice:** `dp[i] = max(choice1, choice2, choice3)`
- **Sum:** `dp[i] = dp[i-1] + dp[i-2]`
- **Range:** `dp[i][j] = min(dp[i][k] + dp[k+1][j])` for all k

#### Step 4: Handle Base Cases
**Ask: What are the simplest subproblems I can solve directly?**
- Empty array, single element
- Zero capacity, first row/column

#### Step 5: Determine Fill Order
**Ask: What order should I fill the DP table?**
- Make sure when computing `dp[i]`, all dependencies are already computed

### Visual DP Problem Solving Examples

#### Example 1: Climbing Stairs
**Problem:** n steps, can climb 1 or 2 steps. How many ways to reach top?

**Step 1: Recursive thinking**
```python
def climbStairs(n):
    if n <= 1: return 1
    return climbStairs(n-1) + climbStairs(n-2)
```

**Step 2: Visualize the state**
```
dp[i] = number of ways to reach step i

Step:  0  1  2  3  4  5
Ways: [1, 1, 2, 3, 5, 8]
       ^  ^
   base cases
```

**Step 3: Recurrence**
```
dp[i] = dp[i-1] + dp[i-2]
```

**Implementation:**
```python
def climbStairs(n):
    if n <= 1: return 1

    dp = [0] * (n + 1)
    dp[0], dp[1] = 1, 1

    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]

    return dp[n]
```

#### Example 2: House Robber
**Problem:** Array of house values, can't rob adjacent houses. Maximum money?

**Step 1: Recursive thinking**
At each house, you have 2 choices:
- Rob this house + best from houses[0...i-2]
- Skip this house + best from houses[0...i-1]

**Step 2: Visualize the state**
```
houses: [2, 7, 9, 3, 1]
dp[i] = max money from first i+1 houses

i:     0  1  2  3  4
dp:   [2, 7, 11, 11, 12]
```

**Step 3: Recurrence**
```
dp[i] = max(dp[i-1], dp[i-2] + houses[i])
        skip    rob this house
```

**Implementation:**
```python
def rob(nums):
    if not nums: return 0
    if len(nums) == 1: return nums[0]

    dp = [0] * len(nums)
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])

    for i in range(2, len(nums)):
        dp[i] = max(dp[i-1], dp[i-2] + nums[i])

    return dp[-1]
```

#### Example 3: Coin Change
**Problem:** Given coins and amount, minimum coins to make amount?

**Step 1: Visualize the state**
```
dp[amount] = minimum coins to make this amount

coins = [1, 3, 4], amount = 6
dp:  [0, 1, 2, 1, 1, 2, 2]
amt:  0  1  2  3  4  5  6
```

**Step 2: Recurrence thinking**
For amount i, try each coin:
```
dp[i] = min(dp[i-coin] + 1) for all coins <= i
```

**Implementation:**
```python
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1
```

#### Example 4: Longest Increasing Subsequence (LIS)
**Problem:** Find length of longest increasing subsequence.

**Step 1: Define state**
```
dp[i] = length of LIS ending at position i
```

**Step 2: Visualize**
```
arr: [10, 9, 2, 5, 3, 7, 101, 18]
dp:  [1,  1, 1, 2, 2, 3, 4,   4]
```

**Step 3: Recurrence**
```
dp[i] = max(dp[j] + 1) for all j < i where arr[j] < arr[i]
```

**Implementation:**
```python
def lengthOfLIS(nums):
    if not nums: return 0

    dp = [1] * len(nums)

    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)
```

### 2D DP - Grid Problems

#### Example: Unique Paths
**Problem:** Robot at top-left, can only move right/down, paths to bottom-right?

**Visualize the DP table:**
```
3x7 grid:
dp[i][j] = paths to reach cell (i,j)

    0  1  2  3  4  5  6
0  [1, 1, 1, 1, 1, 1, 1]
1  [1, 2, 3, 4, 5, 6, 7]
2  [1, 3, 6,10,15,21,28]
```

**Recurrence:**
```
dp[i][j] = dp[i-1][j] + dp[i][j-1]
```

### Common DP Patterns & When to Use

#### 1. **Linear DP** (1D array)
- **When:** Problem on sequence/array, answer depends on previous elements
- **Examples:** Climbing stairs, house robber, coin change
- **Pattern:** `dp[i] = f(dp[i-1], dp[i-2], ...)`

#### 2. **Grid DP** (2D array)
- **When:** Problems on 2D grid, paths, or comparing two sequences
- **Examples:** Unique paths, edit distance, LCS
- **Pattern:** `dp[i][j] = f(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])`

#### 3. **Interval DP** (Range DP)
- **When:** Problem on ranges/intervals, optimal way to merge
- **Examples:** Matrix chain multiplication, palindrome partitioning
- **Pattern:** `dp[i][j] = min/max(dp[i][k] + dp[k+1][j])` for all k

#### 4. **Tree DP**
- **When:** Optimization on trees
- **Examples:** House robber III, diameter of tree
- **Pattern:** Answer at node depends on children's answers

#### 5. **Knapsack DP**
- **When:** Selecting items with weight/value constraints
- **Examples:** 0/1 knapsack, subset sum, partition equal subset
- **Pattern:** `dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight] + value)`

### Top-Down vs Bottom-Up

#### Top-Down (Memoization)
**When to use:**
- Natural recursive structure
- Not all subproblems needed
- Easier to think about

```python
def fib(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]
```

#### Bottom-Up (Tabulation)
**When to use:**
- Need to solve all subproblems anyway
- Want to optimize space
- Iterative approach preferred

```python
def fib(n):
    if n <= 1: return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

### DP Debugging & Visualization Tips

#### 1. **Print the DP table**
```python
# After filling dp table
for i in range(len(dp)):
    print(f"dp[{i}] = {dp[i]}")
```

#### 2. **Trace through small examples**
- Use n=3 or n=4 first
- Manually compute first few values
- Verify recurrence works

#### 3. **Draw state transitions**
```
For dp[i], what previous states do I need?
dp[3] ← dp[2] + dp[1]
       ← dp[1] + dp[0]
```

#### 4. **Check base cases carefully**
- Are they handled correctly?
- Do they make logical sense?

#### 5. **Verify with brute force**
- Implement naive recursive solution
- Compare outputs on small inputs

### Red Flags - When DP Might Not Work
- No overlapping subproblems (use divide & conquer)
- No optimal substructure (greedy might work)
- Problem asks for specific solution, not optimal value
- State space is too large (exponential in input)

### Interview DP Strategy
1. **Always start with recursive solution**
2. **Identify repeated subproblems**
3. **Define DP state clearly**
4. **Write recurrence relation**
5. **Trace through small example**
6. **Implement bottom-up**
7. **Consider space optimization**

### Understanding DP Array Indices - What Do They Mean?

Understanding what DP indices **represent** is crucial for mastering DP. The indices define the **subproblem you're solving**.

#### 1D DP Arrays - `dp[i]`

**Common Meanings:**
- **`dp[i]`** = answer for **first i elements** of input
- **`dp[i]`** = answer when **current position is i**
- **`dp[i]`** = answer for **target value i**
- **`dp[i]`** = answer **ending at position i**

**Examples:**

**Type 1: "First i elements"**
```python
# Climbing Stairs: dp[i] = ways to reach step i
dp[3] = ways to reach step 3

# House Robber: dp[i] = max money from first i+1 houses
dp[2] = max money from houses[0], houses[1], houses[2]
```

**Type 2: "Current position i"**
```python
# Jump Game: dp[i] = can we reach the end from position i?
dp[3] = can we reach the end starting from index 3?

# Decode Ways: dp[i] = number of ways to decode string starting at position i
dp[2] = ways to decode s[2:] (substring from index 2 to end)
```

**Type 3: "Target value i"**
```python
# Coin Change: dp[i] = min coins to make amount i
dp[5] = min coins to make amount 5

# Perfect Squares: dp[i] = min perfect squares that sum to i
dp[12] = min squares to sum to 12
```

**Type 4: "Ending at position i"**
```python
# LIS: dp[i] = length of LIS ending at index i
dp[3] = length of increasing subsequence ending at arr[3]

# Maximum Subarray: dp[i] = max sum ending at index i
dp[2] = max subarray sum ending at arr[2]
```

#### 2D DP Arrays - `dp[i][j]`

**Common Meanings:**

**Type 1: "Range/Interval problems"**
```python
# dp[i][j] = answer for range [i, j]
# Palindrome: dp[i][j] = is substring [i,j] palindrome?
dp[1][4] = is s[1:5] a palindrome?

# Matrix Chain: dp[i][j] = min cost to multiply matrices [i,j]
dp[0][3] = min cost for matrices[0] * matrices[1] * matrices[2] * matrices[3]
```

**Type 2: "Two sequences/arrays"**
```python
# Edit Distance: dp[i][j] = min edits to transform s1[0:i] to s2[0:j]
dp[3][2] = min edits to transform first 3 chars of s1 to first 2 chars of s2

# LCS: dp[i][j] = length of LCS of s1[0:i] and s2[0:j]
dp[4][3] = LCS length of s1[0:4] and s2[0:3]
```

**Type 3: "Grid coordinates"**
```python
# Unique Paths: dp[i][j] = paths to reach cell (i,j)
dp[2][3] = number of paths to reach row 2, col 3

# Min Path Sum: dp[i][j] = min sum to reach cell (i,j)
dp[1][2] = minimum path sum to reach grid[1][2]
```

**Type 4: "Items and capacity"**
```python
# Knapsack: dp[i][w] = max value using first i items with weight limit w
dp[3][10] = max value using items[0,1,2] with weight limit 10

# Subset Sum: dp[i][j] = can we make sum j using first i numbers?
dp[4][15] = can we make sum 15 using nums[0,1,2,3]?
```

#### 3D DP Arrays - `dp[i][j][k]`

**Common Meanings:**

**Type 1: "Position + state"**
```python
# Stock with Cooldown: dp[i][j][k] = max profit at day i, holding j stocks, k transactions
dp[5][1][2] = max profit at day 5, holding 1 stock, after 2 transactions

# Robot with moves: dp[i][j][k] = ways to reach (i,j) with exactly k moves
dp[2][3][5] = ways to reach (2,3) using exactly 5 moves
```

**Type 2: "Three sequences/dimensions"**
```python
# 3D Grid: dp[i][j][k] = paths to reach cell (i,j,k) in 3D space
dp[1][2][3] = paths to reach point (1,2,3)

# Three strings LCS: dp[i][j][k] = LCS of s1[0:i], s2[0:j], s3[0:k]
dp[3][4][2] = LCS of first 3 chars of s1, 4 chars of s2, 2 chars of s3
```

#### Visual Examples

**1D Example: Coin Change**
```python
coins = [1, 3, 4], target = 6
dp[amount] = min coins to make this amount

Index meaning: dp[i] = "min coins needed to make amount i"

dp[0] = 0    # 0 coins needed for amount 0
dp[1] = 1    # 1 coin (use coin 1) for amount 1
dp[2] = 2    # 2 coins (use coin 1 twice) for amount 2
dp[3] = 1    # 1 coin (use coin 3) for amount 3
dp[4] = 1    # 1 coin (use coin 4) for amount 4
dp[5] = 2    # 2 coins (use coin 4 + coin 1) for amount 5
dp[6] = 2    # 2 coins (use coin 3 twice) for amount 6
```

**2D Example: Edit Distance**
```python
s1 = "cat", s2 = "dog"
dp[i][j] = min edits to transform s1[0:i] to s2[0:j]

Index meaning:
- i = how many characters from s1 we're considering
- j = how many characters from s2 we're considering

    ""  d  o  g
""   0  1  2  3
c    1  1  2  3
a    2  2  2  3
t    3  3  3  3

dp[2][1] = min edits to transform "ca" → "d" = 2
dp[3][3] = min edits to transform "cat" → "dog" = 3
```

**3D Example: Stock with Transactions**
```python
prices = [3,2,6,5,0,3], max_k = 2
dp[i][j][k] = max profit at day i, with j transactions, holding k stocks

Index meaning:
- i = which day (0 to len(prices))
- j = how many transactions completed (0 to max_k)
- k = currently holding stock? (0 = no, 1 = yes)

dp[3][1][0] = max profit at day 3, completed 1 transaction, not holding stock
dp[5][2][1] = max profit at day 5, completed 2 transactions, holding stock
```

#### Key Insights for Index Meanings

**1. "First i" vs "Position i"**
```python
# "First i elements" - dp[i] includes elements [0...i-1]
dp[3] represents first 3 elements: arr[0], arr[1], arr[2]

# "Position i" - dp[i] is specifically about index i
dp[3] represents what happens at arr[3]
```

**2. Inclusive vs Exclusive ranges**
```python
# dp[i][j] for range [i,j] - be clear if inclusive/exclusive
dp[1][4] could mean:
- s[1:4] = characters at indices 1,2,3 (exclusive end)
- s[1:5] = characters at indices 1,2,3,4 (inclusive end)
```

**3. Base cases match index meaning**
```python
# If dp[i] = "answer for first i elements"
dp[0] = answer for 0 elements (empty case)

# If dp[i] = "answer ending at position i"
dp[0] = answer for just arr[0]
```

#### Pro Tips for DP Indices
1. **Always write down what your indices mean** before coding
2. **Check if your base cases match the index meaning**
3. **Trace through dp[0], dp[1], dp[2] manually** to verify
4. **Be consistent** - don't mix "first i" with "position i" interpretations

Understanding index meanings is the key to setting up DP correctly and avoiding off-by-one errors!