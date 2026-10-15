import { motion } from 'framer-motion';
import { fadeUp, fadeLeft, fadeRight, staggerContainer } from '../utils/animations';
import SectionHeading from '../components/SectionHeading/SectionHeading';
import GlassCard from '../components/Card/Card';
import { HiOutlineShieldCheck, HiOutlineEye, HiOutlineGlobe, HiOutlineUserGroup } from 'react-icons/hi';

const values = [
  {
    icon: HiOutlineShieldCheck,
    title: 'Trust & Transparency',
    description: 'We believe in building tools that foster trust in digital content. Our detection methods are transparent and scientifically validated.',
    color: 'text-primary-cyan',
    bg: 'bg-primary-cyan/10',
  },
  {
    icon: HiOutlineEye,
    title: 'Accuracy First',
    description: 'We prioritize minimizing false positives and negatives. Every detection model undergoes rigorous testing before deployment.',
    color: 'text-primary-purple',
    bg: 'bg-primary-purple/10',
  },
  {
    icon: HiOutlineGlobe,
    title: 'Accessible to All',
    description: 'From students to enterprises, our platform is designed to be accessible and easy to use for everyone.',
    color: 'text-emerald-400',
    bg: 'bg-emerald-400/10',
  },
  {
    icon: HiOutlineUserGroup,
    title: 'Community Driven',
    description: 'We actively engage with researchers, educators, and institutions to improve our detection capabilities.',
    color: 'text-amber-400',
    bg: 'bg-amber-400/10',
  },
];

const teamMembers = [
  { name: 'Vikram Singh', role: 'Lead Developer', initials: 'VS', color: 'from-primary-cyan to-blue-500' },
  { name: 'Ananya Patel', role: 'AI Researcher', initials: 'AP', color: 'from-primary-purple to-pink-500' },
  { name: 'Rohan Kumar', role: 'Backend Engineer', initials: 'RK', color: 'from-emerald-400 to-green-500' },
  { name: 'Sneha Gupta', role: 'UI/UX Designer', initials: 'SG', color: 'from-amber-400 to-orange-500' },
];

export default function About() {
  return (
    <div className="pt-24">
      {/* Hero Section */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
          >
            <motion.div variants={fadeUp} className="text-center max-w-3xl mx-auto">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold font-heading mb-6">
                About <span className="gradient-text">Gaia Detector</span>
              </h1>
              <p className="text-gray-400 text-lg md:text-xl leading-relaxed">
                We're on a mission to preserve trust in the digital age. As AI-generated content becomes
                increasingly sophisticated, Gaia Detector provides the tools to verify authenticity with confidence.
              </p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Mission */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.3 }}
              variants={fadeLeft}
            >
              <h2 className="text-3xl md:text-4xl font-bold font-heading mb-6">
                Our <span className="gradient-text">Mission</span>
              </h2>
              <p className="text-gray-400 leading-relaxed mb-4">
                In an era where AI can generate text indistinguishable from human writing, images that appear
                photorealistic, and videos that simulate reality, verifying content authenticity has never been
                more important.
              </p>
              <p className="text-gray-400 leading-relaxed mb-4">
                Gaia Detector was born from the need to provide a reliable, accessible, and fast solution for
                detecting AI-generated content across multiple modalities â€” text, images, videos, and documents.
              </p>
              <p className="text-gray-400 leading-relaxed">
                Our platform combines cutting-edge deep learning models with an intuitive user interface,
                making AI content detection accessible to everyone â€” from individual researchers to large institutions.
              </p>
            </motion.div>

            <motion.div
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, amount: 0.3 }}
              variants={fadeRight}
              className="relative"
            >
              <div className="glass rounded-2xl p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-primary-cyan/10 to-transparent rounded-bl-full" />
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-primary-purple/10 to-transparent rounded-tr-full" />
                
                <div className="relative z-10 space-y-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary-cyan/10 flex items-center justify-center">
                      <span className="text-2xl">ðŸŽ¯</span>
                    </div>
                    <div>
                      <p className="text-white font-semibold">95%+ Accuracy</p>
                      <p className="text-gray-500 text-sm">Detection accuracy across all formats</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary-purple/10 flex items-center justify-center">
                      <span className="text-2xl">âš¡</span>
                    </div>
                    <div>
                      <p className="text-white font-semibold">&lt;5 Seconds</p>
                      <p className="text-gray-500 text-sm">Average analysis time per file</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-emerald-400/10 flex items-center justify-center">
                      <span className="text-2xl">ðŸ”’</span>
                    </div>
                    <div>
                      <p className="text-white font-semibold">Zero Data Retention</p>
                      <p className="text-gray-500 text-sm">Files deleted after analysis</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={fadeUp}
          >
            <SectionHeading
              title="Our Core Values"
              subtitle="The principles that guide everything we build."
            />
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {values.map((value) => {
              const Icon = value.icon;
              return (
                <motion.div key={value.title} variants={fadeUp}>
                  <GlassCard className="flex gap-5">
                    <div className={`w-12 h-12 rounded-xl ${value.bg} flex items-center justify-center flex-shrink-0`}>
                      <Icon className={`w-6 h-6 ${value.color}`} />
                    </div>
                    <div>
                      <h3 className="text-white text-lg font-semibold font-heading mb-2">{value.title}</h3>
                      <p className="text-gray-400 text-sm leading-relaxed">{value.description}</p>
                    </div>
                  </GlassCard>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* Team */}
      <section className="section-padding">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={fadeUp}
          >
            <SectionHeading
              title="Meet the Team"
              subtitle="The people behind Gaia Detector, working to make content verification accessible."
            />
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6"
          >
            {teamMembers.map((member) => (
              <motion.div key={member.name} variants={fadeUp}>
                <GlassCard className="text-center">
                  <div className={`w-16 h-16 rounded-full bg-gradient-to-br ${member.color} flex items-center justify-center mx-auto mb-4 text-white font-bold text-lg shadow-lg`}>
                    {member.initials}
                  </div>
                  <h3 className="text-white font-semibold font-heading mb-1">{member.name}</h3>
                  <p className="text-gray-500 text-sm">{member.role}</p>
                </GlassCard>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>
    </div>
  );
}
