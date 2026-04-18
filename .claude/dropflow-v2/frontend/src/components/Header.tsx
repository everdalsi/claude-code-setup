import { motion } from 'framer-motion';
import { Sparkles, Zap } from 'lucide-react';

interface HeaderProps {
  isHealthy: boolean;
}

export function Header({ isHealthy }: HeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50">
      <div className="glass border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <motion.div
              className="flex items-center gap-3"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <div className="relative">
                <Sparkles className="w-8 h-8 text-primary-500" />
                <motion.div
                  className="absolute inset-0"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}
                >
                  <Zap className="w-8 h-8 text-accent-500 opacity-50" />
                </motion.div>
              </div>
              <div>
                <h1 className="text-2xl font-bold gradient-text">DropFlow</h1>
                <p className="text-xs text-slate-400">Automation Dropshipping v2.0</p>
              </div>
            </motion.div>

            <motion.div
              className="flex items-center gap-3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <div className="text-right">
                <p className="text-sm font-medium text-slate-200">Système</p>
                <p className={`text-xs font-semibold ${isHealthy ? 'text-green-400' : 'text-red-400'}`}>
                  {isHealthy ? '✓ En ligne' : '✗ Hors ligne'}
                </p>
              </div>
              <div className={`w-3 h-3 rounded-full ${isHealthy ? 'bg-green-400' : 'bg-red-400'} ${isHealthy ? 'animate-pulse-glow' : ''}`} />
            </motion.div>
          </div>
        </div>
      </div>
    </header>
  );
}
