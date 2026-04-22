# Complete Guide to Trie Data Structure

## What is a Trie?

A **Trie** (pronounced "try" or "tree") is a tree-like data structure used to store a dynamic set of strings, where keys are usually strings. It's also known as a **prefix tree** or **digital tree**. Each node in the trie represents a single character, and paths from the root to leaf nodes represent complete words or strings.

## Key Characteristics

- **Root Node**: Contains no character (empty)
- **Each Node**: Represents a character and may have up to 26 children (for lowercase English letters)
- **Path from Root**: Represents a prefix or complete word
- **End Marker**: Nodes are marked to indicate the end of a valid word

## Structure Visualization

```
Example Trie containing words: "cat", "car", "card", "care", "careful"

        root
         |
         c
         |
         a
         |
         t*    r
               |
               d*   e*
                    |
                    f
                    |
                    u
                    |
                    l*

* indicates end of word
```

## Time and Space Complexity

### Time Complexity
- **Insert**: O(m) where m is the length of the string
- **Search**: O(m) where m is the length of the string
- **Delete**: O(m) where m is the length of the string
- **Prefix Search**: O(p) where p is the length of the prefix

### Space Complexity
- **Worst Case**: O(ALPHABET_SIZE × N × M) where N is number of keys and M is average length
- **Best Case**: O(N × M) when strings share common prefixes

## Use Cases

### 1. **Autocomplete/Auto-suggestion Systems**
- Search engines, IDEs, mobile keyboards
- Quickly find all words with a given prefix

### 2. **Spell Checkers**
- Dictionary lookup and word validation
- Suggest corrections for misspelled words

### 3. **IP Routing Tables**
- Longest prefix matching in network routers
- Efficient routing decisions

### 4. **Word Games**
- Boggle, Scrabble, crossword puzzles
- Validate words and find possible words

### 5. **String Matching Algorithms**
- Pattern matching in text processing
- Multiple pattern search (Aho-Corasick algorithm)

### 6. **Contact Lists**
- Phone contact search and filtering
- T9 predictive text input

## Technical Interview Indicators

When you see these keywords or patterns in interview problems, consider using a Trie:

### 🔍 **Strong Indicators**
- **"Prefix"** - Any mention of prefix operations
- **"Autocomplete"** or **"Auto-suggestion"**
- **"Dictionary"** or **"Word list"**
- **"All words starting with..."**
- **"Longest common prefix"**
- **"Word search"** in a grid/board
- **"Multiple string matching"**

### 🎯 **Problem Patterns**
- Finding all words with a common prefix
- Checking if a string is a prefix of any word
- Building a dictionary for fast lookups
- Implementing search with wildcards (using '.' or '*')
- Word break problems with large dictionaries
- Boggle-style word finding games

### 📝 **Common Problem Phrases**
- "Given a list of words..."
- "Find all words that start with..."
- "Implement a data structure that supports..."
- "Design an autocomplete system..."
- "Word search in a 2D grid..."

## Pseudocode Implementation

### Basic Trie Node Structure
```
CLASS TrieNode:
    children = HashMap<Character, TrieNode>  // or Array[26] for lowercase
    isEndOfWord = boolean
    
    CONSTRUCTOR():
        children = empty HashMap
        isEndOfWord = false
```

### Core Operations

#### Insert Operation
```
FUNCTION insert(root, word):
    current = root
    
    FOR each character in word:
        IF character NOT in current.children:
            current.children[character] = new TrieNode()
        current = current.children[character]
    
    current.isEndOfWord = true
```

#### Search Operation
```
FUNCTION search(root, word):
    current = root
    
    FOR each character in word:
        IF character NOT in current.children:
            return false
        current = current.children[character]
    
    return current.isEndOfWord
```

#### Starts With (Prefix Search)
```
FUNCTION startsWith(root, prefix):
    current = root
    
    FOR each character in prefix:
        IF character NOT in current.children:
            return false
        current = current.children[character]
    
    return true
```

#### Delete Operation
```
FUNCTION delete(root, word):
    FUNCTION deleteHelper(node, word, index):
        IF index == length(word):
            IF NOT node.isEndOfWord:
                return false  // Word doesn't exist
            node.isEndOfWord = false
            return size(node.children) == 0  // Delete node if no children
        
        character = word[index]
        childNode = node.children[character]
        
        IF childNode == null:
            return false  // Word doesn't exist
        
        shouldDeleteChild = deleteHelper(childNode, word, index + 1)
        
        IF shouldDeleteChild:
            remove childNode from node.children
            return NOT node.isEndOfWord AND size(node.children) == 0
        
        return false
    
    deleteHelper(root, word, 0)
```

## Python Implementation

