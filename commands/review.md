# /review — Code Review Profonde

Analyse en profondeur le code récemment modifié via git diff ou fichiers spécifiés.

## Usage

```bash
/review                  # Revue des changements git (staged + unstaged)
/review src/app.ts       # Revue fichier spécifique
/review src/ lib/        # Revue répertoires
```

## Domaines Couverts

### 1. Qualité & Lisibilité
- ✓ Noms variables/fonctions clairs
- ✓ Longueur fonctions (idéal < 20 lignes)
- ✓ Complexité cyclomatic
- ✓ Code dupliqué (DRY)
- ✓ Comments utiles vs verbeux
- ✓ Types explicites (TypeScript, Python)

### 2. Tests
- ✓ Coverage suffisant (cible > 70%)
- ✓ Tests unitaires vs intégration équilibrés
- ✓ Edge cases couverts
- ✓ Tests "happy path" + erreurs
- ✓ Mocks appropriés ou vraie BD

### 3. Sécurité
- ✓ SQL injection, XSS, command injection
- ✓ Secrets (API keys, tokens, passwords)
- ✓ Auth/autorisation
- ✓ Input validation
- ✓ Dépendances outdated

### 4. Performance
- ✓ Boucles imbriquées evitées
- ✓ Requêtes DB optimisées (N+1 queries)
- ✓ Memory leaks potentiels
- ✓ Rendu inutile (React re-renders)
- ✓ Bundle size impact

---

## Rapport Structuré

Chaque problème trouvé :

```
[PRIORITY: CRITICAL|HIGH|MEDIUM|LOW]
[CATEGORY: quality|tests|security|performance]

Location: src/app.ts:42
Issue: Fonction trop complexe (cyclomatic = 8)

Code:
    40 | function processUser(user) {
    41 |   if (user.age > 18) {
    42 |     if (user.verified) {
    ...

Problem: 
- 8 branches → difficile à tester
- Manque de test cases pour edge cases

Suggestion:
    // Extraire logique en petites fonctions
    const isEligible = (user) => user.age > 18 && user.verified;
    const processEligibleUser = (user) => { ... };

Impact: Medium (facilite tests + maintenabilité)
```

---

## Workflow

1. **Git diff** — Identifier fichiers modifiés
2. **Read** — Lire contexte complet
3. **Analyse statique** — Patterns dangereux (security-reviewer agent)
4. **Test coverage** — Vérifier tests existants
5. **Performance** — Identifier goulots
6. **Rapport** — Synthèse priorités

---

## Output Format

```
═══════════════════════════════════════════════════════════
📋 CODE REVIEW — [fichiers analysés]
═══════════════════════════════════════════════════════════

RÉSUMÉ
  Files: 3
  Lines: 245
  Issues found: 7 (1 CRITICAL, 2 HIGH, 4 MEDIUM)
  Test coverage: 65% (⚠️ < 70%)

───────────────────────────────────────────────────────────
🔴 CRITICAL (1)
───────────────────────────────────────────────────────────

[SEC-001] src/api/auth.ts:28
SQL Injection in login query
    → Use parameterized queries
    → Impact: Account takeover risk

───────────────────────────────────────────────────────────
🟠 HIGH (2)
───────────────────────────────────────────────────────────

[QUAL-001] src/utils/parser.ts:15
Cyclomatic complexity: 8 (target: < 5)
    → Split into smaller functions
    → Add unit tests for each branch

[TEST-001] src/components/Form.tsx
Missing tests for error states
    → 0% coverage for error handling
    → Add error scenarios to test suite

───────────────────────────────────────────────────────────
🟡 MEDIUM (4)
───────────────────────────────────────────────────────────

[PERF-001] src/db/queries.ts:42
N+1 query pattern detected
    → Use JOIN instead of loop

[QUAL-002] src/helpers.ts:8
Variable name not descriptive: "x", "tmp"
    → Rename for clarity

[QUAL-003] src/index.ts:1-50
No TypeScript types on function parameters
    → Add explicit types

[TEST-002] Missing integration test for API
    → Add e2e test for happy path

═══════════════════════════════════════════════════════════
✅ ACTIONS
═══════════════════════════════════════════════════════════

1. Fix CRITICAL SQL injection immediately
2. Refactor 3 HIGH priority items before merge
3. Add tests for error cases
4. Consider performance optimization for DB queries
5. Add TypeScript strict mode

Review ready for commit/PR ✓
═══════════════════════════════════════════════════════════
```

---

## Tips

- Avant chaque PR : `/review`
- Cible : 0 CRITICAL, < 3 HIGH
- Tests : minimum 70% coverage
- Performance : bench avant/après si impactful
