# Dynamic Programming: Complete Guide

## 🎯 What is Dynamic Programming?

Dynamic Programming (DP) is an optimization technique that solves complex problems by breaking them down into simpler subproblems. It's essentially **smart recursion with memory**.

Think of it as: *"I'm solving the same smaller problems over and over. What if I just solve each one ONCE and remember the answer?"*

---

## 🔑 Two Key Properties (Both Required!)

### 1. Optimal Substructure
**Definition:** The optimal solution to the big problem contains optimal solutions to smaller problems.

**Example:** In climbing stairs, to optimally count ways to reach step 4:
- I need the optimal count for step 3 AND step 2
- I don't need to worry about HOW I got to step 3 or step 2
- Structure: `ways(4) = ways(3) + ways(2)`

**Key insight:** Each subproblem has a definitive answer that we can use as a building block.

### 2. Overlapping Subproblems
**Definition:** Same subproblems are solved multiple times in the recursive approach.

**Example:** Calculating ways(5) recursively:
```
ways(5)
├── ways(4)
│   ├── ways(3)
│   │   ├── ways(2)
│   │   └── ways(1)
│   └── ways(2)  ← DUPLICATE!
└── ways(3)      ← DUPLICATE!
    ├── ways(2)  ← DUPLICATE!
    └── ways(1)
```

**Key insight:** Without memoization, we're solving ways(3) and ways(2) multiple times.

---

## 🚨 When to Use DP - Signal Words

Look for these patterns in problem statements:

### Optimization Problems
- "**Maximum/minimum**" with choices
- "**Best way**" to do something
- "**Optimal**" solution

### Counting Problems
- "**How many ways**" to do something
- "**Number of paths**"
- "**Count all possibilities**"

### Decision Problems
- "**Can you reach**" a target
- "**Is it possible**" to achieve something
- "**True/false**" with optimal substructure

### Other Indicators
- Problem has **recursive structure**
- **Multiple ways** to make decisions at each step
- **Choices** affect future possibilities

---

## 📐 DP in Different Dimensions

### 1D DP
**Pattern:** `dp[i]` = answer for input of size i

**Example: Climbing Stairs**
```python
def climbStairs(n):
    dp = [0] * (n + 1)
    dp[0] = 1  # Base case
    dp[1] = 1  # Base case
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]
```

**Array meaning:** `dp[i]` = number of ways to reach step i

### 2D DP
**Pattern:** `dp[i][j]` = answer considering first dimension up to i, second dimension up to j

**Example: Unique Paths in Grid**
```python
def uniquePaths(m, n):
    dp = [[0] * n for _ in range(m)]
    
    # Base cases
    for i in range(m):
        dp[i][0] = 1
    for j in range(n):
        dp[0][j] = 1
    
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
    
    return dp[m-1][n-1]
```

**Array meaning:** `dp[i][j]` = number of paths to reach cell at row i, column j

**Index breakdown:**
- `dp[2][1]` = paths to reach row 2, column 1
- `dp[1][2]` = paths to reach row 1, column 2

### 3D DP
**Pattern:** `dp[i][j][k]` = answer considering three constraints/dimensions up to i, j, and k

**Example: Edit Distance with Operation Limit**
```python
def editDistance(word1, word2, maxOps):
    m, n = len(word1), len(word2)
    dp = [[[float('inf')] * (maxOps + 1) for _ in range(n + 1)] for _ in range(m + 1)]
    
    # Base cases
    for k in range(maxOps + 1):
        dp[0][0][k] = 0
    
    for i in range(m + 1):
        for j in range(n + 1):
            for k in range(maxOps + 1):
                if i == 0 and j == 0:
                    continue
                
                # Try different operations...
                # Insert, delete, replace logic here
    
    return dp[m][n][maxOps]
```

**Array meaning:** `dp[i][j][k]` = minimum cost to transform first i characters of word1 into first j characters of word2 using at most k operations

**Index breakdown:**
- `i` = characters from word1 considered (0 to len(word1))
- `j` = characters from word2 targeted (0 to len(word2))
- `k` = maximum operations allowed (0 to maxOps)

---

## 🔄 DP vs Backtracking

### Similarities
1. **Recursive problem decomposition** - both break problems into smaller pieces
2. **Decision trees** - both explore possibilities
3. **Optimal substructure** - both rely on solutions to smaller problems

### Key Differences

| Aspect | DP | Backtracking |
|--------|----|-----------| 
| **Goal** | Find optimal value | Find valid solution(s) |
| **Optimal Substructure** | Required | Not required |
| **Overlapping Subproblems** | Required | Usually absent |
| **Key Technique** | Memoization | Pruning invalid branches |
| **When to use** | Optimization problems | Constraint satisfaction |

