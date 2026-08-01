import Hero from '../../components/Hero/Hero';
import Stats from '../../components/Stats/Stats';
import Features from '../../components/Features/Features';
import UploadDemo from '../../components/UploadDemo/UploadDemo';
import DetectionPreview from '../../components/DetectionPreview/DetectionPreview';
import HowItWorks from '../../components/HowItWorks/HowItWorks';
import WhyChooseUs from '../../components/WhyChooseUs/WhyChooseUs';
import SupportedFormats from '../../components/SupportedFormats/SupportedFormats';
import Testimonials from '../../components/Testimonials/Testimonials';
import FAQ from '../../components/FAQ/FAQ';
import CTA from '../../components/CTA/CTA';

export default function Home() {
  return (
    <>
      <Hero />
      <Stats />
      <Features />
      <UploadDemo />
      <DetectionPreview />
      <HowItWorks />
      <WhyChooseUs />
      <SupportedFormats />
      <Testimonials />
      <FAQ />
      <CTA />
    </>
  );
}
