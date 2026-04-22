# Dynamic Programming: Fundamentals & Visualization Guide

## The Two Pillars of DP

**1. Overlapping Subproblems** = "I'm solving the same thing multiple times"
**2. Optimal Substructure** = "The best answer uses best answers from smaller problems"

---

## Building Intuition: From Recursion to DP Arrays

### Step 1: See the Repetition (Overlapping Subproblems)

Let's use **Fibonacci** - the "Hello World" of DP:

```
fib(5) = fib(4) + fib(3)
         /              \
    fib(4)              fib(3)
    /    \              /    \
 fib(3) fib(2)      fib(2) fib(1)
 /   \
fib(2) fib(1)
```

Notice: `fib(3)` appears **twice**, `fib(2)` appears **three times**. We're wasting work!

**Key insight**: If we could *remember* what `fib(3)` was the first time, we wouldn't need to recalculate it.

---

### Step 2: What Does the DP Array Store?

**The DP array stores answers to subproblems so we don't recalculate them.**

For Fibonacci:
- `dp[i]` = "What is the i-th Fibonacci number?"
- `dp[5]` stores the answer to `fib(5)`

---

## Visualizing DP Dimensions

**The number of dimensions = number of variables needed to uniquely identify a subproblem**

### 1D DP: One Variable Changes

**Example: Climbing Stairs** - "How many ways to reach step n?"

```
Subproblem: "How many ways to reach step i?"
Variable: i (the step number)
DP Array: dp[i] = ways to reach step i

dp[0] = 1 (one way to stay at ground)
dp[1] = 1 (one step)
dp[2] = 2 (1+1 or 2)
dp[3] = dp[2] + dp[1] = 3
```

**Visualization**:
```
Step:     0    1    2    3    4    5
dp:      [1,   1,   2,   3,   5,   8]
          ^    ^    ^
          |    |    |
        Start  Can come from step 0 or 1
```

---

### 2D DP: Two Variables Change

**Example: Unique Paths** - "Robot at top-left going to bottom-right of m×n grid"

```
Subproblem: "How many ways to reach cell (i, j)?"
Variables: i (row), j (column)
DP Array: dp[i][j] = ways to reach (i, j)
```

**Why 2D?** We need BOTH row AND column to identify which cell we're asking about.

**Visualization** (3×3 grid):
```
     j=0  j=1  j=2
i=0   1    1    1      ← Can only go right
i=1   1    2    3      ← dp[1][1] = dp[0][1] + dp[1][0]
i=2   1    3    6      ← dp[2][2] = dp[1][2] + dp[2][1]
      ↑
Only go down
```

Each cell asks: "How many ways to get HERE?" Answer: Add ways from top + ways from left.

---

### 3D DP: Three Variables Change

**Example: Knapsack with Item Count Limit** - "Max value with capacity W, using at most K items"

```
Subproblem: "Max value with first i items, capacity w, using ≤ k items?"
Variables: i (items considered), w (weight left), k (items left to use)
DP Array: dp[i][w][k] = max value
```

**Why 3D?** Need item index, weight capacity, AND count limit to identify the state.

**Visualization** (Hard to draw, so think of it as):
- A **book** with multiple pages
- Each page is a 2D grid for different values of k
- Page k=0: 2D grid of (items × weight) when using 0 items
- Page k=1: 2D grid of (items × weight) when using ≤1 item
- Page k=2: 2D grid of (items × weight) when using ≤2 items

---

## How to Decide Dimensions: Ask These Questions

1. **What am I trying to find?** (This is usually your answer)
2. **What changes between subproblems?** (These become your indices)
3. **How many independent things vary?** (This is your dimension count)

### Practice: Analyzing Problems

**Problem 1: Longest Increasing Subsequence (LIS)**
- Q: "What's the longest increasing subsequence ending at index i?"
- Variables: Just `i` (position in array)
- **1D**: `dp[i]` = length of LIS ending at i

**Problem 2: Edit Distance** (transform string s to string t)
- Q: "Min edits to transform s[0..i] into t[0..j]?"
- Variables: `i` (position in s), `j` (position in t)
- **2D**: `dp[i][j]` = min edits to transform s[0..i] → t[0..j]

**Problem 3: Best Time to Buy/Sell Stock with Cooldown**
- Q: "Max profit by day i, and am I currently holding a stock?"
- Variables: `i` (day), `holding` (0 or 1)
- **2D**: `dp[i][holding]` = max profit at day i with hold state

---

## The DP Recipe (5 Steps)

1. **Define the subproblem** - "dp[...] represents ___"
2. **Identify base cases** - What are the trivial answers?
3. **Find the recurrence relation** - How do smaller problems build the answer?
4. **Determine order of computation** - Fill the array in what order?
5. **Extract final answer** - Where in the array is your answer?

---

## Detailed 2D Example: Longest Common Subsequence (LCS)

**Problem**: Find longest common subsequence of "ABCD" and "AEBD"