### Why Backtracking Usually Lacks Overlapping Subproblems

In backtracking, the **path taken matters**, making each recursive call represent a **different state**:

**Example: N-Queens**
- State with queens at [(0,1), (1,3)] ≠ State with queens at [(0,2), (1,0)]
- Different board configurations = different subproblems = no overlap

**Example: DP (Unique Paths)**
- Being at cell (2,3) is the same regardless of path taken
- Same position = same subproblem = overlap!

---

## 🛠️ DP Problem-Solving Steps

### Step 1: Identify if it's DP
- ✅ Has optimal substructure?
- ✅ Has overlapping subproblems?
- ✅ Involves optimization/counting/possibility?

### Step 2: Define the State
- What does `dp[i]` represent?
- What are the dimensions needed?
- What do the indices mean?

### Step 3: Find the Recurrence Relation
- How does `dp[i]` relate to smaller subproblems?
- What choices can be made at each step?

### Step 4: Determine Base Cases
- What are the simplest subproblems?
- What can be solved directly?

### Step 5: Decide on Implementation
- Top-down (memoization) or bottom-up (tabulation)?
- Space optimization possible?

---

## 💡 Common DP Patterns

### Pattern 1: Linear DP
```python
# dp[i] depends on dp[i-1], dp[i-2], etc.
dp[i] = some_function(dp[i-1], dp[i-2], ...)
```
**Examples:** Fibonacci, climbing stairs, house robber

### Pattern 2: Grid DP
```python
# dp[i][j] depends on dp[i-1][j], dp[i][j-1], etc.
dp[i][j] = some_function(dp[i-1][j], dp[i][j-1], ...)
```
**Examples:** Unique paths, minimum path sum

### Pattern 3: Interval DP
```python
# dp[i][j] represents optimal solution for interval [i, j]
dp[i][j] = min/max(dp[i][k] + dp[k+1][j] + cost) for k in range(i, j)
```
**Examples:** Matrix chain multiplication, palindrome partitioning

### Pattern 4: Knapsack DP
```python
# dp[i][w] = maximum value using first i items with weight limit w
dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight[i]] + value[i])
```
**Examples:** 0/1 knapsack, subset sum

---

## ⚡ Top-Down vs Bottom-Up

### Top-Down (Memoization)
```python
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]
```

**Pros:**
- ✅ Natural recursive thinking
- ✅ Only computes needed subproblems
- ✅ Easy to implement from recursive solution

**Cons:**
- ❌ Function call overhead
- ❌ Potential stack overflow
- ❌ May use more memory

### Bottom-Up (Tabulation)
```python
def fibonacci_tab(n):
    if n <= 1:
        return n
    
    dp = [0] * (n + 1)
    dp[1] = 1
    
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]
```

**Pros:**
- ✅ No function call overhead
- ✅ No stack overflow risk
- ✅ Often faster in practice
- ✅ Easy to optimize space

**Cons:**
- ❌ Must compute all subproblems
- ❌ Less intuitive for complex problems

---

## 🧠 Memory Tips

### The "Aha!" Moment
DP is recognizing: *"Wait, I'm solving the same smaller problems over and over. What if I just solve each one ONCE and remember the answer?"*

### Think of DP as:
- **Smart recursion** with a notebook
- **Avoiding repeated work** by caching results
- **Building up solutions** from smaller pieces

### Remember:
- **Without optimal substructure:** Can't break down reliably
- **Without overlapping subproblems:** No repeated work to save, so DP doesn't help

---

## 🎯 Quick Identification Guide

**See these phrases? Think DP:**
- "maximum/minimum value"
- "how many ways"
- "can you reach"
- "optimal solution"
- "count all possibilities"
- "best strategy"

**Ask yourself:**
1. Can I break this into smaller versions of the same problem?
2. Do I solve the same subproblems multiple times?
3. Does the optimal solution use optimal solutions to subproblems?

**If all three are YES → It's probably DP!**

---

## 🚀 Practice Strategy

1. **Start simple:** Master 1D DP first (Fibonacci, climbing stairs)
2. **Understand the pattern:** Focus on state definition and recurrence
3. **Draw it out:** Visualize the subproblem dependencies
4. **Practice both approaches:** Top-down and bottom-up
5. **Optimize gradually:** Space optimization comes after correctness

Remember: DP is about **pattern recognition**. The more problems you solve, the easier it becomes to spot the DP structure!