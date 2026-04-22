# Tricky Algorithms & Patterns to Remember

## 🎯 QuickSelect (Kth Element)
**Time:** O(n) average, O(n²) worst case  
**Space:** O(1) iterative, O(log n) recursive stack average, O(n) worst  
**When to use:** "Find kth largest/smallest", "Find median", single element selection, when you don't need all k elements sorted
```python
def quickselect(nums, k):
    # Convert kth largest to (n-k)th smallest
    target = len(nums) - k
    
    def partition(left, right):
        pivot = nums[right]
        i = left
        for j in range(left, right):
            if nums[j] <= pivot:
                nums[i], nums[j] = nums[j], nums[i]
                i += 1
        nums[i], nums[right] = nums[right], nums[i]
        return i
    
    def select(left, right):
        pivot = partition(left, right)
        if pivot == target:
            return nums[pivot]
        elif pivot < target:
            return select(pivot + 1, right)
        else:
            return select(left, pivot - 1)
    
    return select(0, len(nums) - 1)
```
**Remember:** Better than heap for single kth element. Use randomized pivot for better average case.

## 🎯 Sliding Window Pattern
**Time:** O(n)  
**Space:** O(1) for fixed window, O(k) for variable window with hashmap  
**When to use:** "Maximum/minimum in subarray of size k", "Longest substring with condition", "Substring with k distinct characters", consecutive elements problems
```python
# Fixed window
def maxSumSubarray(nums, k):
    window_sum = sum(nums[:k])
    max_sum = window_sum
    
    for i in range(k, len(nums)):
        window_sum = window_sum - nums[i-k] + nums[i]
        max_sum = max(max_sum, window_sum)
    return max_sum

# Variable window (two pointers)
def longestSubstringKDistinct(s, k):
    left = 0
    char_count = {}
    max_len = 0
    
    for right in range(len(s)):
        char_count[s[right]] = char_count.get(s[right], 0) + 1
        
        while len(char_count) > k:
            char_count[s[left]] -= 1
            if char_count[s[left]] == 0:
                del char_count[s[left]]
            left += 1
        
        max_len = max(max_len, right - left + 1)
    return max_len
```

## 🎯 Cycle Detection (Floyd's Algorithm)
**Time:** O(n)  
**Space:** O(1)  
**When to use:** "Detect cycle in linked list", "Find duplicate number", "Find start of cycle", any problem with limited value range that maps to itself
```python
# Linked List Cycle
def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False

# Find duplicate in array [1,n] with n+1 elements
def findDuplicate(nums):
    slow = fast = nums[0]
    
    # Find intersection
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    
    # Find entrance
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
```

## 🎯 Binary Search Variations
**Time:** O(log n)  
**Space:** O(1)  
**When to use:** Sorted array search, "Find first/last occurrence", "Search in rotated array", "Find peak element", "Find minimum in rotated array", any monotonic condition
```python
# Find first occurrence
def firstOccurrence(nums, target):
    left, right = 0, len(nums) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            result = mid
            right = mid - 1  # Keep searching left
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result

# Search in rotated array
def searchRotated(nums, target):
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        
        # Left half is sorted
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Right half is sorted
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

## 🎯 Monotonic Stack
**Time:** O(n) - each element pushed/popped once  
**Space:** O(n) - stack can contain all elements  
**When to use:** "Next/previous greater/smaller element", "Largest rectangle in histogram", "Trapping rain water", "Daily temperatures", maintain increasing/decreasing order
```python
# Next Greater Element
def nextGreater(nums):
    result = [-1] * len(nums)
    stack = []  # stores indices
    
    for i in range(len(nums)):
        while stack and nums[stack[-1]] < nums[i]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)
    return result

# Largest Rectangle in Histogram
def largestRectangle(heights):
    stack = []
    max_area = 0
    
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height_idx = stack.pop()
            height = heights[height_idx]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    
    while stack:
        height_idx = stack.pop()
        height = heights[height_idx]
        width = len(heights) if not stack else len(heights) - stack[-1] - 1
        max_area = max(max_area, height * width)
    
    return max_area
```

## 🎯 Union Find (Disjoint Set)
**Time:** O(α(n)) ≈ O(1) for find/union with path compression and union by rank  
**Space:** O(n) for parent and rank arrays  
**When to use:** "Number of connected components", "Detect cycle in undirected graph", "Accounts merge", "Number of islands (alternative to DFS)", dynamic connectivity queries
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        
        # Union by rank
        if self.rank[px] < self.rank[py]:
            self.parent[px] = py
        elif self.rank[px] > self.rank[py]:
            self.parent[py] = px
        else:
            self.parent[py] = px
            self.rank[px] += 1
        return True
```

## 🎯 Trie (Prefix Tree)
**Time:** O(m) for insert/search where m = word length  
**Space:** O(ALPHABET_SIZE * m * n) where n = number of words  
**When to use:** "Word search", "Autocomplete", "Spell checker", "Prefix matching", "Longest common prefix", multiple string queries with common prefixes
```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
    
    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_word
    
    def startsWith(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True
```

