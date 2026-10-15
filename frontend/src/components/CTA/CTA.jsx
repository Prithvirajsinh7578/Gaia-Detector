import { motion } from 'framer-motion';
import { fadeUp } from '../../utils/animations';
import Button from '../Button/Button';

export default function CTA() {
  return (
    <section className="section-padding relative overflow-hidden">
      {/* Ambient glow background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-gradient-to-r from-primary-cyan/15 via-primary-purple/10 to-primary-cyan/15 rounded-full blur-[120px] animate-pulse-glow" />
      </div>

      <div className="max-w-4xl mx-auto relative z-10">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={fadeUp}
          className="glass rounded-3xl p-8 md:p-16 text-center relative overflow-hidden"
        >
          {/* Decorative border gradient */}
          <div className="absolute inset-0 rounded-3xl p-[1px] pointer-events-none">
            <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-primary-cyan/20 via-primary-purple/20 to-primary-cyan/20" style={{ mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)', maskComposite: 'exclude', WebkitMaskComposite: 'xor', padding: '1px' }} />
          </div>

          {/* Floating decorative elements */}
          <motion.div
            className="absolute top-4 right-8 w-16 h-16 rounded-full bg-primary-cyan/5 blur-xl"
            animate={{ y: [0, -15, 0], opacity: [0.3, 0.6, 0.3] }}
            transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
          />
          <motion.div
            className="absolute bottom-4 left-8 w-20 h-20 rounded-full bg-primary-purple/5 blur-xl"
            animate={{ y: [0, -10, 0], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
          />

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold font-heading mb-6">
              Ready to Verify{' '}
              <span className="gradient-text">Authenticity</span>?
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
              Start analyzing content today. Upload your files and get instant AI-powered authenticity reports with confidence scores and detailed insights.
            </p>

            <div className="flex flex-wrap gap-4 justify-center">
              <Button variant="primary" size="lg" to="/#upload-demo">
                Get Started Free
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </Button>
              <Button variant="outline" size="lg" to="/contact">
                Contact Us
              </Button>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
