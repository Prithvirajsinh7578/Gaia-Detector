import { motion } from 'framer-motion';
import { fadeUp, staggerContainer } from '../../utils/animations';
import { FEATURES } from '../../constants/constants';
import SectionHeading from '../SectionHeading/SectionHeading';
import { HiOutlineDocumentText, HiOutlinePhotograph, HiOutlineVideoCamera, HiOutlineDocumentSearch } from 'react-icons/hi';

const iconMap = {
  text: HiOutlineDocumentText,
  image: HiOutlinePhotograph,
  video: HiOutlineVideoCamera,
  document: HiOutlineDocumentSearch,
};

const colorMap = {
  text: { bg: 'bg-primary-cyan/10', text: 'text-primary-cyan', border: 'border-primary-cyan/20', glow: 'group-hover:shadow-[0_0_30px_rgba(6,182,212,0.2)]' },
  image: { bg: 'bg-primary-purple/10', text: 'text-primary-purple', border: 'border-primary-purple/20', glow: 'group-hover:shadow-[0_0_30px_rgba(168,85,247,0.2)]' },
  video: { bg: 'bg-amber-400/10', text: 'text-amber-400', border: 'border-amber-400/20', glow: 'group-hover:shadow-[0_0_30px_rgba(251,191,36,0.2)]' },
  document: { bg: 'bg-emerald-400/10', text: 'text-emerald-400', border: 'border-emerald-400/20', glow: 'group-hover:shadow-[0_0_30px_rgba(52,211,153,0.2)]' },
};

export default function Features() {
  return (
    <section id="features" className="section-padding relative">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={fadeUp}
        >
          <SectionHeading
            title="Powerful Detection Features"
            subtitle="Our multi-modal AI engine analyzes content across different formats to detect AI-generated material with precision."
          />
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {FEATURES.map((feature) => {
            const Icon = iconMap[feature.icon];
            const color = colorMap[feature.icon];
            return (
              <motion.div
                key={feature.title}
                variants={fadeUp}
                className={`group glass rounded-2xl p-6 cursor-pointer transition-all duration-500 hover:bg-white/[0.08] ${color.glow}`}
                whileHover={{ scale: 1.03, y: -8 }}
              >
                <div className={`w-14 h-14 rounded-xl ${color.bg} ${color.border} border flex items-center justify-center mb-5 transition-transform duration-300 group-hover:scale-110`}>
                  <Icon className={`w-7 h-7 ${color.text}`} />
                </div>
                <h3 className="text-white text-lg font-semibold font-heading mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  {feature.description}
                </p>
                <div className={`mt-4 flex items-center gap-2 ${color.text} text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-300`}>
                  Learn more
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
