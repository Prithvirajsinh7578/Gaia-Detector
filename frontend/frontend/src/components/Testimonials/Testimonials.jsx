import { motion } from 'framer-motion';
import { fadeUp, staggerContainer } from '../../utils/animations';
import { TESTIMONIALS } from '../../constants/constants';
import SectionHeading from '../SectionHeading/SectionHeading';
import { HiStar, HiOutlineStar } from 'react-icons/hi';

function StarRating({ rating }) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        star <= rating
          ? <HiStar key={star} className="w-5 h-5 text-amber-400" />
          : <HiOutlineStar key={star} className="w-5 h-5 text-gray-600" />
      ))}
    </div>
  );
}

function AvatarPlaceholder({ name }) {
  const initials = name.split(' ').map(n => n[0]).join('').slice(0, 2);
  const colors = [
    'from-primary-cyan to-blue-500',
    'from-primary-purple to-pink-500',
    'from-emerald-400 to-green-500',
  ];
  const colorIndex = name.charCodeAt(0) % colors.length;
  
  return (
    <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${colors[colorIndex]} flex items-center justify-center text-white font-bold text-sm shadow-lg`}>
      {initials}
    </div>
  );
}

export default function Testimonials() {
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
            title="What People Say"
            subtitle="Trusted by researchers, educators, and professionals worldwide."
          />
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {TESTIMONIALS.map((testimonial, index) => (
            <motion.div
              key={testimonial.name}
              variants={fadeUp}
              className="glass rounded-2xl p-6 transition-all duration-500 hover:bg-white/[0.08] group"
              whileHover={{ scale: 1.03, y: -5 }}
            >
              {/* Quote icon */}
              <div className="mb-4">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" className="text-primary-cyan/30">
                  <path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" fill="currentColor"/>
                  <path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z" fill="currentColor"/>
                </svg>
              </div>

              {/* Review */}
              <p className="text-gray-300 text-sm leading-relaxed mb-6">
                "{testimonial.review}"
              </p>

              {/* Rating */}
              <div className="mb-4">
                <StarRating rating={testimonial.rating} />
              </div>

              {/* Author */}
              <div className="flex items-center gap-3 pt-4 border-t border-white/10">
                <AvatarPlaceholder name={testimonial.name} />
                <div>
                  <p className="text-white font-semibold text-sm">{testimonial.name}</p>
                  <p className="text-gray-500 text-xs">{testimonial.role}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
