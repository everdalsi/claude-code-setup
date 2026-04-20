import { motion } from 'framer-motion';
import { Search, CheckCircle, Zap, Rocket } from 'lucide-react';

interface Step {
  id: number;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

const steps: Step[] = [
  {
    id: 1,
    name: 'RECHERCHE',
    description: 'Trouver les produits tendance',
    status: 'completed'
  },
  {
    id: 2,
    name: 'VALIDATION',
    description: 'Vérifier le potentiel',
    status: 'completed'
  },
  {
    id: 3,
    name: 'CRÉATION',
    description: 'Créer la boutique',
    status: 'pending'
  },
  {
    id: 4,
    name: 'LANCEMENT',
    description: 'Lancer les campagnes',
    status: 'pending'
  }
];

const icons = [Search, CheckCircle, Zap, Rocket];

export function PipelineFlow() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">Processus d'Automatisation</h2>
        <p className="text-slate-400">4 étapes pour créer et lancer votre boutique automatiquement</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
        {/* Connecting line */}
        <div className="hidden md:block absolute top-16 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-500 via-primary-500 to-transparent" />

        {steps.map((step, idx) => {
          const Icon = icons[idx];
          const isCompleted = step.status === 'completed';
          const isRunning = step.status === 'running';

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="relative"
            >
              <div className="glass rounded-2xl p-6 text-center">
                <motion.div
                  className={`w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center
                    ${isCompleted ? 'bg-green-500/20 border-2 border-green-500' : ''}
                    ${isRunning ? 'bg-primary-500/20 border-2 border-primary-500' : ''}
                    ${step.status === 'pending' ? 'bg-slate-700/50 border-2 border-slate-600' : ''}
                  `}
                >
                  {isRunning && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <Icon className={`w-8 h-8 ${isCompleted ? 'text-green-400' : 'text-primary-400'}`} />
                    </motion.div>
                  )}
                  {!isRunning && (
                    <Icon className={`w-8 h-8 ${isCompleted ? 'text-green-400' : 'text-slate-500'}`} />
                  )}
                </motion.div>

                <h3 className="font-bold text-white mb-1">{step.name}</h3>
                <p className="text-sm text-slate-400 mb-3">{step.description}</p>

                <div className="text-xs font-semibold">
                  {isCompleted && <span className="text-green-400">✓ Complété</span>}
                  {isRunning && <span className="text-primary-400 animate-pulse">⟳ En cours...</span>}
                  {step.status === 'pending' && <span className="text-slate-500">◯ En attente</span>}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      <motion.div
        className="glass rounded-2xl p-6 border-l-4 border-primary-500"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <h3 className="font-semibold text-white mb-2">📋 Qu'est-ce qui se passe ?</h3>
        <p className="text-sm text-slate-300">
          Le système scanne automatiquement les produits tendance, filtre les meilleurs, trouve des fournisseurs et crée votre boutique. Tout se fait sans intervention manuelle !
        </p>
      </motion.div>
    </div>
  );
}
