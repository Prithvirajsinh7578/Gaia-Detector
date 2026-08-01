import { motion } from 'framer-motion';
import { fadeUp, staggerContainer } from '../../utils/animations';
import { HOW_IT_WORKS_STEPS } from '../../constants/constants';
import SectionHeading from '../SectionHeading/SectionHeading';
import { HiOutlineCloudUpload, HiOutlineCog, HiOutlineChip, HiOutlineDocumentReport } from 'react-icons/hi';

const iconMap = {
  upload: HiOutlineCloudUpload,
  processing: HiOutlineCog,
  analysis: HiOutlineChip,
  report: HiOutlineDocumentReport,
};

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="section-padding relative overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={fadeUp}
        >
          <SectionHeading
            title="How It Works"
            subtitle="Four simple steps to verify the authenticity of any content. Our streamlined process delivers results in seconds."
          />
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="relative"
        >
          {/* Connecting Line - Desktop */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-[2px] -translate-y-1/2 z-0">
            <div className="w-full h-full bg-gradient-to-r from-primary-cyan/20 via-primary-purple/30 to-primary-cyan/20" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative z-10">
            {HOW_IT_WORKS_STEPS.map((step, index) => {
              const Icon = iconMap[step.icon];
              const colors = [
                { gradient: 'from-primary-cyan to-blue-500', glow: 'group-hover:shadow-[0_0_40px_rgba(6,182,212,0.25)]', text: 'text-primary-cyan', ring: 'ring-primary-cyan/30' },
                { gradient: 'from-primary-purple to-pink-500', glow: 'group-hover:shadow-[0_0_40px_rgba(168,85,247,0.25)]', text: 'text-primary-purple', ring: 'ring-primary-purple/30' },
                { gradient: 'from-amber-400 to-orange-500', glow: 'group-hover:shadow-[0_0_40px_rgba(251,191,36,0.25)]', text: 'text-amber-400', ring: 'ring-amber-400/30' },
                { gradient: 'from-emerald-400 to-green-500', glow: 'group-hover:shadow-[0_0_40px_rgba(52,211,153,0.25)]', text: 'text-emerald-400', ring: 'ring-emerald-400/30' },
              ];
              const color = colors[index];

              return (
                <motion.div
                  key={step.step}
                  variants={fadeUp}
                  className={`group glass rounded-2xl p-6 text-center relative transition-all duration-500 hover:bg-white/[0.08] ${color.glow}`}
                  whileHover={{ scale: 1.03, y: -8 }}
                >
                  {/* Step Number */}
                  <div className={`absolute -top-3 -right-3 w-8 h-8 rounded-full bg-gradient-to-br ${color.gradient} flex items-center justify-center text-white text-sm font-bold shadow-lg`}>
                    {step.step}
                  </div>

                  {/* Icon */}
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${color.gradient} bg-opacity-10 flex items-center justify-center mx-auto mb-5 ring-2 ${color.ring} transition-transform duration-300 group-hover:scale-110`}
                    style={{ background: `linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))` }}
                  >
                    <Icon className={`w-8 h-8 ${color.text}`} />
                  </div>

                  <h3 className="text-white text-lg font-semibold font-heading mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-400 text-sm leading-relaxed">
                    {step.description}
                  </p>

                  {/* Arrow indicator for mobile/tablet */}
                  {index < HOW_IT_WORKS_STEPS.length - 1 && (
                    <div className="lg:hidden flex justify-center mt-6">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-gray-600">
                        <path d="M12 5v14M5 12l7 7 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
