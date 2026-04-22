# Complete Sorting Algorithms Reference

## 🎯 Quick Reference Table

| Algorithm | Time (Best) | Time (Average) | Time (Worst) | Space | Stable | In-Place |
|-----------|-------------|----------------|--------------|-------|--------|----------|
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) | ✅ | ✅ |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) | ❌ | ✅ |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | ✅ | ✅ |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ | ❌ |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | ❌ | ✅ |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | ❌ | ✅ |
| Counting Sort | O(n+k) | O(n+k) | O(n+k) | O(k) | ✅ | ❌ |
| Radix Sort | O(d(n+k)) | O(d(n+k)) | O(d(n+k)) | O(n+k) | ✅ | ❌ |
| Bucket Sort | O(n+k) | O(n+k) | O(n²) | O(n) | ✅ | ❌ |

---

## 1. 🫧 Bubble Sort
**Time:** O(n) best, O(n²) average/worst  
**Space:** O(1)  
**Stable:** Yes | **In-Place:** Yes

### Pseudocode:
```
procedure bubbleSort(array):
    n = length(array)
    for i = 0 to n-1:
        swapped = false
        for j = 0 to n-2-i:
            if array[j] > array[j+1]:
                swap(array[j], array[j+1])
                swapped = true
        if not swapped:
            break
```

### Python Implementation:
```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        # Last i elements are already sorted
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # If no swapping occurred, array is sorted
        if not swapped:
            break
    return arr
```

**When to Use:** Educational purposes, nearly sorted data, very small datasets

---

## 2. 🎯 Selection Sort
**Time:** O(n²) all cases  
**Space:** O(1)  
**Stable:** No | **In-Place:** Yes

### Pseudocode:
```
procedure selectionSort(array):
    n = length(array)
    for i = 0 to n-1:
        minIndex = i
        for j = i+1 to n-1:
            if array[j] < array[minIndex]:
                minIndex = j
        swap(array[i], array[minIndex])
```

### Python Implementation:
```python
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        # Find minimum element in remaining array
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        
        # Swap found minimum with first element
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```

**When to Use:** Memory is limited, small datasets, when number of swaps should be minimized

---

## 3. 📝 Insertion Sort
**Time:** O(n) best, O(n²) average/worst  
**Space:** O(1)  
**Stable:** Yes | **In-Place:** Yes

### Pseudocode:
```
procedure insertionSort(array):
    for i = 1 to length(array)-1:
        key = array[i]
        j = i - 1
        while j >= 0 and array[j] > key:
            array[j+1] = array[j]
            j = j - 1
        array[j+1] = key
```

### Python Implementation:
```python
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        
        # Move elements greater than key one position ahead
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        
        # Place key in correct position
        arr[j + 1] = key
    return arr
```

**When to Use:** Small datasets, nearly sorted data, online algorithm (sorts as data arrives)

---

## 4. 🌳 Merge Sort
**Time:** O(n log n) all cases  
**Space:** O(n)  
**Stable:** Yes | **In-Place:** No

### Pseudocode:
```
procedure mergeSort(array):
    if length(array) <= 1:
        return array
    
    mid = length(array) / 2
    left = mergeSort(array[0...mid-1])
    right = mergeSort(array[mid...end])
    
    return merge(left, right)

procedure merge(left, right):
    result = []
    while left and right are not empty:
        if left[0] <= right[0]:
            append left[0] to result
            remove left[0]
        else:
            append right[0] to result
            remove right[0]
    append remaining elements to result
    return result
```

### Python Implementation:
```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    # Divide
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # Conquer
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    
    # Merge in sorted order
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

**When to Use:** Guaranteed O(n log n), stable sorting needed, external sorting, large datasets

---

## 5. ⚡ Quick Sort
**Time:** O(n log n) best/average, O(n²) worst  
**Space:** O(log n) average, O(n) worst  
**Stable:** No | **In-Place:** Yes

### Pseudocode:
```
procedure quickSort(array, low, high):
    if low < high:
        pivotIndex = partition(array, low, high)
        quickSort(array, low, pivotIndex - 1)
        quickSort(array, pivotIndex + 1, high)

procedure partition(array, low, high):
    pivot = array[high]
    i = low - 1
    for j = low to high - 1:
        if array[j] <= pivot:
            i = i + 1
            swap(array[i], array[j])
    swap(array[i + 1], array[high])
    return i + 1
