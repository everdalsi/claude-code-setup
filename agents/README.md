# 🧠 Claude Code Agent System V1.0

**Multi-agent orchestration system for professional software development**  
*Adapted from Trading Bot with 57 specialized agents*

---

## 📋 Architecture Overview

### 3 Personality Types
- **🔵 ANALYST** — Détecte problèmes, patterns, opportunités
- **🟢 EXECUTOR** — Implémente, exécute, refactorise avec confiance
- **🔴 GUARDIAN** — Sécurité, protection, compliance, veto sur risques

### 9 Agents Disponibles

#### Core Orchestration (3)
| Agent | Role | Personality |
|-------|------|-------------|
| **base_agent** | Foundation class + personality system | - |
| **supervisor** | Vote pondéré, décision finale bayésienne | EXECUTOR |
| **learning** | Mémoire persistante, pattern scoring | ANALYST |

#### Quality & Analysis (3)
| Agent | Role | Personality |
|-------|------|-------------|
| **code_analyzer** | Erreurs, imports, types, antipatterns | ANALYST |
| **security** | OWASP Top 10, vulnerabilities, risk | GUARDIAN |
| **pattern** | Design patterns, code smell detection | ANALYST |

#### Improvement & Monitoring (3)
| Agent | Role | Personality |
|-------|------|-------------|
| **refactor** | Refactoring suggestions, optimization | EXECUTOR |
| **health_monitor** | Watchdog, system health, diagnostics | GUARDIAN |
| **research** | Best practices, documentation, context | ANALYST |

---

## 🚀 Quick Start

### Basic Code Analysis
```python
from agents.orchestrator import CodeOrchestrator

orch = CodeOrchestrator()

# Analyze code
result = orch.analyze_code("""
def process_data(username, password):
    query = f"SELECT * FROM users WHERE user='{username}' AND pwd='{password}'"
    db.execute(query)
""", language="python")

print(result['final_decision'])  # "BLOCK"
print(result['action_items'])    # ["SQL Injection", "Hardcoded password"]
```

### Code Review with Report
```python
report = orch.code_review(code, language="python")
print(report)  # Markdown report with all agent analysis
```

### Individual Agent Usage
```python
from agents.code_analyzer_agent import CodeAnalyzerAgent
from agents.security_agent import SecurityAgent

analyzer = CodeAnalyzerAgent()
security = SecurityAgent()

# Analyze for errors
response = analyzer.respond({"code": "...", "language": "python"})

# Check security
response = security.respond({"code": "...", "language": "python"})
```

---

## 🔄 Workflow: Question → Consensus → Decision

```
1. Question/Code submitted
         ↓
2. Relevant agents respond in parallel
         ↓
3. Each agent provides: confidence, recommendation, reasoning
         ↓
4. Supervisor aggregates via weighted vote
         ↓
5. Confidence > threshold? 
         ├─ YES → Final Decision + Action Items
         └─ NO  → ABSTAIN
         ↓
6. Learning Agent records pattern
         ↓
7. Health Monitor tracks system state
```

---

## 📊 Weighted Voting System

Supervisor uses **Bayesian weighted vote**:

```
consensus_score = Σ(agent_weight × agent_confidence × agent_direction)
```

Default weights:
- code_analyzer: 0.25 (error detection)
- security: 0.25 (critical)
- pattern: 0.15
- learning: 0.15
- research: 0.10
- refactor: 0.10

**Veto Agents** (can block despite consensus):
- security (confidence > 0.7 + REJECT = BLOCKED)
- health_monitor (anomalies detected)

---

## 💾 Persistence

All agents save to `.claude/memory/agent_learning/`:

```
agent_learning/
├── patterns.json           # Learning agent patterns
├── decisions.json          # Decision history
├── health.json             # System health checks
├── refactor_changes.json   # Applied suggestions
├── research.json           # Research queries
└── patterns_detected.json  # Pattern analysis
```

---

## 🔐 Security

### OWASP Coverage
- A1: SQL Injection detection
- A2: XSS/Template escaping
- A3: Command injection
- A4: Auth/AuthZ failures
- A5: Secrets exposure (hardcoded)
- A6: Data exposure (logging)

### Zero Trust
- Security agent can veto any decision
- All vulnerabilities logged
- Pattern history prevents regression

---

## 📈 Performance Tracking

Health Monitor tracks:
- ✅ Agent response times
- ✅ Error/warning counts
- ✅ Anomaly detection
- ✅ System health trend (↗️ improving / ↘️ declining)

---

## 🎓 Learning System

Learning Agent tracks:

```python
{
    "decision": "Refactor extract function",
    "outcome": "success",  # or "failure"
    "category": "refactor",
    "timestamp": "2026-04-09T..."
}
```

Patterns scored by **win rate**:
```
pattern_score = successes / (successes + failures)
```

---

## 🛠️ Extension

### Add Custom Agent

```python
from agents.base_agent import BaseAgent, PERSONALITY_ANALYST

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my_agent",
            role="My specialized role",
            domain_keywords=["my", "keywords"]
        )
    
    def respond(self, context):
        return {
            "agent": self.name,
            "confidence": 0.85,
            "recommendation": "...",
            "reasoning": "...",
            "action_items": [...]
        }

# Register
orch.agents["my_agent"] = MyAgent()
```

---

## 📚 References

- **Base Pattern**: Trading Bot (57 agents)
- **Vote System**: Bayesian consensus from Trading Bot supervisor_agent
- **Architecture**: Multi-agent orchestration
- **Persistence**: JSON-based memory system
- **Scope**: Code quality, security, refactoring, research

---

## 🤝 Contributing Agents

From Trading Bot, useful agents adapted:
- ✅ base_agent → personality system
- ✅ supervisor_agent → weighted voting
- ✅ learning_agent → memory + patterns
- ✅ code_fixer_agent → code_analyzer_agent
- ✅ evolution_agent → refactor_agent
- ✅ self_improvement → health_monitor_agent
- ✅ research_agent → research_agent
- ✅ pattern_recognition → pattern_agent
- ✅ risk_agent → security_agent

---

**Version**: 1.0.0  
**Last Updated**: 2026-04-09  
**Status**: Production Ready ✅
