# /analyze — Analyse collective du code

Lance une analyse **multi-agent complète** du code avec:
- Code quality (erreurs, imports, types)
- Security (OWASP Top 10)
- Design patterns (bonnes pratiques)
- Refactoring suggestions (optimisations)
- Research (best practices pour langage)

## Usage

```
/analyze python "code here"
/analyze js <<< "$(cat file.js)"
/analyze typescript
```

## Modes

### 1. Full Analysis (default)
Tous les agents répondent, decision finale via vote pondéré.

```
/analyze python
```

**Output:**
```
Final Decision: APPROVE / BLOCK / REVIEW
Confidence: 85%
Reasoning: Found 2 issues...

All Agent Responses:
- code_analyzer: ✅ PASS (95%)
- security: 🔴 CRITICAL (98%)
- pattern: ✅ RECOGNIZED (80%)
...
```

### 2. Security Only
```
/analyze python --security-only
```

### 3. Refactoring Suggestions
```
/analyze python --refactor-suggestions
```

### 4. Pattern Detection
```
/analyze python --patterns-only
```

## Examples

### Example 1: Vulnerable Python Code
```
/analyze python "
import os
from flask import Flask, request

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    query = f'SELECT * FROM users WHERE user=\"{username}\"'
    os.system(f'ls {username}')
"
```

**Result:**
```
🔴 BLOCK

Security Issues:
1. SQL Injection (CRITICAL)
   → Line 9: String interpolation in query
   → Fix: Use parameterized queries

2. Command Injection (CRITICAL)
   → Line 10: os.system() with user input
   → Fix: subprocess.run(['ls'], shell=False)

3. Hardcoded Database (MEDIUM)
   → No password hashing detected
```

### Example 2: Clean Code
```
/analyze typescript "
async function fetchUser(id: number): Promise<User> {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) throw new Error('Not found');
    return await response.json();
  } catch (error) {
    logger.error('Fetch failed', { id, error });
    throw error;
  }
}
"
```

**Result:**
```
✅ APPROVE

Confidence: 90%

Patterns Recognized:
✅ Async/Await (modern)
✅ Error handling (try/catch)
✅ Type safety (TypeScript)

Suggestions:
- Consider adding retry logic for transient failures
- Type the catch error: catch (error: Error)
```

## Options

| Option | Description |
|--------|-------------|
| `--security-only` | Security analysis only |
| `--patterns-only` | Pattern detection only |
| `--refactor-suggestions` | Refactoring ideas |
| `--no-research` | Skip best practices lookup |
| `--verbose` | Show all agent details |
| `--json` | JSON output format |

## Decision Rules

### Final Decision
- **APPROVE**: confidence > 80% + no CRITICAL issues
- **BLOCK**: CRITICAL security issue or veto from security agent
- **REVIEW**: confidence 60-80% or mixed signals
- **ABSTAIN**: confidence < 60%

### Veto Agents
- Security (confidence > 70% + REJECT)
- Health Monitor (anomalies detected)

## Performance

- **Full analysis**: ~2-5s (parallel agents)
- **Security only**: ~1s
- **Pattern detection**: ~500ms

## Integration

```python
from agents.orchestrator import CodeOrchestrator

orch = CodeOrchestrator()
result = orch.analyze_code(code, language="python")
print(f"Decision: {result['final_decision']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## Related Commands

- `/review` — Code review with explanation
- `/auto-fix` — Automatic fixes for common issues
- `/refactor` — Detailed refactoring guide