**Step 1: Define subproblem**
```
dp[i][j] = length of LCS of s1[0..i-1] and s2[0..j-1]
```

**Step 2: Base cases**
```
dp[0][j] = 0 (empty first string)
dp[i][0] = 0 (empty second string)
```

**Step 3: Recurrence**
```
If s1[i-1] == s2[j-1]:
    dp[i][j] = dp[i-1][j-1] + 1  (match! extend previous LCS)
Else:
    dp[i][j] = max(dp[i-1][j], dp[i][j-1])  (skip from one string)
```

**Step 4: Visualize the table**
```
      ""  A  E  B  D
""     0  0  0  0  0
A      0  1  1  1  1   ← A matches A
B      0  1  1  2  2   ← B matches B
C      0  1  1  2  2   ← C matches nothing
D      0  1  1  2  3   ← D matches D
         ↑  ↑     ↑
       Match E  Match D
```

**Step 5: Answer**
`dp[4][4] = 3` → LCS is "ABD"

---

## Understanding DP Array Indices

### What do indices typically represent?

**dp[variables] = answer to the subproblem identified by these variables**

### Type 1: "Up to i" (Prefix-based)

**dp[i] = answer for input[0...i]** or **"first i elements"**

**Examples:**
- **Climbing Stairs**: `dp[i]` = ways to reach step i
- **House Robber**: `dp[i]` = max money robbing houses 0 to i
- **LIS**: `dp[i]` = length of longest increasing subseq ending at i
- **Fibonacci**: `dp[i]` = i-th Fibonacci number

**Key characteristic**: You're building up from the start, each step depends on previous steps.

---

### Type 2: "State at i" (State-based)

**dp[i] = answer when you're IN state i** (not necessarily "up to")

**Examples:**
- **0/1 Knapsack**: `dp[i][w]` = max value considering items 0 to i with capacity w
  - Not just "items up to i", but "items 0 to i **with remaining capacity w**"

- **Edit Distance**: `dp[i][j]` = min edits to transform s1[0..i] → s2[0..j]
  - Two independent positions, not "up to"

- **Stock with Cooldown**: `dp[i][holding]` = max profit at day i, currently holding stock (0/1)
  - The state is day i **combined with** whether you hold stock

---

### Quick Test for Each Index:

Ask: **"If I change this index, does the problem change?"**

**1D Example - House Robber:**
- `dp[5]` = max money from houses 0-5
- `dp[6]` = max money from houses 0-6
- Index changes → different prefix → **1D**

**2D Example - Edit Distance:**
- `dp[3][5]` = min edits for s1[0..3] → s2[0..5]
- `dp[3][6]` = min edits for s1[0..3] → s2[0..6] (different!)
- `dp[4][5]` = min edits for s1[0..4] → s2[0..5] (different!)
- Both indices matter → **2D**

---

### Common DP Index Meanings:

| Index Type | Meaning | Example |
|------------|---------|---------|
| `dp[i]` | Answer for prefix/first i elements | Coin Change, Climbing Stairs |
| `dp[i]` | Answer ending at position i | LIS, Max Subarray |
| `dp[i][j]` | Two sequences at positions i, j | LCS, Edit Distance |
| `dp[i][w]` | Position i with capacity/limit w | Knapsack |
| `dp[i][state]` | Position i in a specific state | Stock (hold/not hold) |
| `dp[L][R]` | Subproblem on range [L, R] | Palindrome partitioning |

---

## Three Common Patterns for 2D DP

### Pattern 1: Range DP → dp[i][j] = answer for range [i, j]

**"What's the answer for the subarray/substring from index i to j?"**

**Examples:**
- **Longest Palindromic Substring**: `dp[i][j]` = is s[i..j] a palindrome?
- **Matrix Chain Multiplication**: `dp[i][j]` = min cost to multiply matrices i through j
- **Burst Balloons**: `dp[i][j]` = max coins from bursting balloons i to j

**Visual for "ABCBA":**
```
     j=0  j=1  j=2  j=3  j=4
i=0   T    F    F    F    T     ← s[0..4] = "ABCBA" is palindrome
i=1   -    T    F    T    F     ← s[1..3] = "BCB" is palindrome
i=2   -    -    T    F    F
i=3   -    -    -    T    F
i=4   -    -    -    -    T
```

**Key trait**: Usually fill **diagonally** or by **increasing length**, because `dp[i][j]` depends on smaller ranges inside [i, j]

---

### Pattern 2: Two Sequences DP → dp[i][j] = answer for prefix of two inputs

**"What's the answer considering first i elements of sequence1 and first j elements of sequence2?"**

**Examples:**
- **Longest Common Subsequence**: `dp[i][j]` = LCS length of s1[0..i-1] and s2[0..j-1]
- **Edit Distance**: `dp[i][j]` = min edits to transform s1[0..i-1] → s2[0..j-1]
- **Distinct Subsequences**: `dp[i][j]` = count of s2[0..j-1] in s1[0..i-1]