```

### Python Implementation:
```python
def quick_sort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        # Partition and get pivot index
        pivot_idx = partition(arr, low, high)
        
        # Recursively sort left and right subarrays
        quick_sort(arr, low, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, high)
    return arr

def partition(arr, low, high):
    # Choose rightmost element as pivot
    pivot = arr[high]
    i = low - 1  # Index of smaller element
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    # Place pivot in correct position
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```

**When to Use:** General purpose, average case performance, when memory is limited

---

## 6. 🏔️ Heap Sort
**Time:** O(n log n) all cases  
**Space:** O(1)  
**Stable:** No | **In-Place:** Yes

### Pseudocode:
```
procedure heapSort(array):
    buildMaxHeap(array)
    for i = length(array) - 1 down to 1:
        swap(array[0], array[i])
        heapify(array, 0, i)

procedure buildMaxHeap(array):
    for i = length(array)/2 - 1 down to 0:
        heapify(array, i, length(array))

procedure heapify(array, root, size):
    largest = root
    left = 2 * root + 1
    right = 2 * root + 2
    
    if left < size and array[left] > array[largest]:
        largest = left
    if right < size and array[right] > array[largest]:
        largest = right
    
    if largest != root:
        swap(array[root], array[largest])
        heapify(array, largest, size)
```

### Python Implementation:
```python
def heap_sort(arr):
    n = len(arr)
    
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    
    # Extract elements from heap one by one
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  # Swap
        heapify(arr, i, 0)  # Heapify reduced heap
    
    return arr

def heapify(arr, heap_size, root_idx):
    largest = root_idx
    left = 2 * root_idx + 1
    right = 2 * root_idx + 2
    
    # Check if left child exists and is greater than root
    if left < heap_size and arr[left] > arr[largest]:
        largest = left
    
    # Check if right child exists and is greater than current largest
    if right < heap_size and arr[right] > arr[largest]:
        largest = right
    
    # If largest is not root, swap and continue heapifying
    if largest != root_idx:
        arr[root_idx], arr[largest] = arr[largest], arr[root_idx]
        heapify(arr, heap_size, largest)
```

**When to Use:** Guaranteed O(n log n) with O(1) space, real-time systems

---

## 7. 🔢 Counting Sort
**Time:** O(n + k) where k = range of input  
**Space:** O(k)  
**Stable:** Yes | **In-Place:** No

### Pseudocode:
```
procedure countingSort(array, maxVal):
    count = array of size (maxVal + 1) filled with 0
    output = array of size length(array)
    
    // Count occurrences
    for i = 0 to length(array) - 1:
        count[array[i]] = count[array[i]] + 1
    
    // Cumulative count
    for i = 1 to maxVal:
        count[i] = count[i] + count[i-1]
    
    // Build output array
    for i = length(array) - 1 down to 0:
        output[count[array[i]] - 1] = array[i]
        count[array[i]] = count[array[i]] - 1
    
    return output
```

### Python Implementation:
```python
def counting_sort(arr):
    if not arr:
        return arr
    
    # Find range
    max_val = max(arr)
    min_val = min(arr)
    range_size = max_val - min_val + 1
    
    # Count occurrences
    count = [0] * range_size
    for num in arr:
        count[num - min_val] += 1
    
    # Calculate cumulative count
    for i in range(1, range_size):
        count[i] += count[i - 1]
    
    # Build output array (stable version)
    output = [0] * len(arr)
    for i in range(len(arr) - 1, -1, -1):
        output[count[arr[i] - min_val] - 1] = arr[i]
        count[arr[i] - min_val] -= 1
    
    return output
```

**When to Use:** Small range of integers, when k = O(n), need stable sort

---

## 8. 📊 Radix Sort
**Time:** O(d(n + k)) where d = digits, k = radix  
**Space:** O(n + k)  
**Stable:** Yes | **In-Place:** No

### Pseudocode:
```
procedure radixSort(array):
    maxVal = maximum value in array
    exp = 1
    while maxVal / exp > 0:
        countingSortByDigit(array, exp)
        exp = exp * 10

