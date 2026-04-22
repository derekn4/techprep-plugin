# Python Interview Reference Guide

## Essential Built-in Data Structures

### 1. Lists
```python
arr = [1, 2, 3]
arr.append(4)          # O(1) - add to end
arr.pop()              # O(1) - remove from end
arr.pop(0)             # O(n) - remove from beginning
arr.insert(0, val)     # O(n) - insert at beginning
arr.extend([4, 5])     # O(k) - add multiple elements
arr.reverse()          # O(n) - reverse in-place
arr.sort()             # O(n log n) - sort in-place
sorted(arr)            # O(n log n) - returns new sorted list
arr[::-1]              # O(n) - reverse copy
arr[1:3]               # O(k) - slicing
```

### 2. Deque (Double-ended Queue)
```python
from collections import deque

dq = deque([1, 2, 3])
dq.append(4)           # O(1) - add to right
dq.appendleft(0)       # O(1) - add to left
dq.pop()               # O(1) - remove from right
dq.popleft()           # O(1) - remove from left
dq.rotate(1)           # O(k) - rotate right by k
dq.rotate(-1)          # O(k) - rotate left by k
```

### 3. Dictionaries (HashMap)
```python
d = {}
d = dict()
d = {'a': 1, 'b': 2}

d['key'] = value       # O(1) average - insert/update
val = d.get('key', 0)  # O(1) - get with default
'key' in d             # O(1) - check existence
del d['key']           # O(1) - delete key
d.pop('key', default)  # O(1) - remove and return
d.keys()               # O(1) - get keys view
d.values()             # O(1) - get values view
d.items()              # O(1) - get (key, val) pairs

# Useful patterns
d.setdefault('key', []).append(val)  # Append to list in dict
```

### 4. Sets
```python
s = set()
s = {1, 2, 3}

s.add(4)               # O(1) average - add element
s.remove(4)            # O(1) - remove (raises error if not found)
s.discard(4)           # O(1) - remove (no error if not found)
4 in s                 # O(1) - check membership
s.pop()                # O(1) - remove arbitrary element

# Set operations
s1 | s2                # Union
s1 & s2                # Intersection
s1 - s2                # Difference
s1 ^ s2                # Symmetric difference
s1.issubset(s2)        # Check if s1 ⊆ s2
```

### 5. Heap (Priority Queue)
```python
import heapq

heap = []
heapq.heappush(heap, 3)        # O(log n) - add element
min_val = heapq.heappop(heap)  # O(log n) - remove minimum
heap[0]                         # O(1) - peek at minimum

# Convert list to heap
nums = [3, 1, 4, 1, 5]
heapq.heapify(nums)            # O(n) - in-place heapify

# For max heap, negate values
heapq.heappush(heap, -val)     # Push negative
max_val = -heapq.heappop(heap) # Pop and negate

# Get k largest/smallest
heapq.nlargest(k, nums)         # O(n log k)
heapq.nsmallest(k, nums)        # O(n log k)
```

## Useful Collections Module

### Counter
```python
from collections import Counter

counter = Counter([1, 2, 2, 3, 3, 3])
counter = Counter("hello")           # Count characters

counter['a'] += 1                    # Increment count
counter.most_common(3)               # Get top 3 most common
counter.update([4, 4, 5])           # Add more elements
counter.subtract([1, 2])            # Subtract counts

# Convert to dict
dict(counter)
```

### defaultdict
```python
from collections import defaultdict

# Auto-initialize with default type
dd = defaultdict(list)
dd['key'].append(value)    # No need to check if key exists

dd = defaultdict(int)
dd['count'] += 1           # Starts at 0 automatically

dd = defaultdict(set)
dd['key'].add(value)
```

### OrderedDict
```python
from collections import OrderedDict

od = OrderedDict()
od['first'] = 1
od['second'] = 2
od.move_to_end('first')       # Move to end
od.move_to_end('second', False) # Move to beginning
od.popitem()                  # Remove last item
od.popitem(False)             # Remove first item
```

## Useful Built-in Functions

### String Operations
```python
s = "hello world"

s.split()              # Split by whitespace
s.split(',')           # Split by delimiter
','.join(['a','b'])    # Join with delimiter
s.strip()              # Remove whitespace
s.lower()              # Lowercase
s.upper()              # Uppercase
s.replace('a', 'b')    # Replace all occurrences
s.startswith('he')     # Check prefix
s.endswith('ld')       # Check suffix
s.isalnum()            # Check alphanumeric
s.isdigit()            # Check if all digits
s.find('ll')           # Find substring index (-1 if not found)
s.count('l')           # Count occurrences

# Character operations
ord('a')               # Get ASCII value (97)
chr(97)                # Get character from ASCII ('a')
```

### Sorting
```python
# Basic sorting
arr.sort()                          # In-place sort
sorted(arr)                         # Return new sorted list

# Custom sorting
arr.sort(key=lambda x: x[1])       # Sort by second element
arr.sort(key=lambda x: (-x[0], x[1])) # Multiple criteria
arr.sort(reverse=True)              # Descending order

# Sort dictionary by value
sorted(d.items(), key=lambda x: x[1])
```

