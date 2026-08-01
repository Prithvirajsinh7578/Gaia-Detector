import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeUp, staggerContainer } from '../../utils/animations';
import { FAQ_ITEMS } from '../../constants/constants';
import SectionHeading from '../SectionHeading/SectionHeading';
import { HiChevronDown } from 'react-icons/hi';

function AccordionItem({ question, answer, isOpen, onToggle }) {
  return (
    <div className="glass rounded-xl overflow-hidden transition-all duration-300 hover:bg-white/[0.06]">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-5 text-left cursor-pointer"
      >
        <span className="text-white font-semibold text-sm md:text-base pr-4">
          {question}
        </span>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3 }}
          className="flex-shrink-0"
        >
          <HiChevronDown className={`w-5 h-5 transition-colors duration-300 ${isOpen ? 'text-primary-cyan' : 'text-gray-500'}`} />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
          >
            <div className="px-5 pb-5 text-gray-400 text-sm leading-relaxed border-t border-white/5 pt-4">
              {answer}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <section className="section-padding relative">
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={fadeUp}
        >
          <SectionHeading
            title="Frequently Asked Questions"
            subtitle="Got questions? We've got answers. Here are the most common ones."
          />
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="space-y-3"
        >
          {FAQ_ITEMS.map((item, index) => (
            <motion.div key={item.question} variants={fadeUp}>
              <AccordionItem
                question={item.question}
                answer={item.answer}
                isOpen={openIndex === index}
                onToggle={() => setOpenIndex(openIndex === index ? -1 : index)}
              />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
