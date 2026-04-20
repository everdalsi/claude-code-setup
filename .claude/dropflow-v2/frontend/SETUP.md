# 🚀 DropFlow Frontend - Guide de Configuration

Guide complet pour configurer et lancer le frontend DropFlow v2.

## ✅ Prérequis

- **Node.js** 16+ ([télécharger](https://nodejs.org))
- **npm** (inclus avec Node.js)
- **Backend FastAPI** en cours d'exécution sur `http://localhost:8000`

## 📦 Installation

```bash
# 1. Naviguez vers le dossier frontend
cd ~/.claude/dropflow-v2/frontend

# 2. Installez les dépendances
npm install

# Cela installe:
# - react & react-dom
# - vite (build tool ultra-rapide)
# - tailwindcss (styling)
# - framer-motion (animations)
# - lucide-react (icons)
# - recharts (graphiques)
```

## 🏃 Lancer le serveur de développement

```bash
npm run dev
```

Le frontend sera accessible à: **http://localhost:5173**

Vous verrez un message comme:
```
Local:   http://localhost:5173/
Press q to quit
```

## 🎯 Vérifier la connexion

1. Ouvrez http://localhost:5173
2. Regardez le header:
   - ✓ Vert = Backend connecté
   - ✗ Rouge = Backend non disponible

Si le backend n'est pas disponible:
```bash
# Terminal différent, allez au dossier backend
cd ~/.claude/dropflow-v2/backend

# Activez l'environnement virtuel
source venv/bin/activate  # ou venv\Scripts\activate sur Windows

# Lancez le backend
python -m uvicorn main:app --reload
```

## 🛠️ Fichiers Importants

```
frontend/
├── src/
│   ├── App.tsx              # Application principale
│   ├── components/          # Composants React réutilisables
│   │   ├── Header.tsx       # Barre de navigation
│   │   ├── KPICard.tsx      # Cartes de statistiques
│   │   ├── PipelineFlow.tsx # Workflow des 4 étapes
│   │   ├── StoresGrid.tsx   # Grille des boutiques
│   │   └── AutomationPanel.tsx # Panneau de lancement
│   ├── services/
│   │   └── api.ts           # Appels API au backend
│   ├── types.ts             # Types TypeScript
│   └── index.css            # Styles Tailwind
├── index.html               # Fichier HTML principal
├── package.json             # Dépendances npm
├── vite.config.ts           # Configuration Vite
└── tailwind.config.js       # Configuration Tailwind
```

## 🎨 Personnaliser l'interface

### Changer les couleurs

Modifiez `tailwind.config.js`:
```javascript
colors: {
  primary: {
    500: '#667eea',  // Bleu primaire
  },
  accent: {
    500: '#764ba2',  // Violet accent
  }
}
```

### Ajouter une section

Créez un nouveau composant dans `src/components/`:
```bash
touch src/components/NewFeature.tsx
```

Exemple:
```typescript
import { motion } from 'framer-motion';

export function NewFeature() {
  return (
    <motion.div
      className="glass rounded-2xl p-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <h2 className="text-2xl font-bold text-white">Nouvelle Fonctionnalité</h2>
    </motion.div>
  );
}
```

Puis importez-le dans `App.tsx`.

## 📱 Mode Responsive

L'interface s'adapte automatiquement:

- **Mobile** (<768px): Une colonne, empilé
- **Tablet** (768px-1024px): Deux colonnes
- **Desktop** (>1024px): Grille complète

Testez dans Chrome DevTools:
```
F12 → Toggle Device Toolbar (Ctrl+Shift+M)
```

## 🔗 Intégration API

L'app se connecte automatiquement au backend sur:
```
http://localhost:8000
```

Endpoints utilisés:
- `GET /health` - Vérifier la santé du serveur
- `GET /stats` - Récupérer les statistiques
- `GET /stores` - Récupérer les boutiques
- `POST /pipeline?niche=X` - Lancer l'automatisation

## 🐛 Dépannage

### Erreur: "Cannot find module 'react'"
```bash
npm install
```

### Erreur: "PORT 5173 is already in use"
```bash
# Trouvez et fermez l'autre processus, ou changez le port:
# Modifiez vite.config.ts:
port: 5174  // Autre port libre
```

### Backend timeout errors
- Vérifiez que le backend est en cours d'exécution
- Vérifiez les logs du backend pour les erreurs
- Attendez 2-3 secondes après le lancement du backend

### Styles ne s'appliquent pas
```bash
# Videz le cache et relancez
rm -rf node_modules/.vite
npm run dev
```

## 🏗️ Build pour Production

```bash
# Créer une build optimisée
npm run build

# Cela crée un dossier 'dist/' avec les fichiers statiques
```

Pour servir localement:
```bash
npm run preview
```

Pour déployer:
- Uploadez le contenu de `dist/` sur un serveur web (Vercel, Netlify, etc.)
- Configurez les proxies pour les appels `/api/*` vers le backend

## 📚 Ressources

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Framer Motion](https://www.framer.com/motion/)
- [Vite Guide](https://vitejs.dev/)
- [TypeScript](https://www.typescriptlang.org/)

## 🎓 Concepts Clés

### Animations avec Framer Motion
```typescript
<motion.div
  initial={{ opacity: 0 }}      // État initial
  animate={{ opacity: 1 }}       // État animé
  transition={{ duration: 0.5 }} // Configuration animation
>
  Content
</motion.div>
```

### Styles Tailwind
```html
<div className="bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg p-6">
  Tailwind classes are applied directly to elements
</div>
```

### Appels API
```typescript
const data = await api.getStats();
```

## 🚀 Prochaines étapes

- [ ] Ajouter des graphiques avec Recharts
- [ ] Implémenter le mode sombre/clair
- [ ] Ajouter des notifications toast
- [ ] Créer une page de détails de boutique
- [ ] Intégrer les paramètres du backend
- [ ] Ajouter l'authentification

## 💬 Support

Pour les questions:
1. Vérifiez les logs du navigateur (F12)
2. Vérifiez les logs du backend
3. Consultez la documentation fournie

---

**Prêt ?** Lancez le serveur et commencez ! 🎉
