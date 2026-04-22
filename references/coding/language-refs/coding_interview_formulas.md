# Essential Math Formulas for Coding Interviews

## 🔢 **ARITHMETIC SEQUENCES & SERIES**

### Sum of First N Natural Numbers
```
1 + 2 + 3 + ... + n = n(n+1)/2
```
**Use cases**: Missing number, array sum problems, counting problems

### Sum of First N Even Numbers  
```
2 + 4 + 6 + ... + 2n = n(n+1)
```

### Sum of First N Odd Numbers
```
1 + 3 + 5 + ... + (2n-1) = n²
```

### Arithmetic Sequence Sum
```
Sum = n/2 * (first_term + last_term)
Sum = n/2 * (2a + (n-1)d)  where a=first term, d=common difference
```

---

## 📐 **GEOMETRIC SEQUENCES**

### Geometric Series Sum
```
a + ar + ar² + ... + ar^(n-1) = a(r^n - 1)/(r - 1)
```
**Use cases**: Binary tree problems, exponential growth

### Sum of Powers of 2
```
1 + 2 + 4 + 8 + ... + 2^(n-1) = 2^n - 1
```
**Use cases**: Binary representation, tree heights

---

## 🎯 **COMBINATORICS** 

### Combinations (Choose)
```
C(n,r) = n!/(r!(n-r)!) = nCr
```
**Use cases**: Subset problems, path counting

### Permutations  
```
P(n,r) = n!/(n-r)!
```

### Factorial Approximation (Stirling's)
```
n! ≈ √(2πn) * (n/e)^n
```

---

## 📊 **PROBABILITY & STATISTICS**

### Expected Value
```
E[X] = Σ(x * P(x))
```

### Variance
```
Var(X) = E[X²] - (E[X])²
```

---

## 🔺 **GEOMETRY**

### Triangle Area (Heron's Formula)
```
Area = √(s(s-a)(s-b)(s-c))  where s = (a+b+c)/2
```

### Distance Between Points
```
d = √((x₂-x₁)² + (y₂-y₁)²)
```

### Circle Area & Circumference
```
Area = πr²
Circumference = 2πr
```

---

## 🌳 **TREE & GRAPH FORMULAS**

### Complete Binary Tree Nodes
```
Height h → Max nodes = 2^(h+1) - 1
Nodes n → Height = ⌊log₂(n)⌋
```

### Tree Relationships
```
In binary tree with n nodes: edges = n - 1
Full binary tree: internal_nodes = leaves - 1
```

---

## 💾 **BIT MANIPULATION**

### Powers of 2 Check
```
n is power of 2 ⟺ (n & (n-1)) == 0 and n > 0
```

### Count Set Bits (Brian Kernighan)
```
while(n) { count++; n = n & (n-1); }
```

### XOR Properties
```
a ⊕ a = 0
a ⊕ 0 = a  
a ⊕ b ⊕ a = b
```

---

## ⏰ **TIME COMPLEXITY SHORTCUTS**

### Master Theorem (Divide & Conquer)
```
T(n) = aT(n/b) + f(n)

If f(n) = O(n^c):
- c < log_b(a) → T(n) = O(n^(log_b(a)))
- c = log_b(a) → T(n) = O(n^c * log n)  
- c > log_b(a) → T(n) = O(f(n))
```

### Common Complexities
```
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2^n) < O(n!)
```

---

## 🎲 **MODULAR ARITHMETIC**

### Modular Properties
```
(a + b) mod m = ((a mod m) + (b mod m)) mod m
(a * b) mod m = ((a mod m) * (b mod m)) mod m
```

### Fast Exponentiation
```
a^n mod m using binary exponentiation: O(log n)
```

---

## 📈 **ALGORITHM-SPECIFIC FORMULAS**

### Binary Search Range
```
left + (right - left) // 2  (avoids overflow)
```

### Sliding Window Maximum Size
```
For array of size n, window of size k: n - k + 1 windows
```

### Two Pointers Meeting Point
```
In array of size n: meet after at most n steps
```

---

## 🧮 **QUICK REFERENCE VALUES**

### Common Powers
```
2^10 = 1,024 ≈ 10³
2^20 = 1,048,576 ≈ 10⁶  
2^30 ≈ 10⁹
```

### Fibonacci Growth
```
F(n) ≈ φⁿ/√5  where φ = (1+√5)/2 ≈ 1.618 (golden ratio)
```

### Prime Approximation
```
Number of primes ≤ n ≈ n/ln(n)
```

---

## 💡 **INTERVIEW STRATEGY**

### **Memorize These First** (Most Common):
1. **Sum formula**: `n(n+1)/2`
2. **Powers of 2**: `2^n - 1`
3. **Combinations**: `nCr = n!/(r!(n-r)!)`
4. **Distance formula**: `√((x₂-x₁)² + (y₂-y₁)²)`
5. **Binary tree height**: `⌊log₂(n)⌋`

### **Practice Applications**:
- Missing number → Sum formula
- Subsets → Powers of 2  
- Path counting → Combinations
- Tree problems → Tree formulas
- Geometric problems → Distance/area formulas

### **Pro Tips**:
- **Derive on the spot** if you forget (show your thought process)
- **Double-check with small examples**
- **Know when NOT to use** (avoid overflow, consider edge cases)
- **Explain the intuition** behind the formula choice

Remember: Understanding WHY a formula works is more valuable than just memorizing it!