## 🎯 Topological Sort (Kahn's Algorithm)
**Time:** O(V + E) where V = vertices, E = edges  
**Space:** O(V + E) for graph representation and queue  
**When to use:** "Course schedule", "Task dependencies", "Build order", "Alien dictionary", any DAG ordering problem, detecting cycles in directed graphs
```python
def topologicalSort(num_courses, prerequisites):
    graph = [[] for _ in range(num_courses)]
    in_degree = [0] * num_courses
    
    # Build graph
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1
    
    # Find all nodes with no incoming edges
    queue = [i for i in range(num_courses) if in_degree[i] == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result if len(result) == num_courses else []
```

## 🎯 Kadane's Algorithm (Max Subarray)
**Time:** O(n)  
**Space:** O(1)  
**When to use:** "Maximum sum subarray", "Maximum product subarray" (modified), "Best time to buy/sell stock", any contiguous subarray optimization problem
```python
def maxSubarray(nums):
    max_sum = current_sum = nums[0]
    
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    return max_sum
```

## 🎯 Dutch National Flag (3-way partition)
**Time:** O(n) - single pass  
**Space:** O(1) - in-place sorting  
**When to use:** "Sort colors (0,1,2)", "Sort array with 3 distinct values", "Partition around pivot", "Move zeros to end", any 3-way partitioning
```python
def sortColors(nums):  # 0s, 1s, 2s
    low = curr = 0
    high = len(nums) - 1
    
    while curr <= high:
        if nums[curr] == 0:
            nums[low], nums[curr] = nums[curr], nums[low]
            low += 1
            curr += 1
        elif nums[curr] == 2:
            nums[curr], nums[high] = nums[high], nums[curr]
            high -= 1
            # Don't increment curr!
        else:  # nums[curr] == 1
            curr += 1
```

## 🎯 Reservoir Sampling
**Time:** O(n) where n = stream size  
**Space:** O(1) for single item, O(k) for k items  
**When to use:** "Random selection from stream", "Select k items from unknown size", "Linked list random node", when you can't store all elements in memory
```python
import random

def getRandom(stream):
    result = None
    count = 0
    
    for item in stream:
        count += 1
        # Keep item with probability 1/count
        if random.randint(1, count) == 1:
            result = item
    
    return result
```

## 🎯 Bit Manipulation Tricks
**Time:** O(1) for most operations, O(log n) for counting bits  
**Space:** O(1)  
**When to use:** "Single number" problems, "Power of 2", "Count bits", "Missing number", XOR for finding unique elements, optimizing space for boolean arrays
```python
# Check if power of 2
def isPowerOfTwo(n):
    return n > 0 and (n & (n - 1)) == 0

# Count set bits (Brian Kernighan)
def countBits(n):
    count = 0
    while n:
        n &= n - 1  # Clear lowest set bit
        count += 1
    return count

# Find single number (all others appear twice)
def singleNumber(nums):
    result = 0
    for num in nums:
        result ^= num
    return result
```

## 🎯 Matrix Spiral Traversal
**Time:** O(m * n) where m = rows, n = columns  
**Space:** O(1) if not counting output, O(m * n) for result array  
**When to use:** "Spiral matrix", "Rotate matrix", "Snake pattern traversal", layer-by-layer processing, any problem requiring boundary shrinking
```python
def spiralOrder(matrix):
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        # Right
        for i in range(left, right + 1):
            result.append(matrix[top][i])
        top += 1
        
        # Down
        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1
        
        # Left (if row exists)
        if top <= bottom:
            for i in range(right, left - 1, -1):
                result.append(matrix[bottom][i])
            bottom -= 1
        
        # Up (if column exists)
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1
    
    return result
```

## 🔥 Quick Complexity Reminders

| Pattern | Time | Space | When to Use |
|---------|------|-------|------------|
| QuickSelect | O(n) avg | O(1) | Single kth element |
| MinHeap size k | O(n log k) | O(k) | Top k elements |
| Bucket Sort | O(n) | O(n) | Bounded range |
| Union Find | O(α(n))* | O(n) | Connected components |
| Monotonic Stack | O(n) | O(n) | Next greater/smaller |
| Sliding Window | O(n) | O(k) | Subarray/substring |
| Binary Search | O(log n) | O(1) | Sorted array |
| Trie | O(m) insert/search | O(ALPHABET_SIZE * m * n) | Prefix operations |

*α(n) is inverse Ackermann, practically constant

## 💡 Pattern Recognition Tips

1. **"Kth element"** → QuickSelect or Heap
2. **"Top/Bottom K"** → Heap or Bucket Sort if bounded
3. **"Consecutive/Subarray"** → Sliding Window or Kadane's
4. **"Next Greater"** → Monotonic Stack
5. **"Cycle Detection"** → Floyd's Tortoise & Hare
6. **"Connected Components"** → Union Find or DFS
7. **"Prefix matching"** → Trie
8. **"Course prerequisites"** → Topological Sort
9. **"Rotated array"** → Modified Binary Search
10. **"Three-way partition"** → Dutch National Flag