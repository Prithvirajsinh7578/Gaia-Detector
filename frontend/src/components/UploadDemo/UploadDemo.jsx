import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeUp } from '../../utils/animations';
import { UPLOAD_TABS } from '../../constants/constants';
import SectionHeading from '../SectionHeading/SectionHeading';
import Badge from '../Badge/Badge';
import {
  HiOutlineCloudUpload,
  HiOutlineDocumentText,
  HiOutlinePhotograph,
  HiOutlineVideoCamera,
  HiOutlineDocumentSearch,
  HiOutlineSparkles,
  HiOutlineCheckCircle,
  HiOutlineExclamationCircle,
  HiOutlineRefresh
} from 'react-icons/hi';
import {
  detectText,
  detectImage,
  detectVideo,
  detectDocument
} from '../../services/api';

const tabIcons = {
  text: HiOutlineDocumentText,
  image: HiOutlinePhotograph,
  video: HiOutlineVideoCamera,
  document: HiOutlineDocumentSearch,
};

export default function UploadDemo({ onDetectionComplete }) {
  const [activeTab, setActiveTab] = useState('text');
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [rawText, setRawText] = useState('');
  const [textMode, setTextMode] = useState('input'); // 'input' | 'file'
  const [detectionStatus, setDetectionStatus] = useState(null); // 'analyzing' | 'success' | 'error'
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);

  const currentTab = UPLOAD_TABS.find(t => t.id === activeTab);

  const resetState = () => {
    setUploadedFile(null);
    setDetectionStatus(null);
    setStatusMessage('');
    setErrorMessage('');
  };

  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    resetState();
  };

  const executeDetection = async (fileToAnalyze = null, textToAnalyze = null) => {
    setDetectionStatus('analyzing');
    setErrorMessage('');

    try {
      let result = null;

      if (activeTab === 'text') {
        if (textMode === 'input' || !fileToAnalyze) {
          const content = textToAnalyze !== null ? textToAnalyze : rawText;
          if (!content || content.trim().length < 10) {
            throw new Error('Please enter at least 10 characters of text to analyze.');
          }
          setStatusMessage('Extracting 18 linguistic features & running RoBERTa hybrid model...');
          result = await detectText(content.trim());
        } else {
          // File uploaded under text tab (.txt, .pdf, .docx)
          setStatusMessage('Extracting text and analyzing authenticity...');
          result = await detectDocument(fileToAnalyze);
        }
      } else if (activeTab === 'image') {
        if (!fileToAnalyze) throw new Error('Please select an image file to analyze.');
        setStatusMessage('Evaluating image visual authenticity with CLIP detector...');
        result = await detectImage(fileToAnalyze);
      } else if (activeTab === 'video') {
        if (!fileToAnalyze) throw new Error('Please select a video file to analyze.');
        setStatusMessage('Extracting video frames and running spatio-temporal analysis...');
        result = await detectVideo(fileToAnalyze);
      } else if (activeTab === 'document') {
        if (!fileToAnalyze) throw new Error('Please select a document file (.pdf, .docx, .txt).');
        setStatusMessage('Parsing document structure and running authenticity detection...');
        result = await detectDocument(fileToAnalyze);
      }

      setDetectionStatus('success');
      setStatusMessage(`Analysis complete: ${result.prediction || result.status} (${Math.round(result.confidence || 0)}% confidence)`);

      if (onDetectionComplete) {
        onDetectionComplete(result);
      }

      // Smooth scroll to preview section
      setTimeout(() => {
        const previewEl = document.getElementById('detection-preview');
        if (previewEl) {
          previewEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 400);

    } catch (err) {
      setDetectionStatus('error');
      setErrorMessage(err.message || 'Detection failed. Please verify the backend is running.');
    }
  };

  const handleFile = (file) => {
    if (!file) return;
    setUploadedFile(file);
    setDetectionStatus(null);
    setErrorMessage('');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleBrowse = () => {
    fileInputRef.current?.click();
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    handleFile(file);
  };

  return (
    <section id="upload-demo" className="section-padding relative">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={fadeUp}
        >
          <SectionHeading
            title="Try the Detection Engine"
            subtitle="Analyze text, images, videos, and documents to detect synthetic and AI-generated content in real-time."
          />
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={fadeUp}
        >
          {/* Tabs */}
          <div className="flex gap-2 mb-6 p-1.5 glass rounded-xl w-fit mx-auto">
            {UPLOAD_TABS.map((tab) => {
              const Icon = tabIcons[tab.id];
              return (
                <button
                  key={tab.id}
                  id={`tab-${tab.id}`}
                  onClick={() => handleTabChange(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 cursor-pointer
                    ${activeTab === tab.id
                      ? 'bg-gradient-to-r from-primary-cyan to-primary-purple text-white shadow-lg'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Mode switch for text tab */}
          {activeTab === 'text' && (
            <div className="flex justify-center gap-3 mb-4">
              <button
                type="button"
                onClick={() => { setTextMode('input'); resetState(); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  textMode === 'input' ? 'bg-primary-cyan/20 text-primary-cyan border border-primary-cyan/40' : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                Direct Text Input
              </button>
              <button
                type="button"
                onClick={() => { setTextMode('file'); resetState(); }}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  textMode === 'file' ? 'bg-primary-cyan/20 text-primary-cyan border border-primary-cyan/40' : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                Upload File (.txt, .pdf, .docx)
              </button>
            </div>
          )}

          {/* Direct Text Input Box */}
          {activeTab === 'text' && textMode === 'input' ? (
            <div className="glass rounded-2xl p-6 md:p-8 border border-white/10 text-left">
              <div className="flex items-center justify-between mb-3">
                <label htmlFor="text-input-field" className="text-white text-sm font-semibold flex items-center gap-2">
                  <HiOutlineDocumentText className="text-primary-cyan w-5 h-5" />
                  Paste or Enter Text to Analyze
                </label>
                <span className="text-gray-500 text-xs">
                  {rawText.trim().split(/\s+/).filter(Boolean).length} words | {rawText.length} chars
                </span>
              </div>
              <textarea
                id="text-input-field"
                rows={6}
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="Paste the text here (articles, essays, emails, social posts)... Gaia's hybrid detector analyzes 18 linguistic features alongside RoBERTa transformer metrics."
                className="w-full rounded-xl bg-white/5 border border-white/10 p-4 text-white text-sm focus:outline-none focus:border-primary-cyan/60 transition-colors resize-y placeholder-gray-500"
              />

              {/* Status / Error display */}
              {detectionStatus === 'analyzing' && (
                <div className="mt-4 p-3 rounded-xl bg-primary-cyan/10 border border-primary-cyan/20 flex items-center gap-3 text-primary-cyan text-sm">
                  <motion.div
                    className="w-4 h-4 border-2 border-primary-cyan/30 border-t-primary-cyan rounded-full shrink-0"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  />
                  <span>{statusMessage}</span>
                </div>
              )}

              {detectionStatus === 'success' && (
                <div className="mt-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-2 text-emerald-400 text-sm">
                  <HiOutlineCheckCircle className="w-5 h-5 shrink-0" />
                  <span>{statusMessage}</span>
                </div>
              )}

              {detectionStatus === 'error' && (
                <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-2 text-red-400 text-sm">
                  <HiOutlineExclamationCircle className="w-5 h-5 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              <div className="mt-5 flex flex-wrap gap-3 items-center justify-between">
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setRawText("Artificial intelligence has revolutionized numerous industries, offering unprecedented efficiencies in data processing and automated decision-making. However, ethical considerations remain paramount as these systems become more deeply integrated into daily operations.")}
                    className="text-xs text-primary-cyan hover:underline"
                  >
                    Load Sample AI Text
                  </button>
                  <span className="text-gray-600">|</span>
                  <button
                    type="button"
                    onClick={() => setRawText("I remember walking down the quiet cobblestone street that rainy Tuesday afternoon, clutching a warm cup of coffee and listening to the rhythm of drops against the canvas awning.")}
                    className="text-xs text-gray-400 hover:text-white hover:underline"
                  >
                    Load Sample Human Text
                  </button>
                </div>

                <button
                  id="btn-analyze-text"
                  type="button"
                  disabled={detectionStatus === 'analyzing'}
                  onClick={() => executeDetection(null, rawText)}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-primary-cyan to-primary-purple text-white font-medium hover:opacity-90 transition-all shadow-lg flex items-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  <HiOutlineSparkles className="w-5 h-5" />
                  {detectionStatus === 'analyzing' ? 'Analyzing...' : 'Analyze Authenticity'}
                </button>
              </div>
            </div>
          ) : (
            /* File Upload Area for Image, Video, Document, or File Text */
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab + (textMode || '')}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className={`
                  glass rounded-2xl p-8 md:p-12 text-center transition-all duration-300
                  ${isDragging ? 'border-primary-cyan border-2 bg-primary-cyan/5 glow-cyan-strong' : 'border border-white/10'}
                `}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={handleBrowse}
              >
                <input
                  ref={fileInputRef}
                  id="file-upload-input"
                  type="file"
                  accept={currentTab?.accept}
                  onChange={handleFileInput}
                  className="hidden"
                />

                {!uploadedFile ? (
                  <>
                    <motion.div
                      animate={{ y: isDragging ? -10 : 0 }}
                      className="mb-6"
                    >
                      <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-cyan/10 to-primary-purple/10 border border-white/10 flex items-center justify-center mx-auto">
                        <HiOutlineCloudUpload className={`w-10 h-10 transition-colors duration-300 ${isDragging ? 'text-primary-cyan' : 'text-gray-500'}`} />
                      </div>
                    </motion.div>

                    <h3 className="text-white text-lg font-semibold font-heading mb-2">
                      Drop your {activeTab} file here
                    </h3>
                    <p className="text-gray-500 mb-4">or</p>
                    <button
                      type="button"
                      id="btn-browse-file"
                      onClick={(e) => { e.stopPropagation(); handleBrowse(); }}
                      className="px-6 py-2.5 rounded-xl bg-white/10 text-white font-medium hover:bg-white/15 transition-all duration-300 cursor-pointer"
                    >
                      Browse Files
                    </button>

                    <div className="mt-6 flex flex-wrap gap-2 justify-center">
                      {currentTab?.formats.map((fmt) => (
                        <Badge key={fmt} variant="default" size="sm">.{fmt}</Badge>
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="py-4" onClick={(e) => e.stopPropagation()}>
                    <div className={`w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center ${
                      detectionStatus === 'success' ? 'bg-emerald-500/10' : detectionStatus === 'error' ? 'bg-red-500/10' : 'bg-primary-cyan/10'
                    }`}>
                      {detectionStatus === 'analyzing' ? (
                        <motion.div
                          className="w-8 h-8 border-2 border-primary-cyan/30 border-t-primary-cyan rounded-full"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        />
                      ) : detectionStatus === 'success' ? (
                        <HiOutlineCheckCircle className="w-8 h-8 text-emerald-400" />
                      ) : detectionStatus === 'error' ? (
                        <HiOutlineExclamationCircle className="w-8 h-8 text-red-400" />
                      ) : (
                        <HiOutlineCloudUpload className="w-8 h-8 text-primary-cyan" />
                      )}
                    </div>

                    <p className="text-white font-semibold mb-1">{uploadedFile.name}</p>
                    <p className="text-gray-500 text-sm mb-3">
                      {(uploadedFile.size / 1024).toFixed(1)} KB &bull; {uploadedFile.type || 'file'}
                    </p>

                    {detectionStatus === 'analyzing' && (
                      <p className="text-sm font-medium text-primary-cyan animate-pulse">
                        {statusMessage}
                      </p>
                    )}

                    {detectionStatus === 'success' && (
                      <p className="text-sm font-medium text-emerald-400">
                        {statusMessage}
                      </p>
                    )}

                    {detectionStatus === 'error' && (
                      <p className="text-sm font-medium text-red-400">
                        {errorMessage}
                      </p>
                    )}

                    <div className="mt-6 flex flex-wrap gap-3 justify-center">
                      <button
                        type="button"
                        id="btn-analyze-file"
                        disabled={detectionStatus === 'analyzing'}
                        onClick={() => executeDetection(uploadedFile)}
                        className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-primary-cyan to-primary-purple text-white font-medium hover:opacity-90 transition-all shadow-lg flex items-center gap-2 cursor-pointer disabled:opacity-50"
                      >
                        <HiOutlineSparkles className="w-5 h-5" />
                        {detectionStatus === 'analyzing' ? 'Analyzing...' : `Run ${activeTab.toUpperCase()} Detection`}
                      </button>

                      <button
                        type="button"
                        onClick={resetState}
                        className="px-4 py-2.5 rounded-xl bg-white/10 text-gray-300 text-sm hover:bg-white/15 transition-colors cursor-pointer flex items-center gap-2"
                      >
                        <HiOutlineRefresh className="w-4 h-4" />
                        Change File
                      </button>
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          )}
        </motion.div>
      </div>
    </section>
  );
}
