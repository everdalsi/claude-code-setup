import { motion } from 'framer-motion';
import { Play, AlertCircle, Zap } from 'lucide-react';
import { useState } from 'react';

interface AutomationPanelProps {
  isRunning: boolean;
  onStart: (niche: string) => void;
}

const nicheOptions = [
  { value: 'gadgets', label: '🔧 Gadgets & Tech', desc: 'Électronique, accessoires' },
  { value: 'home', label: '🏠 Maison & Déco', desc: 'Décoration, mobilier' },
  { value: 'fashion', label: '👕 Mode & Accessoires', desc: 'Vêtements, bijoux' },
  { value: 'sports', label: '⚽ Sports & Fitness', desc: 'Équipement sportif' },
];

export function AutomationPanel({ isRunning, onStart }: AutomationPanelProps) {
  const [selectedNiche, setSelectedNiche] = useState('gadgets');

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">🚀 Lancer l'Automatisation</h2>
          <p className="text-slate-400">Sélectionnez une niche et laissez le système faire le travail</p>
        </div>

        <motion.div
          className="glass rounded-2xl p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="space-y-6">
            {/* Niche selector */}
            <div>
              <h3 className="font-semibold text-white mb-4">Sélectionner une niche:</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {nicheOptions.map(niche => (
                  <motion.button
                    key={niche.value}
                    onClick={() => setSelectedNiche(niche.value)}
                    className={`p-4 rounded-xl text-left transition-all ${
                      selectedNiche === niche.value
                        ? 'glass border-primary-500 shadow-lg shadow-primary-500/50'
                        : 'glass-hover'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <p className="font-semibold text-white">{niche.label}</p>
                    <p className="text-sm text-slate-400 mt-1">{niche.desc}</p>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Warning box */}
            <motion.div
              className="glass rounded-xl p-4 border-l-4 border-yellow-500 bg-yellow-500/5"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <div className="flex gap-3">
                <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-yellow-400 mb-1">Avant de commencer</p>
                  <p className="text-sm text-slate-300">
                    Assurez-vous que vos identifiants Shopify sont configurés dans les paramètres. Le processus prend environ 2-3 minutes.
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Start button */}
            <motion.button
              onClick={() => onStart(selectedNiche)}
              disabled={isRunning}
              className={`w-full btn-primary text-white flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed`}
              whileHover={!isRunning ? { scale: 1.02 } : {}}
              whileTap={!isRunning ? { scale: 0.98 } : {}}
            >
              {isRunning ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <Zap className="w-5 h-5" />
                  </motion.div>
                  Automatisation en cours...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Démarrer l'automatisation
                </>
              )}
            </motion.button>

            {/* Info box */}
            <motion.div
              className="glass rounded-xl p-4 space-y-2"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <p className="font-semibold text-white text-sm">✨ Ce que le système va faire:</p>
              <ul className="text-sm text-slate-300 space-y-1">
                <li>✓ Analyser 100+ produits tendance</li>
                <li>✓ Filtrer les produits gagnants</li>
                <li>✓ Trouver les meilleurs fournisseurs</li>
                <li>✓ Créer votre boutique automatiquement</li>
                <li>✓ Configurer les prix et marges</li>
              </ul>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
