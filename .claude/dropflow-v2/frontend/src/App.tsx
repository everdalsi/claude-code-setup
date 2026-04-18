import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ShoppingBag, Store, Zap, TrendingUp } from 'lucide-react';
import { Header } from './components/Header';
import { KPICard } from './components/KPICard';
import { PipelineFlow } from './components/PipelineFlow';
import { StoresGrid } from './components/StoresGrid';
import { AutomationPanel } from './components/AutomationPanel';
import { secureApi } from './services/secureApi';
import { csrfUtils } from './utils/csrf';
import { errorHandler } from './utils/errorHandler';
import { Stats, Store as StoreType } from './types';
import './index.css';

function App() {
  const [stats, setStats] = useState<Stats>({
    total_products: 0,
    total_stores: 0,
    total_revenue: 0,
    total_campaigns: 0,
    uptime_hours: 0,
    revenue_pending: 0,
  });

  const [stores, setStores] = useState<StoreType[]>([]);
  const [isHealthy, setIsHealthy] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(true);
  const [isLoadingStores, setIsLoadingStores] = useState(true);
  const [isRunning, setIsRunning] = useState(false);

  // Load initial data
  useEffect(() => {
    // Initialize CSRF protection on app startup
    csrfUtils.init();

    const loadData = async () => {
      try {
        // Check health
        const healthy = await secureApi.healthCheck();
        setIsHealthy(healthy);

        if (healthy) {
          // Load stats
          const statsData = await secureApi.getStats();
          setStats(statsData);
          setIsLoadingStats(false);

          // Load stores
          const storesData = await secureApi.getStores();
          setStores(storesData);
          setIsLoadingStores(false);
        }
      } catch (error) {
        const errorInfo = errorHandler.log(error, 'loadData');
        console.error(errorInfo.message);
        setIsHealthy(false);
        setIsLoadingStats(false);
        setIsLoadingStores(false);
      }
    };

    loadData();

    // Refresh every 5 seconds
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStartAutomation = async (niche: string) => {
    setIsRunning(true);
    try {
      const result = await secureApi.runPipeline(niche);

      // Refresh data after automation
      const statsData = await secureApi.getStats();
      setStats(statsData);

      const storesData = await secureApi.getStores();
      setStores(storesData);

      // Show success message
      if (result.success) {
        alert(`✅ Automatisation complétée!\n\nProduit: ${result.product?.name}\nScore: ${result.product?.score}`);
      }
    } catch (error) {
      const errorInfo = errorHandler.log(error, 'handleStartAutomation');
      alert(`❌ ${errorInfo.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Header isHealthy={isHealthy} />

      {/* Main content */}
      <main className="pt-24">
        {/* Top section - Stats */}
        <section className="max-w-7xl mx-auto px-6 py-12 space-y-8">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="space-y-4"
          >
            <h2 className="text-4xl font-bold text-white">
              Bienvenue dans <span className="gradient-text">DropFlow</span>
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl">
              Votre plateforme d'automatisation dropshipping. Créez des boutiques rentables en quelques minutes, sans effort technique.
            </p>
          </motion.div>

          {/* KPI Cards */}
          {!isHealthy ? (
            <motion.div
              className="glass rounded-2xl p-8 border-l-4 border-red-500"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <p className="text-red-400 font-semibold mb-2">⚠️ Serveur non disponible</p>
              <p className="text-slate-300 text-sm">
                Assurez-vous que le serveur FastAPI est en cours d'exécution sur le port 8000:
              </p>
              <code className="block bg-slate-900 p-3 rounded mt-3 text-sm text-primary-400">
                python -m uvicorn main:app --reload
              </code>
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <KPICard
                title="Produits Trouvés"
                value={isLoadingStats ? '...' : stats.total_products}
                icon={ShoppingBag}
                delay={0.1}
              />
              <KPICard
                title="Boutiques Créées"
                value={isLoadingStats ? '...' : stats.total_stores}
                icon={Store}
                trend={12}
                delay={0.2}
              />
              <KPICard
                title="Revenu Total"
                value={isLoadingStats ? '...' : `$${stats.total_revenue.toFixed(2)}`}
                icon={TrendingUp}
                trend={28}
                delay={0.3}
              />
              <KPICard
                title="Campagnes"
                value={isLoadingStats ? '...' : stats.total_campaigns}
                icon={Zap}
                delay={0.4}
              />
            </div>
          )}
        </section>

        {/* Main workflow section */}
        <section className="max-w-7xl mx-auto px-6 py-12 space-y-12">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left column - Pipeline and automation */}
            <div className="lg:col-span-2 space-y-12">
              <PipelineFlow />
              <AutomationPanel isRunning={isRunning} onStart={handleStartAutomation} />
            </div>

            {/* Right column - Settings/Help */}
            <motion.div
              className="space-y-6"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <div className="glass rounded-2xl p-6 space-y-4">
                <h3 className="font-bold text-white mb-4">⚙️ Configuration</h3>

                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-slate-400 block mb-2">Budget quotidien ($)</label>
                    <input
                      type="number"
                      defaultValue="15"
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500"
                    />
                  </div>

                  <div>
                    <label className="text-sm text-slate-400 block mb-2">Marge bénéficiaire min (%)</label>
                    <input
                      type="number"
                      defaultValue="30"
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500"
                    />
                  </div>

                  <div>
                    <label className="text-sm text-slate-400 block mb-2">Recherches mensuelles min</label>
                    <input
                      type="number"
                      defaultValue="5000"
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-primary-500"
                    />
                  </div>
                </div>

                <button className="w-full btn-secondary text-white text-sm mt-4">
                  Enregistrer les paramètres
                </button>
              </div>

              <div className="glass rounded-2xl p-6 space-y-3">
                <h3 className="font-bold text-white mb-3">💡 Conseils</h3>
                <div className="space-y-2 text-sm">
                  <p className="text-slate-300">
                    <span className="text-primary-400 font-semibold">→</span> Commencez avec un budget faible ($15/jour)
                  </p>
                  <p className="text-slate-300">
                    <span className="text-primary-400 font-semibold">→</span> Testez d'abord avec 'Gadgets'
                  </p>
                  <p className="text-slate-300">
                    <span className="text-primary-400 font-semibold">→</span> Augmentez si vous voyez des ventes
                  </p>
                </div>
              </div>

              <div className="glass rounded-2xl p-6 space-y-3">
                <h3 className="font-bold text-white mb-3">🆘 Besoin d'aide ?</h3>
                <button className="w-full btn-secondary text-white text-sm">
                  📖 Voir la documentation
                </button>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Stores section */}
        <section className="max-w-7xl mx-auto px-6 py-12">
          <StoresGrid stores={stores} isLoading={isLoadingStores} />
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 mt-12">
          <div className="max-w-7xl mx-auto px-6 py-8 text-center text-slate-500 text-sm">
            <p>DropFlow v2.0 • Automatisation Dropshipping Complète</p>
            <p className="mt-2">✨ Créé avec FastAPI, React et ❤️</p>
          </div>
        </footer>
      </main>
    </div>
  );
}

export default App;
