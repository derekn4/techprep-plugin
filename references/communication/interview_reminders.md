# Interview Reminders - Key Communication Patterns

## 🎯 Core Communication Patterns to Maintain

### 1. **Decisive Language** ✅
- ✅ "I will use X because..."
- ✅ "I'll implement this approach since..."
- ❌ "Should I use...?"
- ❌ "I think maybe..."

### 2. **Present Multiple Approaches First**
Always present 2-3 approaches, then choose one:
- "I see three approaches: sorting O(n log n), heap O(n log k), and quickselect O(n) average..."
- "I'll go with quickselect because we need O(n) average time"

### 3. **State Trade-offs Without Being Asked**
- Time vs Space complexity
- Code simplicity vs Performance
- Average case vs Worst case

## 📝 Problem-Solving Checklist

### Before Coding:
- [ ] Clarify constraints (even though they're given)
- [ ] Ask about edge cases
- [ ] Present multiple approaches
- [ ] Choose approach with clear reasoning
- [ ] State complexity before coding

### While Coding:
- [ ] Explain as you code (brief comments)
- [ ] Use clear variable names
- [ ] Don't worry about minor typos (most interviews use a shared doc, not an IDE)

### After Coding:
- [ ] Trace through with an example
- [ ] Identify edge cases to test
- [ ] State final complexity
- [ ] Ask "Would you like me to optimize further?"

## 💡 Technical Patterns to Remember

### Complexity Tricks:
- **HashSet/HashMap:** O(1) average lookup/insert
- **MinHeap of size k:** O(n log k) not O(n log n)
- **QuickSelect:** O(n) average, O(n²) worst
- **Bucket Sort:** O(n) when range is bounded
- **Two-pointer:** Often reduces O(n²) to O(n)

### Common Optimizations:
- **Finding kth element:** QuickSelect > Sorting
- **Top K elements:** MinHeap > Sorting
- **Consecutive sequences:** HashSet > Sorting
- **Anagram grouping:** Character count > Sorting

## 🚫 What NOT to Do

1. **Don't apologize for thinking**
   - ❌ "Sorry, let me think..."
   - ✅ "Let me analyze this problem..."

2. **Don't second-guess after choosing**
   - Once you pick an approach, commit to it
   - Only change if you discover a fundamental issue

3. **Don't obsess over typos**
   - Most interviews use a shared doc, not an IDE
   - Interviewers expect typos
   - Catch them during trace-through if possible

## 🎤 Interview Flow

### Opening (First 2 minutes):
- Restate problem in your words
- Clarify constraints
- Ask about edge cases

### Planning (3-5 minutes):
- Present approaches
- Analyze trade-offs
- Choose with confidence

### Coding (15-20 minutes):
- Implement cleanly
- Explain key decisions
- Focus on correctness first

### Testing (5 minutes):
- Trace through example
- Test edge cases
- State complexity

### Discussion (Remaining time):
- Optimization ideas
- Follow-up questions
- Alternative approaches

## 🔥 Your Strengths (Keep Doing These!)
- Excellent complexity analysis
- Strong algorithm knowledge
- Clear trade-off articulation
- Quick pattern recognition
- Decisive approach selection

## 📈 Progress Indicators
- Day 1: "I can think of..." → Day 4: "I will implement..." ✅
- Presenting multiple approaches consistently ✅
- Stating assumptions proactively ✅
- Testing edge cases without prompting (improving)

## 🎯 Final Week Focus
- Maintain confident communication
- Practice mock interviews
- Review this list before each session
- Trust your preparation - you're doing great!

## 🚀 Interview Day Mantras
1. "I know multiple ways to solve this"
2. "Let me present the trade-offs"
3. "I'll implement X because Y"
4. "Let me trace through an example"
5. "The complexity is..."

---

**Remember:** You're tracking at 9+/10 performance. You've got this! 💪