import { motion } from 'framer-motion';
import { fadeUp, staggerContainer } from '../../utils/animations';
import { WHY_CHOOSE_US } from '../../constants/constants';
import SectionHeading from '../SectionHeading/SectionHeading';
import { HiOutlineShieldCheck, HiOutlineLightningBolt, HiOutlineBadgeCheck, HiOutlineViewGrid, HiOutlineCursorClick, HiOutlineCloud } from 'react-icons/hi';

const iconMap = {
  secure: HiOutlineShieldCheck,
  fast: HiOutlineLightningBolt,
  accurate: HiOutlineBadgeCheck,
  multiformat: HiOutlineViewGrid,
  easy: HiOutlineCursorClick,
  cloud: HiOutlineCloud,
};

const colorPairs = [
  { bg: 'bg-primary-cyan/10', text: 'text-primary-cyan', border: 'border-primary-cyan/20', glow: 'group-hover:shadow-[0_0_30px_rgba(6,182,212,0.2)]' },
  { bg: 'bg-amber-400/10', text: 'text-amber-400', border: 'border-amber-400/20', glow: 'group-hover:shadow-[0_0_30px_rgba(251,191,36,0.2)]' },
  { bg: 'bg-emerald-400/10', text: 'text-emerald-400', border: 'border-emerald-400/20', glow: 'group-hover:shadow-[0_0_30px_rgba(52,211,153,0.2)]' },
  { bg: 'bg-primary-purple/10', text: 'text-primary-purple', border: 'border-primary-purple/20', glow: 'group-hover:shadow-[0_0_30px_rgba(168,85,247,0.2)]' },
  { bg: 'bg-blue-400/10', text: 'text-blue-400', border: 'border-blue-400/20', glow: 'group-hover:shadow-[0_0_30px_rgba(96,165,250,0.2)]' },
  { bg: 'bg-pink-400/10', text: 'text-pink-400', border: 'border-pink-400/20', glow: 'group-hover:shadow-[0_0_30px_rgba(244,114,182,0.2)]' },
];

export default function WhyChooseUs() {
  return (
    <section className="section-padding relative">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={fadeUp}
        >
          <SectionHeading
            title="Why Choose Gaia Detector"
            subtitle="Built with security, speed, and accuracy in mind. Here's why thousands trust us."
          />
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {WHY_CHOOSE_US.map((item, index) => {
            const Icon = iconMap[item.icon];
            const color = colorPairs[index % colorPairs.length];
            return (
              <motion.div
                key={item.title}
                variants={fadeUp}
                className={`group glass rounded-2xl p-6 transition-all duration-500 hover:bg-white/[0.08] ${color.glow}`}
                whileHover={{ scale: 1.03, y: -5 }}
              >
                <div className={`w-12 h-12 rounded-xl ${color.bg} ${color.border} border flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110`}>
                  <Icon className={`w-6 h-6 ${color.text}`} />
                </div>
                <h3 className="text-white text-lg font-semibold font-heading mb-2">
                  {item.title}
                </h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  {item.description}
                </p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
