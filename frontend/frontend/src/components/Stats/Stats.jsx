import { motion } from 'framer-motion';
import { fadeUp, staggerContainer } from '../../utils/animations';
import { useCountUp } from '../../hooks/useCountUp';
import { HiOutlineDocumentText, HiOutlineChartBar, HiOutlineCollection, HiOutlineClock } from 'react-icons/hi';

const statIcons = [HiOutlineDocumentText, HiOutlineChartBar, HiOutlineCollection, HiOutlineClock];

function StatCard({ label, value, suffix, prefix, displayValue, index }) {
  const { count, ref } = useCountUp(value, 2000, prefix || '', suffix || '');
  const Icon = statIcons[index];
  const colors = [
    { gradient: 'from-primary-cyan to-blue-500', glow: 'glow-cyan', text: 'text-primary-cyan' },
    { gradient: 'from-emerald-400 to-green-500', glow: 'glow-cyan', text: 'text-emerald-400' },
    { gradient: 'from-primary-purple to-pink-500', glow: 'glow-purple', text: 'text-primary-purple' },
    { gradient: 'from-amber-400 to-orange-500', glow: '', text: 'text-amber-400' },
  ];
  const color = colors[index];

  return (
    <motion.div
      ref={ref}
      variants={fadeUp}
      className="glass rounded-2xl p-6 md:p-8 text-center group hover:bg-white/[0.08] transition-all duration-300"
      whileHover={{ scale: 1.05, y: -5 }}
    >
      <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${color.gradient} bg-opacity-10 flex items-center justify-center mx-auto mb-4 ${color.glow}`}
        style={{ background: `linear-gradient(135deg, ${color.gradient.includes('cyan') ? 'rgba(6,182,212,0.15)' : color.gradient.includes('emerald') ? 'rgba(52,211,153,0.15)' : color.gradient.includes('purple') ? 'rgba(168,85,247,0.15)' : 'rgba(251,191,36,0.15)'}, transparent)` }}
      >
        <Icon className={`w-7 h-7 ${color.text}`} />
      </div>
      <div className={`text-3xl md:text-4xl font-bold font-heading mb-2 ${color.text}`}>
        {count}
      </div>
      <div className="text-gray-400 text-sm font-medium uppercase tracking-wider">
        {label}
      </div>
    </motion.div>
  );
}

export default function Stats() {
  const stats = [
    { label: 'Files Analyzed', value: 100000, suffix: '+', prefix: '', displayValue: '100K+' },
    { label: 'Accuracy', value: 95, suffix: '%', prefix: '', displayValue: '95%' },
    { label: 'Supported Formats', value: 10, suffix: '+', prefix: '', displayValue: '10+' },
    { label: 'Response Time', value: 5, suffix: ' sec', prefix: '<', displayValue: '<5 sec' },
  ];

  return (
    <section className="section-padding relative">
      <div className="max-w-7xl mx-auto">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6"
        >
          {stats.map((stat, i) => (
            <StatCard key={stat.label} {...stat} index={i} />
          ))}
        </motion.div>
      </div>
    </section>
  );
}
