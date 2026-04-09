# /auto-fix — Auto-correction Intelligente

Analyse tous les fichiers du projet et corrige automatiquement erreurs, lint, tests et dépendances.

## Usage

```bash
/auto-fix                    # Toutes les corrections
/auto-fix typing             # Seulement erreurs de typage
/auto-fix lint               # Seulement violations lint
/auto-fix tests              # Seulement tests échoués
/auto-fix deps               # Seulement dépendances
/auto-fix typing lint        # Combinaisons
```

---

## Domaines de Correction

### 1. Erreurs de Typage
**Trigger :** `npm run type-check` ou `tsc --noEmit`

**Auto-fixes :**
- ✓ Ajouter types manquants (`:` any → inférer type)
- ✓ Fixer type incompatibles (string vs number)
- ✓ Ajouter null checks (`?.` optional chaining)
- ✓ Fixer return types
- ✓ Corriger generics mal typés

**Exemple :**
```typescript
// ❌ Avant
function add(a, b) { return a + b; }

// ✅ Après
function add(a: number, b: number): number { return a + b; }
```

**Command :** `npx tsc --noEmit && npx tsc --pretty false`

---

### 2. Violations Lint (ESLint)
**Trigger :** `npm run lint -- --fix`

**Auto-fixes :**
- ✓ Indentation, spacing, semicolons
- ✓ Unused variables/imports
- ✓ Naming conventions (camelCase, PascalCase)
- ✓ No-console, no-debugger
- ✓ Import sorting

**Exemple :**
```javascript
// ❌ Avant
const x=5;console.log(x)
function MyFunc( ) { }

// ✅ Après
const x = 5;
function myFunc() { }
```

**Command :** `npx eslint . --fix` (ou `prettier --write .`)

---

### 3. Tests Échoués
**Trigger :** `npm test -- --bail`

**Auto-fixes :**
- ✓ Tests avec assertions simples (expect exists)
- ✓ Tests timeout (augmenter)
- ✓ Mock setup incorrect
- ✓ Imports manquants dans tests
- ❌ Logic errors (pas fixable auto)

**Process :**
1. Lancer tests
2. Parser output (failed tests list)
3. Read test file + code source
4. Fixer imports, mocks, asserts simples
5. Commit si 100% pass

**Exemple :**
```javascript
// ❌ Avant
test('should add', () => {
  expect(add(1, 2))  // assertion incomplète
})

// ✅ Après
test('should add', () => {
  expect(add(1, 2)).toBe(3)
})
```

---

### 4. Dépendances Obsolètes
**Trigger :** `npm outdated` ou `npm audit`

**Auto-fixes :**
- ✓ Minor updates (1.2.3 → 1.3.0)
- ✓ Patch updates (1.2.3 → 1.2.4)
- ✓ Audit vulnerabilities (auto-fix simples)
- ❌ Major versions (demander confirmation)

**Process :**
1. Run `npm outdated`
2. Update minor/patch : `npm update`
3. Run audit : `npm audit fix`
4. Run tests → vérifier rien ne break
5. Commit si OK

**Exemple :**
```bash
# ❌ Avant
eslint: 8.10.0 (current) 8.55.0 (latest)

# ✅ Après
npm update eslint@latest
# tests run OK → commit
```

---

## Workflow Complet

```
1. GIT CHECK
   - Repo clean? (no uncommitted changes)
   - On feature branch? (not main)

2. TYPE-CHECK
   npm run type-check 2>&1 | parse errors
   → Fix types automatiquement
   → Commit: "fix: TypeScript type errors"
   → Run type-check again

3. LINT
   npm run lint -- --fix
   → Commit: "style: ESLint auto-fixes"

4. TESTS
   npm test
   → Si fail: parse output
   → Fix imports/mocks/asserts
   → Commit: "test: fix failing tests"
   → Run tests again

5. DEPS
   npm outdated → npm update
   npm audit fix
   npm test → vérifier
   → Commit: "chore: update dependencies"

6. SUMMARY
   Files changed: X
   Commits: Y
   All passing: ✓
```

---

## Commit Strategy

**Chaque correction = 1 commit :**

```bash
✓ Commit 1: "fix: TypeScript type errors (12 files)"
✓ Commit 2: "style: ESLint auto-fixes"
✓ Commit 3: "test: fix failing tests (3 suites)"
✓ Commit 4: "chore: update dependencies"

Message format:
[type]: [description]
[optional: file count or details]

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

---

## Safety Checks

⚠️ Avant d'exécuter :

- [ ] Git status clean (ou stash changes)
- [ ] Pas sur main branch
- [ ] npm install / pip install OK
- [ ] Tests actuellement passent (ou au moins running)
- [ ] Node/Python version compatible

⚠️ Si ça break :

- [ ] Git reset --hard HEAD~N (undo N commits)
- [ ] Identifier le problème (test output)
- [ ] Fix manuellement
- [ ] Re-run /auto-fix après

---

## Output Format

```
═══════════════════════════════════════════════════════════
🔧 AUTO-FIX REPORT
═══════════════════════════════════════════════════════════

✅ SCAN COMPLETED
  Files: 245 total
  Issues found: 34

───────────────────────────────────────────────────────────
📝 TYPE-CHECK (8 fixes)
───────────────────────────────────────────────────────────
  ✓ src/app.ts:12 — Added return type `: Promise<void>`
  ✓ src/utils.ts:45 — Fixed parameter type (any → string)
  ✓ src/types.ts:8 — Added missing generic <T>
  [5 more fixes...]

  Commit: fix: TypeScript type errors (8 files)

───────────────────────────────────────────────────────────
🎨 LINT (12 fixes)
───────────────────────────────────────────────────────────
  ✓ src/index.ts — Fixed indentation + semicolons
  ✓ src/api.ts — Removed unused imports (4)
  ✓ src/helpers.ts — Rename variables (camelCase)
  [9 more fixes...]

  Commit: style: ESLint auto-fixes

───────────────────────────────────────────────────────────
✓ TESTS (2 fixes)
───────────────────────────────────────────────────────────
  ✓ src/__tests__/app.test.ts:22 — Fixed assertion
  ✓ src/__tests__/utils.test.ts:8 — Added missing import

  Commit: test: fix failing tests (2 suites)

───────────────────────────────────────────────────────────
⬆️ DEPENDENCIES (1 fix)
───────────────────────────────────────────────────────────
  ✓ Updated eslint: 8.10.0 → 8.55.0
  ✓ Updated typescript: 5.0.2 → 5.3.3
  ✓ npm audit: 5 vulnerabilities fixed

  Commit: chore: update dependencies

═══════════════════════════════════════════════════════════
✅ ALL FIXES APPLIED
═══════════════════════════════════════════════════════════

Summary:
  Files changed: 18
  Commits created: 4
  Tests passing: ✓ 45/45
  Type errors: 0
  Lint issues: 0

Ready for PR ✓

═══════════════════════════════════════════════════════════
```

---

## Tips

- **Avant PR :** `/auto-fix` pour nettoyer le code
- **Régulier :** `/auto-fix deps` chaque semaine
- **Safe :** Sur feature branch, jamais main
- **Review :** Vérifier chaque commit après
- **Fail :** Reset et fix manuellement si nécessaire

---

## Combinaisons Utiles

```bash
# Avant commit
/auto-fix typing lint tests

# Avant merge
/auto-fix

# Maintenance routine
/auto-fix deps

# Fix rapide
/auto-fix lint
```
