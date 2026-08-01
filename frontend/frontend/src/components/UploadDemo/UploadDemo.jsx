import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeUp } from '../../utils/animations';
import { UPLOAD_TABS } from '../../constants/constants';
import SectionHeading from '../SectionHeading/SectionHeading';
import Badge from '../Badge/Badge';
import { HiOutlineCloudUpload, HiOutlineDocumentText, HiOutlinePhotograph, HiOutlineVideoCamera, HiOutlineDocumentSearch } from 'react-icons/hi';

const tabIcons = {
  text: HiOutlineDocumentText,
  image: HiOutlinePhotograph,
  video: HiOutlineVideoCamera,
  document: HiOutlineDocumentSearch,
};

export default function UploadDemo() {
  const [activeTab, setActiveTab] = useState('text');
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null); // 'uploading' | 'success' | 'error'
  const fileInputRef = useRef(null);

  const currentTab = UPLOAD_TABS.find(t => t.id === activeTab);

  const handleFile = async (file) => {
    if (!file) return;
    setUploadedFile(file);
    setUploadStatus('uploading');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', activeTab);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setUploadStatus('success');
      } else {
        setUploadStatus('error');
      }
    } catch {
      setUploadStatus('error');
    }
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
            title="Try the Upload Demo"
            subtitle="Upload your content and see our detection engine in action. Drag and drop or browse to select a file."
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
                  onClick={() => { setActiveTab(tab.id); setUploadedFile(null); setUploadStatus(null); }}
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

          {/* Upload Area */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={`
                glass rounded-2xl p-8 md:p-12 text-center cursor-pointer transition-all duration-300
                ${isDragging ? 'border-primary-cyan border-2 bg-primary-cyan/5 glow-cyan-strong' : 'border border-white/10'}
              `}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={handleBrowse}
            >
              <input
                ref={fileInputRef}
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
                <div className="py-4">
                  <div className={`w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center ${
                    uploadStatus === 'success' ? 'bg-emerald-500/10' : uploadStatus === 'error' ? 'bg-red-500/10' : 'bg-primary-cyan/10'
                  }`}>
                    {uploadStatus === 'uploading' && (
                      <motion.div
                        className="w-8 h-8 border-2 border-primary-cyan/30 border-t-primary-cyan rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      />
                    )}
                    {uploadStatus === 'success' && (
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" className="text-emerald-400">
                        <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5"/>
                      </svg>
                    )}
                    {uploadStatus === 'error' && (
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" className="text-red-400">
                        <path d="M15 9l-6 6M9 9l6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5"/>
                      </svg>
                    )}
                  </div>
                  <p className="text-white font-semibold mb-1">{uploadedFile.name}</p>
                  <p className="text-gray-500 text-sm mb-3">
                    {(uploadedFile.size / 1024).toFixed(1)} KB
                  </p>
                  <p className={`text-sm font-medium ${
                    uploadStatus === 'success' ? 'text-emerald-400' : uploadStatus === 'error' ? 'text-red-400' : 'text-primary-cyan'
                  }`}>
                    {uploadStatus === 'uploading' && 'Uploading...'}
                    {uploadStatus === 'success' && 'File uploaded successfully! Saved to tempdect folder.'}
                    {uploadStatus === 'error' && 'Upload failed. Make sure the upload server is running.'}
                  </p>
                  <button
                    onClick={(e) => { e.stopPropagation(); setUploadedFile(null); setUploadStatus(null); }}
                    className="mt-4 px-4 py-2 rounded-lg bg-white/10 text-gray-300 text-sm hover:bg-white/15 transition-colors cursor-pointer"
                  >
                    Upload Another
                  </button>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </motion.div>
      </div>
    </section>
  );
}