```python
class TrieNode:
    def __init__(self):
        self.children = {}  # Dictionary to store children
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        """Initialize the Trie with an empty root node."""
        self.root = TrieNode()
    
    def insert(self, word: str) -> None:
        """
        Insert a word into the trie.
        Time Complexity: O(m) where m is the length of the word
        Space Complexity: O(m) in worst case
        """
        current = self.root
        
        for char in word:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        
        current.is_end_of_word = True
    
    def search(self, word: str) -> bool:
        """
        Search for a word in the trie.
        Time Complexity: O(m) where m is the length of the word
        """
        current = self.root
        
        for char in word:
            if char not in current.children:
                return False
            current = current.children[char]
        
        return current.is_end_of_word
    
    def starts_with(self, prefix: str) -> bool:
        """
        Check if any word in the trie starts with the given prefix.
        Time Complexity: O(p) where p is the length of the prefix
        """
        current = self.root
        
        for char in prefix:
            if char not in current.children:
                return False
            current = current.children[char]
        
        return True
    
    def get_words_with_prefix(self, prefix: str) -> list:
        """
        Get all words in the trie that start with the given prefix.
        Useful for autocomplete functionality.
        """
        def dfs(node, current_word, results):
            if node.is_end_of_word:
                results.append(current_word)
            
            for char, child_node in node.children.items():
                dfs(child_node, current_word + char, results)
        
        # Find the node representing the prefix
        current = self.root
        for char in prefix:
            if char not in current.children:
                return []
            current = current.children[char]
        
        # Collect all words starting from this node
        results = []
        dfs(current, prefix, results)
        return results
    
    def delete(self, word: str) -> None:
        """
        Delete a word from the trie.
        Time Complexity: O(m) where m is the length of the word
        """
        def delete_helper(node, word, index):
            if index == len(word):
                if not node.is_end_of_word:
                    return False  # Word doesn't exist
                node.is_end_of_word = False
                return len(node.children) == 0  # Delete if no children
            
            char = word[index]
            child_node = node.children.get(char)
            
            if not child_node:
                return False  # Word doesn't exist
            
            should_delete_child = delete_helper(child_node, word, index + 1)
            
            if should_delete_child:
                del node.children[char]
                return not node.is_end_of_word and len(node.children) == 0
            
            return False
        
        delete_helper(self.root, word, 0)
    
    def is_empty(self) -> bool:
        """Check if the trie is empty."""
        return len(self.root.children) == 0
    
    def get_all_words(self) -> list:
        """Get all words stored in the trie."""
        return self.get_words_with_prefix("")

# Example usage and test cases
if __name__ == "__main__":
    # Create a new trie
    trie = Trie()
    
    # Insert words
    words = ["cat", "car", "card", "care", "careful", "cats", "dog", "dogs"]
    for word in words:
        trie.insert(word)
    
    # Test search
    print("Search 'car':", trie.search("car"))        # True
    print("Search 'care':", trie.search("care"))      # True
    print("Search 'careful':", trie.search("careful")) # True
    print("Search 'careless':", trie.search("careless")) # False
    
    # Test prefix search
    print("Starts with 'car':", trie.starts_with("car"))   # True
    print("Starts with 'dog':", trie.starts_with("dog"))   # True
    print("Starts with 'elephant':", trie.starts_with("elephant")) # False
    
    # Test autocomplete
    print("Words with prefix 'car':", trie.get_words_with_prefix("car"))
    # Output: ['car', 'card', 'care', 'careful']
    
    print("Words with prefix 'dog':", trie.get_words_with_prefix("dog"))
    # Output: ['dog', 'dogs']
    
    # Test delete
    trie.delete("care")
    print("After deleting 'care':")
    print("Search 'care':", trie.search("care"))      # False
    print("Search 'careful':", trie.search("careful")) # True (still exists)
    
    # Get all words
    print("All words:", trie.get_all_words())
```

## Advanced Variations

### 1. **Compressed Trie (Patricia Tree)**
- Reduces space by merging nodes with single children
- More space-efficient for sparse datasets

### 2. **Suffix Trie**
- Contains all suffixes of a given string
- Useful for pattern matching and string algorithms

### 3. **Ternary Search Trie**
- Each node has at most 3 children (less than, equal, greater than)
- More space-efficient than standard trie for large alphabets

## When NOT to Use Trie

- **Small datasets**: Hash tables might be more efficient
- **Memory constraints**: Tries can use significant memory
- **Single string operations**: Simple string methods may suffice
- **Numeric data**: Other data structures like B-trees might be better

## Practice Problems

1. **LeetCode 208**: Implement Trie (Prefix Tree)
2. **LeetCode 211**: Design Add and Search Words Data Structure
3. **LeetCode 212**: Word Search II
4. **LeetCode 421**: Maximum XOR of Two Numbers in an Array
5. **LeetCode 648**: Replace Words
6. **LeetCode 677**: Map Sum Pairs

## Summary

Tries are powerful data structures for string-related operations, especially when dealing with prefixes and dictionaries. They shine in scenarios requiring fast prefix searches, autocomplete functionality, and word validation. The key is recognizing when the problem involves prefix operations or multiple string searches, making the Trie an optimal choice despite its memory overhead.