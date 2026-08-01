import { motion } from 'framer-motion';
import { fadeUp } from '../../utils/animations';
import { DETECTION_RESULT } from '../../constants/constants';
import SectionHeading from '../SectionHeading/SectionHeading';

function CircularProgress({ value, size = 120, strokeWidth = 8 }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  const getColor = (val) => {
    if (val >= 80) return '#ef4444';
    if (val >= 60) return '#f59e0b';
    return '#22c55e';
  };

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none"
          stroke={getColor(value)}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          whileInView={{ strokeDashoffset: offset }}
          viewport={{ once: true }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white">{value}%</span>
        <span className="text-xs text-gray-500">Confidence</span>
      </div>
    </div>
  );
}

function ConfidenceBar({ value }) {
  const getColor = (val) => {
    if (val >= 80) return 'from-red-500 to-red-600';
    if (val >= 60) return 'from-amber-400 to-amber-500';
    return 'from-emerald-400 to-emerald-500';
  };

  return (
    <div className="w-full h-3 rounded-full bg-white/5 overflow-hidden">
      <motion.div
        className={`h-full rounded-full bg-gradient-to-r ${getColor(value)}`}
        initial={{ width: 0 }}
        whileInView={{ width: `${value}%` }}
        viewport={{ once: true }}
        transition={{ duration: 1.5, ease: 'easeOut', delay: 0.3 }}
      />
    </div>
  );
}

function RiskIndicator({ level }) {
  const colors = {
    High: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20', dot: 'bg-red-400' },
    Medium: { bg: 'bg-amber-400/10', text: 'text-amber-400', border: 'border-amber-400/20', dot: 'bg-amber-400' },
    Low: { bg: 'bg-emerald-400/10', text: 'text-emerald-400', border: 'border-emerald-400/20', dot: 'bg-emerald-400' },
  };
  const color = colors[level] || colors.Medium;

  return (
    <span className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full ${color.bg} ${color.border} border text-sm font-medium ${color.text}`}>
      <span className={`w-2 h-2 rounded-full ${color.dot} animate-pulse`} />
      {level} Risk
    </span>
  );
}

export default function DetectionPreview() {
  const { contentType, status, confidence, processingTime, riskLevel, summary } = DETECTION_RESULT;

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
            title="Detection Preview"
            subtitle="Here's what a typical analysis report looks like. All data shown is placeholder."
          />
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={fadeUp}
          className="glass rounded-2xl p-6 md:p-8"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Left - Circular Progress */}
            <div className="flex flex-col items-center justify-center">
              <CircularProgress value={confidence} />
              <div className="mt-4">
                <RiskIndicator level={riskLevel} />
              </div>
            </div>

            {/* Right - Details */}
            <div className="md:col-span-2 space-y-5">
              {/* Status Row */}
              <div className="grid grid-cols-2 gap-4">
                <div className="glass rounded-xl p-4">
                  <p className="text-gray-500 text-xs uppercase tracking-wider mb-1">Content Type</p>
                  <p className="text-white font-semibold">{contentType}</p>
                </div>
                <div className="glass rounded-xl p-4">
                  <p className="text-gray-500 text-xs uppercase tracking-wider mb-1">Status</p>
                  <p className="text-red-400 font-semibold">{status}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="glass rounded-xl p-4">
                  <p className="text-gray-500 text-xs uppercase tracking-wider mb-1">Confidence</p>
                  <p className="text-white font-semibold">{confidence}%</p>
                </div>
                <div className="glass rounded-xl p-4">
                  <p className="text-gray-500 text-xs uppercase tracking-wider mb-1">Processing Time</p>
                  <p className="text-white font-semibold">{processingTime}</p>
                </div>
              </div>

              {/* Confidence Bar */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400">AI Confidence Level</span>
                  <span className="text-white font-semibold">{confidence}%</span>
                </div>
                <ConfidenceBar value={confidence} />
              </div>

              {/* Summary */}
              <div className="glass rounded-xl p-4">
                <p className="text-gray-500 text-xs uppercase tracking-wider mb-2">Analysis Summary</p>
                <p className="text-gray-300 text-sm leading-relaxed">{summary}</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