**Visual for LCS("ABC", "AC"):**
```
        ""  A  C
    ""   0  0  0
    A    0  1  1  ← Matched 'A'
    B    0  1  1  ← 'B' doesn't help
    C    0  1  2  ← Matched 'A' and 'C'
```

**Key trait**: Fill **row by row** or **column by column**, like reading a table left-to-right, top-to-bottom

---

### Pattern 3: Position + State DP → dp[i][j] = answer at position i in state j

**"What's the answer at position i when I'm in state j?"**

Here `j` is NOT a position, but a **state/condition/capacity/limit**

**Examples:**
- **0/1 Knapsack**: `dp[i][w]` = max value with first i items, capacity w
  - `i` = items considered
  - `w` = remaining weight capacity (not a position!)

- **Stock with Transaction Limit**: `dp[i][k]` = max profit at day i with k transactions left
  - `i` = day
  - `k` = transactions remaining (not a position!)

- **Paint House**: `dp[i][color]` = min cost to paint first i houses, house i is `color`
  - `i` = house number
  - `color` = 0/1/2 (red/blue/green, not a position!)

**Visual for Knapsack with items [w:1,v:1], [w:2,v:6], [w:3,v:10], capacity=5:**
```
         w=0  w=1  w=2  w=3  w=4  w=5
item 0    0    0    0    0    0    0
item 1    0    1    1    1    1    1   ← Item 1: weight 1, value 1
item 2    0    1    6    7    7    7   ← Item 2: weight 2, value 6
item 3    0    1    6   10   11   16   ← Item 3: weight 3, value 10
```

**Key trait**: One dimension is position, other is a **constraint or state variable**

---

### How to Tell Them Apart?

**Question 1: "Are there TWO sequences/strings/arrays?"**
- **YES** → Probably **Pattern 2** (Two Sequences)
- **NO** → Keep asking...

**Question 2: "Is the second index also a position/range in the SAME input?"**
- **YES** → Probably **Pattern 1** (Range DP)
- **NO** → Probably **Pattern 3** (Position + State)

---

### Examples to Practice:

**Problem A**: "Min cost to cut a stick at positions [1,3,4,5] between 0 and 7"
- One input (the stick)
- Need subproblem for "cutting from position i to j"
- **Pattern 1: Range DP** → `dp[i][j]` = min cost to cut stick[i..j]

**Problem B**: "Count ways to form string t using characters from string s"
- Two strings
- **Pattern 2: Two Sequences** → `dp[i][j]` = ways using s[0..i] to form t[0..j]

**Problem C**: "Max profit buying/selling stock k times"
- One input (prices array)
- Second dimension is transaction count (a limit, not a position)
- **Pattern 3: Position + State** → `dp[i][k]` = max profit at day i with k transactions left

---

## Common Pitfalls

### Pitfall 1: "I don't know what dp[i] means!"

**Fix**: Always write down what your DP state represents in plain English FIRST.

❌ **Bad**:
```python
dp[i][j]  # some DP thing
```

✅ **Good**:
```python
# dp[i][j] = min edits to transform s1[0..i] into s2[0..j]
#   i = position in s1
#   j = position in s2
```

### Pitfall 2: Assuming all 2D DP is range-based

Only ~30% of 2D DP problems use range [i, j]. The other 70% are:
- **Pattern 2**: Two different sequences (40%)
- **Pattern 3**: Position + some state/constraint (30%)

### Pitfall 3: Not identifying the variables

Before coding, ask:
1. What am I trying to find?
2. What changes between subproblems?
3. How many independent things vary?

---

## Practice Problem: Coin Change

**Problem**: "Min coins to make amount n with coins [1,2,5]"

**Questions to ask:**
1. What changes between subproblems?
2. What do I need to track?
3. How many dimensions?

**Answer:**
- Variables: Just the amount (one number changes)
- **1D**: `dp[i]` = min coins to make amount i
- Recurrence: `dp[i] = min(dp[i - coin] + 1)` for each coin

---

## Summary Checklist

Before solving any DP problem:

1. ✅ Identify what makes each subproblem unique (your indices)
2. ✅ Count how many variables → that's your dimensions
3. ✅ Write down in plain English what `dp[i]` or `dp[i][j]` represents
4. ✅ For 2D, identify which pattern (Range, Two Sequences, or Position+State)
5. ✅ Define base cases
6. ✅ Write the recurrence relation
7. ✅ Determine fill order
8. ✅ Know where your final answer is

---

## Key Takeaways

- **DP dimensions** = number of variables that uniquely identify a subproblem
- **1D**: Usually "up to i" or "ending at i"
- **2D Pattern 1**: Range [i, j] in same sequence
- **2D Pattern 2**: Prefixes of two different sequences
- **2D Pattern 3**: Position + state/capacity/constraint
- **Always define your DP state explicitly before coding!**
