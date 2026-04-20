# DropFlow Frontend - v2.0

Dashboard futuriste et professionnel pour la plateforme d'automatisation dropshipping DropFlow.

## 🎨 Design

- **Moderne & Premium**: Interface ultra-épurée avec gradient bleu/violet sophistiqué
- **Ultra-Intuitif**: Conçu pour que même votre grand-mère puisse l'utiliser
- **Responsive**: Fonctionne parfaitement sur mobile, tablet et desktop
- **Animations**: Transitions fluides et micro-interactions qui ravissent
- **Dark Mode**: Thème sombre moderne avec contraste optimal

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

The app will be available at `http://localhost:5173`

## 📋 Requirements

- Backend API running on `http://localhost:8000`
- Node.js 16+
- npm or yarn

## 🏗️ Architecture

```
src/
├── components/        # React components
│   ├── Header.tsx         # Top navigation bar
│   ├── KPICard.tsx        # Statistics cards (4 KPIs)
│   ├── PipelineFlow.tsx   # 4-step automation workflow visualization
│   ├── StoresGrid.tsx     # Created stores display
│   └── AutomationPanel.tsx # Launch automation
├── services/          # API communication
│   └── api.ts             # Fetch wrapper for backend
├── types.ts           # TypeScript interfaces
├── App.tsx            # Main application
└── index.css          # Tailwind + custom styles
```

## 🎯 Features

### Dashboard
- **4 Main KPIs**: Products found, Stores created, Total revenue, Campaigns
- **Real-time Stats**: Updates every 5 seconds from API
- **System Status**: Green/red indicator showing API health

### Pipeline Visualization
- **4 Steps**: RECHERCHE → VALIDATION → CRÉATION → LANCEMENT
- **Visual Status**: Pending, Running, Completed indicators
- **Clear Explanations**: What each step does in simple language

### Store Management
- **Grid Display**: Cards showing all created stores
- **Key Info**: Product name, niche, domain, revenue, status
- **Beautiful Cards**: Hover effects and animations

### Automation Control
- **Niche Selection**: 4 popular niches (Gadgets, Home, Fashion, Sports)
- **One-Click Launch**: Start full automation with one button
- **Progress Indicator**: Shows when automation is running
- **Helpful Tips**: Before/after guidance

### Settings Panel
- **Simple Config**: Budget, profit margin, minimum searches
- **Tips Section**: Best practices for success
- **Help & Support**: Links to documentation

## 🛠️ Technology Stack

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Delightful animations
- **Recharts**: Charts and graphs (ready for future use)
- **Lucide React**: Beautiful icon library

## 🌐 API Integration

Frontend expects backend on `http://localhost:8000` with these endpoints:

```
GET  /health          - Server health check
GET  /stats           - Platform statistics
GET  /stores          - List all stores
GET  /products        - List all products
POST /pipeline        - Run full automation
POST /find-product    - Find trending product
POST /find-supplier   - Find supplier for product
POST /create-store    - Create store manually
```

## 📱 Responsive Breakpoints

- **Mobile**: Full-width, stacked layout (<768px)
- **Tablet**: 2-column grid (768px-1024px)
- **Desktop**: 4-column grid, side panels (>1024px)

## 🎨 Color Scheme

- **Primary**: `#667eea` (Blue)
- **Accent**: `#764ba2` (Purple)
- **Background**: Deep slate (`#0f172a`)
- **Cards**: Glass effect with transparency
- **Text**: Light slate with proper contrast

## ✨ Key Design Decisions

1. **Glass Morphism**: Semi-transparent cards with backdrop blur for modern look
2. **Gradient Accents**: Primary-to-accent gradient used strategically
3. **Animated KPIs**: Subtle floating animation on stat cards
4. **Smooth Transitions**: All interactions have 300ms transitions
5. **Micro-interactions**: Hover states, button scales, icon animations
6. **Clear Typography**: Large headings with proper hierarchy
7. **Ample Whitespace**: Breathing room between sections
8. **Icon Integration**: Every feature has a clear icon

## 🔄 Data Flow

```
App.tsx
├── useEffect: Fetch stats + stores every 5s
├── Header: Show system health
├── KPI Cards: Display stats
├── Pipeline Flow: Show workflow
├── AutomationPanel: Launch automation
├── Stores Grid: Show created stores
└── Settings: Configure parameters
```

## 🚀 Deployment

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Deploy dist/ folder to:
# - Vercel
# - Netlify
# - Any static host
```

For backend proxy, ensure your host forwards `/api/*` requests to backend.

## 🐛 Troubleshooting

**"Cannot connect to server"**
- Ensure backend is running: `python -m uvicorn main:app --reload`
- Check backend is on port 8000
- Verify CORS is enabled in FastAPI

**Stats not updating**
- Check browser console for fetch errors
- Verify API endpoints are correct
- Check backend logs for errors

**Styles not loading**
- Run `npm install` to ensure Tailwind is installed
- Clear browser cache (Ctrl+Shift+R)
- Rebuild: `npm run build`

## 📝 Next Steps (Future)

- [ ] Product charts and analytics
- [ ] Store performance dashboard
- [ ] Revenue tracking over time
- [ ] Settings persistence to backend
- [ ] Dark/light theme toggle
- [ ] Shopify store links
- [ ] Email notifications
- [ ] Advanced filtering

## 📄 License

MIT - See LICENSE file
