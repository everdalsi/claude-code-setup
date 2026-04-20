import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: number | string;
  icon: LucideIcon;
  trend?: number;
  delay?: number;
}

export function KPICard({ title, value, icon: Icon, trend, delay = 0 }: KPICardProps) {
  return (
    <motion.div
      className="kpi-card hover:shadow-2xl hover:shadow-primary-500/20"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      whileHover={{ y: -5 }}
    >
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <p className="text-slate-400 text-sm font-medium mb-2">{title}</p>
          <h3 className="text-4xl font-bold text-white">{value}</h3>
          {trend !== undefined && (
            <p className={`text-sm mt-2 ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
            </p>
          )}
        </div>
        <motion.div
          className="p-4 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20"
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          <Icon className="w-8 h-8 text-primary-400" />
        </motion.div>
      </div>

      <div className="h-1 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
    </motion.div>
  );
}
