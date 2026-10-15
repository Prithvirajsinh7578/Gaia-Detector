import { motion } from 'framer-motion';
import { fadeUp, staggerContainer } from '../utils/animations';
import { HOW_IT_WORKS_STEPS } from '../constants/constants';
import SectionHeading from '../components/SectionHeading/SectionHeading';
import Button from '../components/Button/Button';
import CTA from '../components/CTA/CTA';
import { HiOutlineCloudUpload, HiOutlineCog, HiOutlineChip, HiOutlineDocumentReport } from 'react-icons/hi';

const iconMap = {
  upload: HiOutlineCloudUpload,
  processing: HiOutlineCog,
  analysis: HiOutlineChip,
  report: HiOutlineDocumentReport,
};

const stepDetails = [
  {
    details: 'Simply drag and drop your file into our secure upload area, or click to browse. We support 10+ file formats including text, images, videos, and documents. All uploads are encrypted end-to-end.',
    tech: ['AES-256 Encryption', 'Multi-format Parser', 'Secure Transport Layer'],
  },
  {
    details: 'Our preprocessing pipeline extracts relevant features from your content. For text, we analyze linguistic patterns; for images, frequency distributions; for videos, frame-by-frame features.',
    tech: ['Feature Extraction', 'Metadata Analysis', 'Format Normalization'],
  },
  {
    details: 'An ensemble of state-of-the-art AI models analyzes the extracted features. Multiple detection strategies are combined using weighted voting to maximize accuracy and minimize false positives.',
    tech: ['Ensemble Learning', 'Weighted Voting', 'Cross-Validation'],
  },
  {
    details: 'Receive a comprehensive report with confidence scores, risk indicators, and detailed explanations. Each finding is annotated with evidence to help you understand the analysis.',
    tech: ['Confidence Scoring', 'Risk Assessment', 'Annotated Evidence'],
  },
];

export default function HowItWorksPage() {
  return (
    <div className="pt-24">
      {/* Hero */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
            className="text-center max-w-3xl mx-auto"
          >
            <motion.h1 variants={fadeUp} className="text-4xl md:text-5xl lg:text-6xl font-bold font-heading mb-6">
              How It <span className="gradient-text">Works</span>
            </motion.h1>
            <motion.p variants={fadeUp} className="text-gray-400 text-lg md:text-xl leading-relaxed">
              Our streamlined four-step process takes your content from upload to detailed authenticity report in seconds.
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Detailed Steps */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto space-y-12">
          {HOW_IT_WORKS_STEPS.map((step, index) => {
            const Icon = iconMap[step.icon];
            const detail = stepDetails[index];
            const colors = [
              { text: 'text-primary-cyan', bg: 'bg-primary-cyan/10', gradient: 'from-primary-cyan to-blue-500', ring: 'ring-primary-cyan/30', dot: 'bg-primary-cyan' },
              { text: 'text-primary-purple', bg: 'bg-primary-purple/10', gradient: 'from-primary-purple to-pink-500', ring: 'ring-primary-purple/30', dot: 'bg-primary-purple' },
              { text: 'text-amber-400', bg: 'bg-amber-400/10', gradient: 'from-amber-400 to-orange-500', ring: 'ring-amber-400/30', dot: 'bg-amber-400' },
              { text: 'text-emerald-400', bg: 'bg-emerald-400/10', gradient: 'from-emerald-400 to-green-500', ring: 'ring-emerald-400/30', dot: 'bg-emerald-400' },
            ];
            const color = colors[index];

            return (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, x: index % 2 === 0 ? -40 : 40 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, amount: 0.3 }}
                transition={{ duration: 0.6 }}
              >
                <div className="glass rounded-2xl p-6 md:p-8 relative overflow-hidden">
                  {/* Step number accent */}
                  <div className={`absolute top-0 left-0 w-16 h-16 bg-gradient-to-br ${color.gradient} opacity-10 rounded-br-full`} />
                  
                  <div className="flex flex-col md:flex-row gap-6 items-start">
                    {/* Step number & icon */}
                    <div className="flex items-center gap-4 md:flex-col md:items-center md:min-w-[80px]">
                      <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${color.gradient} flex items-center justify-center text-white font-bold text-lg shadow-lg`}>
                        {step.step}
                      </div>
                      <div className={`w-14 h-14 rounded-xl ${color.bg} ring-2 ${color.ring} flex items-center justify-center`}>
                        <Icon className={`w-7 h-7 ${color.text}`} />
                      </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1">
                      <h3 className="text-white text-xl font-bold font-heading mb-3">{step.title}</h3>
                      <p className="text-gray-400 text-sm leading-relaxed mb-4">
                        {step.description}
                      </p>
                      <p className="text-gray-500 text-sm leading-relaxed mb-4">
                        {detail.details}
                      </p>

                      {/* Tech badges */}
                      <div className="flex flex-wrap gap-2">
                        {detail.tech.map((tech) => (
                          <span
                            key={tech}
                            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${color.bg} ${color.text} border border-current/10`}
                          >
                            <span className={`w-1.5 h-1.5 rounded-full ${color.dot}`} />
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Connecting line to next step */}
                  {index < HOW_IT_WORKS_STEPS.length - 1 && (
                    <div className="hidden md:flex justify-center mt-4 -mb-8 relative z-10">
                      <div className="w-px h-12 bg-gradient-to-b from-white/10 to-transparent" />
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* CTA */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={fadeUp}
          >
            <h2 className="text-3xl md:text-4xl font-bold font-heading mb-6">
              Ready to <span className="gradient-text">Get Started</span>?
            </h2>
            <p className="text-gray-400 text-lg mb-8 max-w-xl mx-auto">
              Try our demo now â€” no account required. Upload a file and see the results in seconds.
            </p>
            <Button variant="primary" size="lg" to="/#upload-demo">
              Try the Demo
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7"/>
              </svg>
            </Button>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
