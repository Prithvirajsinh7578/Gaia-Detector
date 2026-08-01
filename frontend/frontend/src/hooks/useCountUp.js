import { useState, useEffect, useRef } from 'react';

/**
 * Custom hook that counts up a number when element is visible in viewport.
 * @param {number} end - The target number
 * @param {number} duration - Animation duration in ms
 * @param {string} prefix - Optional prefix (e.g., '<')
 * @param {string} suffix - Optional suffix (e.g., '%', '+')
 * @returns {{ count: string, ref: React.RefObject }}
 */
export function useCountUp(end, duration = 2000, prefix = '', suffix = '') {
  const [count, setCount] = useState(0);
  const [hasStarted, setHasStarted] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasStarted) {
          setHasStarted(true);
        }
      },
      { threshold: 0.3 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [hasStarted]);

  useEffect(() => {
    if (!hasStarted) return;

    let startTime = null;
    const startValue = 0;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      const current = Math.floor(startValue + (end - startValue) * eased);
      setCount(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [hasStarted, end, duration]);

  const formatCount = () => {
    if (end >= 1000) {
      const k = count >= 1000 ? `${Math.floor(count / 1000)}K` : count.toString();
      return `${prefix}${k}${suffix}`;
    }
    return `${prefix}${count}${suffix}`;
  };

  return { count: formatCount(), ref };
}

export default useCountUp;
