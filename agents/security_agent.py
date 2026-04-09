"""
🔐 SECURITY AGENT V1.0 — Analyse OWASP + Vulnerabilités
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Spécialisé dans la détection d'erreurs de sécurité.
OWASP Top 10:
1. SQL Injection
2. XSS (Cross-Site Scripting)
3. Command Injection
4. Auth/AuthZ failures
5. Secrets exposure
6. Data exposure
7. API abuse
8. Deserialization flaws
9. Logging/Monitoring
10. SSRF/LFI

Domaine: security, vulnerability, owasp, injection, xss, auth.
Personnalité: GUARDIAN
"""

from base_agent import BaseAgent, PERSONALITY_GUARDIAN
from typing import Dict, Any, List
import re
from datetime import datetime


class SecurityAgent(BaseAgent):
    """
    Agent spécialisé dans la détection des vulnérabilités de sécurité.
    """

    def __init__(self):
        super().__init__(
            name="security",
            role="Analyste sécurité — OWASP Top 10, injection, auth, secrets",
            domain_keywords=[
                "security", "sécurité", "vulnerability", "vulnérabilité",
                "injection", "xss", "csrf", "auth", "authentication",
                "authorization", "secret", "token", "password", "api key",
                "owasp", "penetration", "pentest", "risk", "exploit",
                "threat", "breach", "compromised", "exposed"
            ]
        )
        self._vulnerability_cache: List[Dict] = []

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse le code pour vulnérabilités OWASP.
        Context:
            - "code": str
            - "language": str
            - "file_path": str (optionnel)
        """
        code = context.get("code", "")
        language = context.get("language", "unknown")

        if not code.strip():
            return {
                "agent": self.name,
                "confidence": 1.0,
                "recommendation": "ABSTAIN",
                "reasoning": "No code to analyze",
                "action_items": []
            }

        vulnerabilities = []

        # ────────────────────────────────────────────────────────────
        # OWASP 1: SQL INJECTION
        # ────────────────────────────────────────────────────────────

        sql_vulns = self._detect_sql_injection(code, language)
        vulnerabilities.extend(sql_vulns)

        # ────────────────────────────────────────────────────────────
        # OWASP 2: XSS (Cross-Site Scripting)
        # ────────────────────────────────────────────────────────────

        xss_vulns = self._detect_xss(code, language)
        vulnerabilities.extend(xss_vulns)

        # ────────────────────────────────────────────────────────────
        # OWASP 3: COMMAND INJECTION
        # ────────────────────────────────────────────────────────────

        cmd_vulns = self._detect_command_injection(code, language)
        vulnerabilities.extend(cmd_vulns)

        # ────────────────────────────────────────────────────────────
        # OWASP 4: AUTH/AUTHZ FAILURES
        # ────────────────────────────────────────────────────────────

        auth_vulns = self._detect_auth_failures(code)
        vulnerabilities.extend(auth_vulns)

        # ────────────────────────────────────────────────────────────
        # OWASP 5: SECRETS EXPOSURE
        # ────────────────────────────────────────────────────────────

        secret_vulns = self._detect_secrets(code)
        vulnerabilities.extend(secret_vulns)

        # ────────────────────────────────────────────────────────────
        # OWASP 6: DATA EXPOSURE
        # ────────────────────────────────────────────────────────────

        data_vulns = self._detect_data_exposure(code)
        vulnerabilities.extend(data_vulns)

        # Détermine confiance et recommandation
        critical_count = len([v for v in vulnerabilities if v["severity"] == "CRITICAL"])
        high_count = len([v for v in vulnerabilities if v["severity"] == "HIGH"])

        if critical_count > 0:
            confidence = 0.99
            recommendation = "BLOCK"
            reasoning = f"🔴 CRITICAL: {critical_count} critical vulnerabilities detected!"
        elif high_count > 0:
            confidence = 0.95
            recommendation = "REVIEW"
            reasoning = f"🟠 HIGH: {high_count} high-risk vulnerabilities found"
        elif len(vulnerabilities) > 0:
            confidence = 0.85
            recommendation = "REVIEW"
            reasoning = f"🟡 {len(vulnerabilities)} medium/low vulnerabilities found"
        else:
            confidence = 0.9
            recommendation = "APPROVE"
            reasoning = "✅ No obvious vulnerabilities detected"

        action_items = [f"[{v['severity']}] {v['issue']}" for v in vulnerabilities[:5]]

        self._vulnerability_cache.append({
            "timestamp": datetime.now().isoformat(),
            "language": language,
            "vuln_count": len(vulnerabilities),
            "critical_count": critical_count,
            "high_count": high_count
        })

        return {
            "agent": self.name,
            "confidence": confidence,
            "recommendation": recommendation,
            "reasoning": reasoning,
            "vulnerabilities": vulnerabilities,
            "action_items": action_items
        }

    def _detect_sql_injection(self, code: str, language: str) -> List[Dict]:
        """Détecte SQL injection."""
        vulns = []

        if language in ["python", "py"]:
            # Python: .format(), f-strings, + avec user input
            if re.search(r'query\s*=\s*["\'].*\{.*\}["\'].*\.format', code):
                vulns.append({
                    "severity": "HIGH",
                    "owasp": "A1: Injection",
                    "issue": "SQL query built with .format() — vulnerable to injection",
                    "fix": "Use parameterized queries: cursor.execute(query, params)",
                    "example": "SELECT * FROM users WHERE id = ?"
                })

            if "execute(" in code and "+'" in code:
                vulns.append({
                    "severity": "CRITICAL",
                    "owasp": "A1: Injection",
                    "issue": "SQL query concatenated with string — SQL injection risk",
                    "fix": "Use parameterized queries",
                    "example": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
                })

        elif language in ["javascript", "js"]:
            if re.search(r'query.*\+.*user|user.*\+.*query', code):
                vulns.append({
                    "severity": "HIGH",
                    "owasp": "A1: Injection",
                    "issue": "Query concatenation with user input",
                    "fix": "Use parameterized queries or ORMs",
                    "example": "db.query('SELECT * FROM users WHERE id = ?', [userId])"
                })

        return vulns

    def _detect_xss(self, code: str, language: str) -> List[Dict]:
        """Détecte XSS (Cross-Site Scripting)."""
        vulns = []

        # Pas d'echappement HTML
        if "innerHTML" in code:
            vulns.append({
                "severity": "CRITICAL",
                "owasp": "A2: XSS",
                "issue": "Using innerHTML with user input — XSS vulnerability",
                "fix": "Use textContent or sanitize HTML",
                "example": "element.textContent = userInput  // safe\nDOMPurify.sanitize(html)  // for HTML"
            })

        if re.search(r'\.html\(.*request\.|\.html\(.*user|render.*{.*request', code):
            vulns.append({
                "severity": "CRITICAL",
                "owasp": "A2: XSS",
                "issue": "User input rendered in template without escaping",
                "fix": "Use template escaping: {{ variable | escape }}",
                "example": "{{ user_input }}  // auto-escaped in most modern frameworks"
            })

        return vulns

    def _detect_command_injection(self, code: str, language: str) -> List[Dict]:
        """Détecte command injection."""
        vulns = []

        if language in ["python", "py"]:
            if re.search(r'os\.system\(|subprocess\.call\(|shell\s*=\s*True', code):
                vulns.append({
                    "severity": "CRITICAL",
                    "owasp": "A3: Command Injection",
                    "issue": "Using os.system() or shell=True with user input",
                    "fix": "Use subprocess with shell=False and list arguments",
                    "example": "subprocess.run(['ls', '-la'], shell=False)  # safe"
                })

        elif language in ["javascript", "js"]:
            if "child_process.exec" in code:
                vulns.append({
                    "severity": "CRITICAL",
                    "owasp": "A3: Command Injection",
                    "issue": "Using exec() with user input — command injection risk",
                    "fix": "Use execFile() with array arguments",
                    "example": "execFile('ls', ['-la'])  // safer than exec"
                })

        return vulns

    def _detect_auth_failures(self, code: str) -> List[Dict]:
        """Détecte failures d'authentification."""
        vulns = []

        # Hardcoded credentials
        if re.search(r'(username|user)\s*=\s*["\'][^"\']+["\']', code):
            vulns.append({
                "severity": "CRITICAL",
                "owasp": "A4: Auth Failure",
                "issue": "Hardcoded username/password in code",
                "fix": "Move to environment variables or secrets manager",
                "example": "username = os.environ.get('DB_USER')"
            })

        # No password hashing
        if "password =" in code.lower() and "bcrypt" not in code and "argon2" not in code:
            vulns.append({
                "severity": "HIGH",
                "owasp": "A4: Auth Failure",
                "issue": "Password stored/validated without hashing",
                "fix": "Use bcrypt, argon2, or scrypt",
                "example": "hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())"
            })

        # Missing CSRF
        if "POST" in code and "_csrf" not in code and "csrf" not in code.lower():
            vulns.append({
                "severity": "MEDIUM",
                "owasp": "A4: Auth Failure",
                "issue": "No CSRF token validation on POST requests",
                "fix": "Add CSRF token validation",
                "example": "# Use Flask-WTF or equivalent"
            })

        return vulns

    def _detect_secrets(self, code: str) -> List[Dict]:
        """Détecte secrets exposés."""
        vulns = []

        secret_patterns = [
            (r'ghp_[a-zA-Z0-9]{36}', "GitHub token"),
            (r'sk_live_[a-zA-Z0-9]{40,}', "Stripe API key"),
            (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
            (r'mongodb\+srv://[^@]+@', "MongoDB connection string"),
            (r'password\s*=\s*["\']([^"\']+)["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', "API key"),
        ]

        for pattern, secret_type in secret_patterns:
            if re.search(pattern, code):
                vulns.append({
                    "severity": "CRITICAL",
                    "owasp": "A5: Secrets Exposure",
                    "issue": f"Exposed {secret_type}",
                    "fix": "Move to .env or secrets manager",
                    "example": f"{secret_type} = os.environ.get('{secret_type.upper()}')"
                })

        return vulns

    def _detect_data_exposure(self, code: str) -> List[Dict]:
        """Détecte data exposure risks."""
        vulns = []

        # Logs avec données sensibles
        if re.search(r'log.*password|log.*token|log.*secret|log.*api', code, re.IGNORECASE):
            vulns.append({
                "severity": "HIGH",
                "owasp": "A6: Data Exposure",
                "issue": "Sensitive data logged (password, token, secret, API key)",
                "fix": "Filter sensitive fields before logging",
                "example": "logger.info(f'User: {user}, Action: {action}')  # no secrets"
            })

        # HTTPS check missing
        if "http://" in code and "https://" not in code:
            vulns.append({
                "severity": "MEDIUM",
                "owasp": "A6: Data Exposure",
                "issue": "Unencrypted HTTP connections",
                "fix": "Use HTTPS only",
                "example": "url = 'https://api.example.com'"
            })

        return vulns
