import { useState } from 'react';
import UploadDemo from '../../components/UploadDemo/UploadDemo';
import DetectionPreview from '../../components/DetectionPreview/DetectionPreview';

export default function Upload() {
  const [detectionResult, setDetectionResult] = useState(null);

  return (
    <div className="min-h-screen pt-28 pb-16 px-4 md:px-8 max-w-7xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-3 tracking-tight font-heading">
          Content <span className="bg-gradient-to-r from-primary-cyan to-primary-purple bg-clip-text text-transparent">Authenticity Workbench</span>
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto text-base">
          Analyze and verify the origin of text, images, videos, and multi-page documents using Gaia's hybrid multi-modal AI detection engine.
        </p>
      </div>

      <UploadDemo onDetectionComplete={(result) => setDetectionResult(result)} />
      <DetectionPreview result={detectionResult} />
    </div>
  );
}