procedure countingSortByDigit(array, exp):
    // Count sort based on digit at exp position
    count = array of size 10 filled with 0
    output = array of size length(array)
    
    for i = 0 to length(array) - 1:
        digit = (array[i] / exp) % 10
        count[digit] = count[digit] + 1
    
    for i = 1 to 9:
        count[i] = count[i] + count[i-1]
    
    for i = length(array) - 1 down to 0:
        digit = (array[i] / exp) % 10
        output[count[digit] - 1] = array[i]
        count[digit] = count[digit] - 1
    
    copy output to array
```

### Python Implementation:
```python
def radix_sort(arr):
    if not arr:
        return arr
    
    # Find maximum number to determine number of digits
    max_num = max(arr)
    
    # Do counting sort for every digit
    exp = 1
    while max_num // exp > 0:
        counting_sort_by_digit(arr, exp)
        exp *= 10
    
    return arr

def counting_sort_by_digit(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10
    
    # Count occurrences of each digit
    for num in arr:
        digit = (num // exp) % 10
        count[digit] += 1
    
    # Calculate cumulative count
    for i in range(1, 10):
        count[i] += count[i - 1]
    
    # Build output array
    for i in range(n - 1, -1, -1):
        digit = (arr[i] // exp) % 10
        output[count[digit] - 1] = arr[i]
        count[digit] -= 1
    
    # Copy output to original array
    for i in range(n):
        arr[i] = output[i]
```

**When to Use:** Fixed-width integers, strings of same length, when d is small

---

## 9. 🪣 Bucket Sort
**Time:** O(n + k) best/average, O(n²) worst  
**Space:** O(n)  
**Stable:** Yes | **In-Place:** No

### Pseudocode:
```
procedure bucketSort(array, numBuckets):
    buckets = array of numBuckets empty lists
    
    // Distribute elements into buckets
    for each element in array:
        bucketIndex = floor(element * numBuckets)
        add element to buckets[bucketIndex]
    
    // Sort individual buckets
    for each bucket in buckets:
        insertionSort(bucket)
    
    // Concatenate buckets
    result = []
    for each bucket in buckets:
        append bucket to result
    return result
```

### Python Implementation:
```python
def bucket_sort(arr, num_buckets=10):
    if not arr:
        return arr
    
    # Find range
    min_val, max_val = min(arr), max(arr)
    range_size = max_val - min_val
    
    # Create buckets
    buckets = [[] for _ in range(num_buckets)]
    
    # Distribute elements into buckets
    for num in arr:
        if range_size == 0:
            bucket_idx = 0
        else:
            bucket_idx = int((num - min_val) * (num_buckets - 1) / range_size)
        buckets[bucket_idx].append(num)
    
    # Sort individual buckets and concatenate
    result = []
    for bucket in buckets:
        if bucket:
            bucket.sort()  # or use insertion_sort(bucket)
            result.extend(bucket)
    
    return result
```

**When to Use:** Uniformly distributed data, floating point numbers, when data fits uniform distribution

---

## 🎯 Algorithm Selection Guide

### Choose Based on Data Characteristics:

**Small datasets (n < 50):**
- Insertion Sort (simple, efficient for small n)

**Nearly sorted data:**
- Insertion Sort or Bubble Sort (O(n) best case)

**Guaranteed O(n log n) needed:**
- Merge Sort (stable) or Heap Sort (in-place)

**Average case performance, memory limited:**
- Quick Sort (fastest average case, in-place)

**Integer data with small range:**
- Counting Sort or Radix Sort

**Uniform distribution:**
- Bucket Sort

**External sorting (data doesn't fit in memory):**
- Merge Sort

### Stability Requirements:
- **Need stable:** Merge Sort, Insertion Sort, Bubble Sort, Counting Sort, Radix Sort, Bucket Sort
- **Don't need stable:** Quick Sort, Heap Sort, Selection Sort

### Space Constraints:
- **O(1) space:** Quick Sort, Heap Sort, Insertion Sort, Selection Sort, Bubble Sort
- **O(n) space okay:** Merge Sort, Counting Sort, Radix Sort, Bucket Sort

## 💡 Interview Tips

1. **Always ask about constraints:** Data size, memory limits, stability requirements
2. **Know the trade-offs:** Time vs space, best vs worst case
3. **Implement simply first:** Get working solution, then optimize
4. **Consider hybrid approaches:** Python's Timsort combines merge and insertion sort
5. **Practice implementation:** Focus on merge sort and quick sort for interviews