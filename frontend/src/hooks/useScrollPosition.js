import { useState, useEffect } from 'react';

/**
 * Custom hook to track scroll position for navbar effects.
 * @returns {{ scrollY: number, isScrolled: boolean }}
 */
export function useScrollPosition() {
  const [scrollY, setScrollY] = useState(0);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const currentY = window.scrollY;
      setScrollY(currentY);
      setIsScrolled(currentY > 50);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return { scrollY, isScrolled };
}

export default useScrollPosition;
