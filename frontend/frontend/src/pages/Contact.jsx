import { useState } from 'react';
import { motion } from 'framer-motion';
import { fadeUp, staggerContainer } from '../utils/animations';
import SectionHeading from '../components/SectionHeading/SectionHeading';
import Button from '../components/Button/Button';
import GlassCard from '../components/Card/Card';
import { HiOutlineMail, HiOutlineLocationMarker, HiOutlineClock } from 'react-icons/hi';

const contactInfo = [
  { icon: HiOutlineMail, title: 'Email', detail: 'support@gaiadetector.com', color: 'text-primary-cyan', bg: 'bg-primary-cyan/10' },
  { icon: HiOutlineLocationMarker, title: 'Location', detail: 'Remote â€” Worldwide', color: 'text-primary-purple', bg: 'bg-primary-purple/10' },
  { icon: HiOutlineClock, title: 'Response Time', detail: 'Within 24 hours', color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
];

export default function Contact() {
  const [formData, setFormData] = useState({ name: '', email: '', subject: '', message: '' });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Placeholder â€” no actual backend
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  };

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
              Get in <span className="gradient-text">Touch</span>
            </motion.h1>
            <motion.p variants={fadeUp} className="text-gray-400 text-lg md:text-xl leading-relaxed">
              Have a question, suggestion, or want to collaborate? We'd love to hear from you.
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Contact Cards */}
      <section className="section-padding pt-0">
        <div className="max-w-7xl mx-auto">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16"
          >
            {contactInfo.map((info) => {
              const Icon = info.icon;
              return (
                <motion.div key={info.title} variants={fadeUp}>
                  <GlassCard className="text-center">
                    <div className={`w-12 h-12 rounded-xl ${info.bg} flex items-center justify-center mx-auto mb-4`}>
                      <Icon className={`w-6 h-6 ${info.color}`} />
                    </div>
                    <h3 className="text-white font-semibold font-heading mb-1">{info.title}</h3>
                    <p className="text-gray-400 text-sm">{info.detail}</p>
                  </GlassCard>
                </motion.div>
              );
            })}
          </motion.div>

          {/* Contact Form */}
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={fadeUp}
            className="max-w-2xl mx-auto"
          >
            <div className="glass rounded-2xl p-6 md:p-8">
              <h2 className="text-2xl font-bold font-heading text-white mb-6">Send a Message</h2>
              
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label htmlFor="contact-name" className="block text-gray-400 text-sm mb-2">Name</label>
                    <input
                      id="contact-name"
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      placeholder="Your name"
                      required
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-600 focus:outline-none focus:border-primary-cyan/50 focus:ring-1 focus:ring-primary-cyan/20 transition-all duration-300"
                    />
                  </div>
                  <div>
                    <label htmlFor="contact-email" className="block text-gray-400 text-sm mb-2">Email</label>
                    <input
                      id="contact-email"
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="your@email.com"
                      required
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-600 focus:outline-none focus:border-primary-cyan/50 focus:ring-1 focus:ring-primary-cyan/20 transition-all duration-300"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="contact-subject" className="block text-gray-400 text-sm mb-2">Subject</label>
                  <input
                    id="contact-subject"
                    type="text"
                    name="subject"
                    value={formData.subject}
                    onChange={handleChange}
                    placeholder="What's this about?"
                    required
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-600 focus:outline-none focus:border-primary-cyan/50 focus:ring-1 focus:ring-primary-cyan/20 transition-all duration-300"
                  />
                </div>

                <div>
                  <label htmlFor="contact-message" className="block text-gray-400 text-sm mb-2">Message</label>
                  <textarea
                    id="contact-message"
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    placeholder="Write your message here..."
                    rows="5"
                    required
                    className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-600 focus:outline-none focus:border-primary-cyan/50 focus:ring-1 focus:ring-primary-cyan/20 transition-all duration-300 resize-none"
                  />
                </div>

                <div className="flex items-center gap-4">
                  <Button variant="primary" size="md" onClick={handleSubmit}>
                    {submitted ? 'Message Sent!' : 'Send Message'}
                    {!submitted && (
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                      </svg>
                    )}
                  </Button>
                  {submitted && (
                    <motion.span
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="text-emerald-400 text-sm"
                    >
                      âœ“ Thank you! We'll get back to you soon.
                    </motion.span>
                  )}
                </div>
              </form>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
