# Floyd-Warshall Algorithm

## Overview
Floyd-Warshall is an **all-pairs shortest path** algorithm that finds shortest distances between every pair of vertices in a weighted graph. It's particularly useful when you need to answer many queries about paths between different vertex pairs.

## Core Concept
The algorithm uses dynamic programming with the key idea:
> "Can I improve the path from vertex i to vertex j by going through vertex k as an intermediate point?"

## Algorithm Implementation

### Standard Shortest Path Version
```python
def floydWarshall(graph):
    V = len(graph)
    # dist[i][j] = shortest distance from i to j
    dist = [[float('inf')] * V for _ in range(V)]

    # Initialize with direct edges
    for i in range(V):
        for j in range(V):
            if i == j:
                dist[i][j] = 0
            elif graph[i][j] != 0:
                dist[i][j] = graph[i][j]

    # Core algorithm: try each vertex as intermediate
    for k in range(V):  # Intermediate vertex
        for i in range(V):  # Source
            for j in range(V):  # Destination
                # Can we improve path from i to j by going through k?
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    return dist
```

### Transitive Closure Version (Reachability)
```python
def floydWarshallReachability(V, edges):
    # reach[i][j] = True if there's a path from i to j
    reach = [[False] * V for _ in range(V)]

    # Initialize with direct edges
    for src, dst in edges:
        reach[src][dst] = True

    # Every vertex can reach itself
    for i in range(V):
        reach[i][i] = True

    # Floyd-Warshall for transitive closure
    for k in range(V):
        for i in range(V):
            for j in range(V):
                # Can reach j from i either directly or through k
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])

    return reach
```

## Time and Space Complexity

- **Time Complexity:** O(V³) - Three nested loops over all vertices
- **Space Complexity:** O(V²) - Distance/reachability matrix
- **Query Time:** O(1) - After preprocessing, each query is a simple lookup

## When to Use Floyd-Warshall

### ✅ Use When:
1. **Many queries on small graphs** (V ≤ 500)
2. **Need all-pairs distances/reachability**
3. **Dense graphs** (E ≈ V²)
4. **Negative edge weights** (but no negative cycles)
5. **Queries significantly outnumber vertices** (Q >> V²)

### ❌ Don't Use When:
1. **Large graphs** (V > 1000)
2. **Single source queries** (use Dijkstra or BFS)
3. **Sparse graphs with few queries**
4. **Early termination needed**
5. **Memory constraints** (requires O(V²) space)

## Course Schedule III - Why Floyd-Warshall?

### Problem Constraints:
- **V (numCourses) ≤ 100** - Small graph
- **Q (queries) ≤ 10,000** - Many queries

### Complexity Analysis:

#### DFS Approach:
```
For each query: O(V + E) DFS
Total: O(Q × (V + E))
     = O(10,000 × 200)  [assuming E ≈ V]
     = O(2,000,000) operations
```

#### Floyd-Warshall Approach:
```
Preprocessing: O(V³) = O(100³) = O(1,000,000)
All queries: O(Q × 1) = O(10,000 × 1) = O(10,000)
Total: O(1,010,000) operations
```

**Floyd-Warshall is ~2x faster for this specific problem!**

### Implementation for Course Schedule III:
```python
def checkIfPrerequisiteOptimized(numCourses, prerequisites, queries):
    # Build reachability matrix using Floyd-Warshall
    reach = [[False] * numCourses for _ in range(numCourses)]

    # Initialize with direct prerequisites
    for course, prereq in prerequisites:
        reach[prereq][course] = True  # prereq is prerequisite of course

    # Floyd-Warshall to find all transitive prerequisites
    for k in range(numCourses):
        for i in range(numCourses):
            for j in range(numCourses):
                # i is prereq of j if:
                # - i is already prereq of j, OR
                # - i is prereq of k AND k is prereq of j
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])

    # Answer all queries in O(1) each
    return [reach[uj][vj] for uj, vj in queries]
```

## Comparison with Other Algorithms

| Algorithm | Type | Negative Weights | Time Complexity | Best For |
|-----------|------|-----------------|-----------------|----------|
| **BFS** | Single Source | No | O(V + E) | Unweighted graphs |
| **DFS** | Path Finding | Yes | O(V + E) | Single path queries |
| **Dijkstra** | Single Source | No | O((V + E) log V) | Non-negative weights |
| **Bellman-Ford** | Single Source | Yes | O(VE) | Negative weights |
| **Floyd-Warshall** | All Pairs | Yes | O(V³) | Small dense graphs, many queries |

## Quick Decision Framework

```python
def chooseAlgorithm(V, E, numQueries):
    if V > 500:
        return "Never use Floyd-Warshall - too many vertices"
    elif numQueries > V * V:
        return "Consider Floyd-Warshall - many queries justify preprocessing"
    elif numQueries < 10:
        return "Use DFS/BFS - few queries don't justify O(V³) preprocessing"
    else:
        # Calculate actual complexities
        dfs_cost = numQueries * (V + E)
        floyd_cost = V * V * V + numQueries
        return "Floyd-Warshall" if floyd_cost < dfs_cost else "DFS"
```

## Key Interview Insights

1. **Recognize the pattern:** Small V with large Q often hints at preprocessing
2. **Mention trade-offs:** Shows you understand when to use which algorithm
3. **Consider space:** O(V²) space might be prohibitive for large graphs
4. **Alternative solutions:** Mention that you could also:
   - Use DFS from each vertex: O(V × (V + E))
   - Cache DFS results as you go
   - Use Tarjan's algorithm for strongly connected components

## Practice Problems

1. **All Pairs Shortest Path** - Classic Floyd-Warshall
2. **Course Schedule III** - Transitive closure variant
3. **City Connectivity** - Reachability queries
4. **Cheapest Flights Within K Stops** - Modified for path constraints
5. **Network Delay Time** - Can compare with Dijkstra

## Remember

Floyd-Warshall shines when:
- **V³ < Q × (V + E)** - Preprocessing pays off
- **V ≤ 500** - Cubic time is manageable
- **Need complete information** - All distances/reachability at once

It's not a silver bullet, but for the right constraints (like Course Schedule III), it's the optimal choice!