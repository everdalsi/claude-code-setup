import { motion } from 'framer-motion';
import { ExternalLink, TrendingUp } from 'lucide-react';
import { Store } from '../types';

interface StoresGridProps {
  stores: Store[];
  isLoading: boolean;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return 'bg-green-500/20 text-green-400 border-green-500/50';
    case 'completed': return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
    default: return 'bg-slate-700/50 text-slate-400 border-slate-600/50';
  }
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'active': return '🟢 Active';
    case 'completed': return '✓ Complétée';
    default: return '⏳ Pending';
  }
};

export function StoresGrid({ stores, isLoading }: StoresGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map(i => (
          <div key={i} className="glass rounded-2xl p-6 shimmer" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white mb-1">Boutiques Créées</h2>
        <p className="text-slate-400">{stores.length} {stores.length === 1 ? 'boutique' : 'boutiques'} en ligne</p>
      </div>

      {stores.length === 0 ? (
        <motion.div
          className="glass rounded-2xl p-12 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <p className="text-slate-400 mb-4">Aucune boutique créée pour le moment</p>
          <p className="text-sm text-slate-500">Lancez l'automatisation pour créer votre première boutique</p>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {stores.map((store, idx) => (
            <motion.div
              key={store.id}
              className="glass rounded-2xl overflow-hidden hover:shadow-2xl hover:shadow-primary-500/20 transition-all duration-300 group"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              whileHover={{ y: -5 }}
            >
              {/* Background gradient */}
              <div className="h-32 bg-gradient-to-r from-primary-500/30 to-accent-500/30 relative overflow-hidden">
                <motion.div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  initial={{ backgroundPosition: '0% 0%' }}
                  animate={{ backgroundPosition: '100% 100%' }}
                  transition={{ duration: 3, repeat: Infinity }}
                />
              </div>

              {/* Content */}
              <div className="p-6">
                <h3 className="font-bold text-lg text-white mb-1 line-clamp-2">
                  {store.product_name}
                </h3>
                <p className="text-sm text-slate-400 mb-4">{store.niche}</p>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Domaine:</span>
                    <code className="text-xs bg-slate-800/50 px-2 py-1 rounded text-primary-400">
                      {store.domain}
                    </code>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400">Revenu:</span>
                    <span className="font-semibold text-green-400">
                      ${store.revenue.toFixed(2)}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp className="w-4 h-4 text-slate-400" />
                  <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(store.status)}`}>
                    {getStatusLabel(store.status)}
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <p className="text-xs text-slate-500 mb-3">
                    Créée {new Date(store.created_at).toLocaleDateString('fr-FR')}
                  </p>
                  <motion.button
                    className="w-full flex items-center justify-center gap-2 text-sm font-semibold text-primary-400 hover:text-primary-300 transition-colors"
                    whileHover={{ x: 5 }}
                  >
                    Voir détails
                    <ExternalLink className="w-4 h-4" />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