### Math Operations
```python
import math

math.ceil(3.2)         # 4 - Round up
math.floor(3.8)        # 3 - Round down
math.sqrt(16)          # 4.0 - Square root
math.pow(2, 3)         # 8.0 - Power (use ** for integer)
math.log(8, 2)         # 3.0 - Log base 2
math.gcd(12, 8)        # 4 - Greatest common divisor
math.factorial(5)      # 120

abs(-5)                # 5 - Absolute value
min(1, 2, 3)          # 1
max(1, 2, 3)          # 3
sum([1, 2, 3])        # 6
round(3.7)            # 4 - Round to nearest

# Infinity
float('inf')           # Positive infinity
float('-inf')          # Negative infinity
```

### Iteration Tools
```python
# Range
range(5)               # 0, 1, 2, 3, 4
range(2, 5)           # 2, 3, 4
range(0, 10, 2)       # 0, 2, 4, 6, 8

# Enumerate
for i, val in enumerate(arr):
    print(i, val)

# Zip
for a, b in zip(arr1, arr2):
    print(a, b)

# Reversed
for val in reversed(arr):
    print(val)
```

## Advanced Itertools

```python
from itertools import combinations, permutations, product

# Combinations - order doesn't matter
list(combinations([1,2,3], 2))     # [(1,2), (1,3), (2,3)]

# Permutations - order matters
list(permutations([1,2,3], 2))     # [(1,2), (1,3), (2,1), (2,3), (3,1), (3,2)]

# Cartesian product
list(product([1,2], ['a','b']))    # [(1,'a'), (1,'b'), (2,'a'), (2,'b')]
```

## Binary Operations

```python
# Bitwise operations
a & b                  # AND
a | b                  # OR
a ^ b                  # XOR
~a                     # NOT
a << n                 # Left shift (multiply by 2^n)
a >> n                 # Right shift (divide by 2^n)

# Check bit
(num >> i) & 1         # Check if i-th bit is set

# Set bit
num |= (1 << i)        # Set i-th bit to 1

# Clear bit
num &= ~(1 << i)       # Set i-th bit to 0

# Toggle bit
num ^= (1 << i)        # Flip i-th bit

# Count set bits
bin(num).count('1')
```

## Type Conversions

```python
# String to int/float
int("123")             # 123
float("3.14")          # 3.14
int("101", 2)          # 5 (binary to decimal)
int("FF", 16)          # 255 (hex to decimal)

# Int to string
str(123)               # "123"
bin(5)                 # "0b101"
oct(8)                 # "0o10"
hex(255)               # "0xff"

# List/string conversions
list("hello")          # ['h', 'e', 'l', 'l', 'o']
''.join(['a','b'])     # "ab"

# Type checking
isinstance(x, int)
isinstance(x, (int, float))  # Multiple types
type(x) == list
```

## Common Patterns & Tricks

### List Comprehensions
```python
# Basic
[x*2 for x in range(5)]              # [0, 2, 4, 6, 8]

# With condition
[x for x in range(10) if x % 2 == 0] # [0, 2, 4, 6, 8]

# Nested
[[0]*3 for _ in range(3)]            # 3x3 matrix of zeros

# Dictionary comprehension
{k: v*2 for k, v in d.items()}

# Set comprehension
{x*2 for x in range(5)}
```

### Multiple Assignment
```python
a, b = b, a            # Swap
a, b, c = 1, 2, 3     # Multiple assignment
*first, last = [1, 2, 3, 4]  # first=[1,2,3], last=4
```

### Default Values
```python
# For missing keys
val = d.get('key', default_value)

# For None checks
x = a if a is not None else b
x = a or b             # If a is falsy, use b
```

### Division
```python
5 // 2                 # 2 - Integer division (floor)
5 / 2                  # 2.5 - Float division
5 % 2                  # 1 - Modulo
divmod(5, 2)          # (2, 1) - Both quotient and remainder
```

## Interview Tips

1. **Always clarify**: Can there be duplicates? Is the array sorted? What about edge cases?

2. **Common time complexities**:
   - List append: O(1) amortized
   - List insert at index 0: O(n)
   - Dict/Set operations: O(1) average, O(n) worst
   - Sorting: O(n log n)
   - Heap push/pop: O(log n)

3. **Space-efficient alternatives**:
   - Use `yield` for generators instead of building full lists
   - Use `set` for membership testing instead of lists
   - Use `deque` for queue operations instead of list

4. **Debugging tricks**:
   ```python
   print(f"var={var}")  # F-string debugging
   print(locals())       # Print all local variables
   ```

5. **Initialize 2D arrays correctly**:
   ```python
   # WRONG - creates references to same list
   matrix = [[0] * 3] * 3

   # CORRECT - creates independent lists
   matrix = [[0] * 3 for _ in range(3)]
   ```

Remember: In interviews, explain your choice of data structure based on the time complexity requirements!