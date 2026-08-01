import { motion } from 'framer-motion';
import { fadeUp, staggerContainerFast } from '../../utils/animations';
import { SUPPORTED_FORMATS } from '../../constants/constants';
import SectionHeading from '../SectionHeading/SectionHeading';

const formatColors = {
  TXT: 'from-primary-cyan/20 to-blue-500/20 text-primary-cyan border-primary-cyan/20',
  PDF: 'from-red-500/20 to-rose-500/20 text-red-400 border-red-400/20',
  DOCX: 'from-blue-500/20 to-indigo-500/20 text-blue-400 border-blue-400/20',
  PNG: 'from-emerald-400/20 to-green-500/20 text-emerald-400 border-emerald-400/20',
  JPG: 'from-amber-400/20 to-yellow-500/20 text-amber-400 border-amber-400/20',
  JPEG: 'from-orange-400/20 to-amber-500/20 text-orange-400 border-orange-400/20',
  MP4: 'from-primary-purple/20 to-pink-500/20 text-primary-purple border-primary-purple/20',
  MOV: 'from-pink-400/20 to-rose-400/20 text-pink-400 border-pink-400/20',
  AVI: 'from-violet-400/20 to-purple-400/20 text-violet-400 border-violet-400/20',
  WEBP: 'from-teal-400/20 to-cyan-400/20 text-teal-400 border-teal-400/20',
};

const formatCategories = {
  TXT: 'Text', PDF: 'Document', DOCX: 'Document',
  PNG: 'Image', JPG: 'Image', JPEG: 'Image', WEBP: 'Image',
  MP4: 'Video', MOV: 'Video', AVI: 'Video',
};

export default function SupportedFormats() {
  return (
    <section className="section-padding relative">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={fadeUp}
        >
          <SectionHeading
            title="Supported Formats"
            subtitle="We support a wide range of file formats across text, image, video, and document categories."
          />
        </motion.div>

        <motion.div
          variants={staggerContainerFast}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          className="flex flex-wrap gap-3 justify-center"
        >
          {SUPPORTED_FORMATS.map((format) => {
            const colorClass = formatColors[format] || 'from-gray-400/20 to-gray-500/20 text-gray-400 border-gray-400/20';
            const category = formatCategories[format] || 'Other';
            return (
              <motion.div
                key={format}
                variants={fadeUp}
                whileHover={{ scale: 1.1, y: -4 }}
                className={`
                  group relative px-5 py-3 rounded-xl border cursor-default
                  bg-gradient-to-br ${colorClass}
                  transition-all duration-300
                  hover:shadow-lg
                `}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold font-heading">.{format}</span>
                </div>
                <span className="text-xs opacity-60 font-medium">{category}</span>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
