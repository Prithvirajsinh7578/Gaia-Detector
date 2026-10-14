import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HiOutlineCloudUpload, HiOutlineSparkles, HiOutlineExclamationCircle } from 'react-icons/hi';
import { tabIcons } from '../../components/UploadDemo/UploadDemo';
import { UPLOAD_TABS } from '../../constants/constants';
import Badge from '../../components/Badge/Badge';
import api from '../../services/api';

export default function Upload() {
  const [activeTab, setActiveTab] = useState('image');
  const [file, setFile] = useState(null);
  const [textInput, setTextInput] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);
  const currentTab = UPLOAD_TABS.find((t) => t.id === activeTab);

  const handleSelectFile = (selected) => {
    if (!selected) return;
    setFile(selected);
    setResult(null);
    setError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = async () => {
    setError(null);
    setResult(null);
    setAnalyzing(true);

    try {
      let res;
      if (activeTab === 'image') {
        if (!file) throw new Error('Please select an image file to analyze.');
        res = await api.detectImage(file);
      } else if (activeTab === 'text') {
        if (!textInput.trim()) throw new Error('Please enter text to analyze.');
        res = await api.detectText(textInput);
      } else if (activeTab === 'document') {
        if (!file) throw new Error('Please select a document (.pdf or .txt) to analyze.');
        res = await api.detectDocument(file);
      } else if (activeTab === 'video') {
        if (!file) throw new Error('Please select a video file to analyze.');
        res = await api.detectVideo(file);
      }
      setResult(res);
    } catch (err) {
      setError(err.message || 'Detection failed. Please check your file or network.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 md:px-8 max-w-5xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl md:text-5xl font-bold font-heading text-white mb-3">
          AI Authenticity <span className="gradient-text">Detector</span>
        </h1>
        <p className="text-gray-400 max-w-xl mx-auto text-sm md:text-base">
          Analyze text, images, documents, and videos using our backend detection pipelines.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 p-1.5 glass rounded-xl w-fit mx-auto">
        {UPLOAD_TABS.map((tab) => {
          const Icon = tabIcons[tab.id];
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id);
                setFile(null);
                setResult(null);
                setError(null);
              }}
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

      {/* Upload or Text Area */}
      <div className="glass rounded-2xl p-6 md:p-10 border border-white/10 relative">
        {activeTab === 'text' ? (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Enter or paste text to analyze
            </label>
            <textarea
              rows={8}
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste article, essay, or generated response here..."
              className="w-full p-4 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-primary-cyan transition-colors"
            />
          </div>
        ) : (
          <div
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onClick={() => fileInputRef.current?.click()}
            className={`
              border-2 border-dashed rounded-2xl p-8 md:p-12 text-center cursor-pointer transition-all duration-300
              ${isDragging ? 'border-primary-cyan bg-primary-cyan/5' : 'border-white/15 hover:border-white/30 bg-white/5'}
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={currentTab?.accept}
              onChange={(e) => handleSelectFile(e.target.files[0])}
              className="hidden"
            />
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-cyan/10 to-primary-purple/10 border border-white/10 flex items-center justify-center mx-auto mb-4">
              <HiOutlineCloudUpload className="w-8 h-8 text-primary-cyan" />
            </div>
            {file ? (
              <div>
                <p className="text-white font-semibold text-lg">{file.name}</p>
                <p className="text-gray-400 text-sm mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="mt-3 text-xs text-red-400 hover:underline"
                >
                  Remove & change file
                </button>
              </div>
            ) : (
              <div>
                <p className="text-white font-medium mb-1">Click to browse or drag & drop {activeTab} file</p>
                <p className="text-gray-500 text-xs mb-3">Supported formats: {currentTab?.formats.join(', ')}</p>
                <div className="flex gap-1.5 justify-center flex-wrap">
                  {currentTab?.formats.map((fmt) => (
                    <Badge key={fmt} variant="default" size="sm">.{fmt}</Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3">
            <HiOutlineExclamationCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleAnalyze}
            disabled={analyzing || (activeTab === 'text' ? !textInput.trim() : !file)}
            className="px-6 py-3 rounded-xl font-medium text-white bg-gradient-to-r from-primary-cyan to-primary-purple hover:opacity-90 transition-opacity disabled:opacity-40 cursor-pointer flex items-center gap-2 shadow-lg shadow-primary-cyan/20"
          >
            {analyzing ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Analyzing with AI...
              </>
            ) : (
              <>
                <HiOutlineSparkles className="w-5 h-5" />
                Run Authenticity Check
              </>
            )}
          </button>
        </div>
      </div>

      {/* Detection Result Card */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="mt-8 glass rounded-2xl p-6 md:p-8 border border-white/10 shadow-2xl"
          >
            <div className="flex items-center justify-between pb-6 border-b border-white/10 flex-wrap gap-4">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Analysis Result</span>
                <h3 className="text-2xl font-bold font-heading text-white mt-1 flex items-center gap-2">
                  {result.status}
                  {result.verified ? (
                    <Badge variant="cyan" size="sm">Verified Model</Badge>
                  ) : (
                    <Badge variant="purple" size="sm">Unmounted Pipeline</Badge>
                  )}
                </h3>
              </div>
              <div className="text-right">
                <span className="text-xs text-gray-400">Model Confidence / Score</span>
                <p className="text-2xl font-extrabold gradient-text">
                  {result.verified ? `${result.confidence}%` : 'N/A'}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 my-6">
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-xs text-gray-400 block">Content Type</span>
                <span className="text-white font-medium capitalize">{result.content_type}</span>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-xs text-gray-400 block">Prediction</span>
                <span className="text-white font-medium">{result.prediction}</span>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-xs text-gray-400 block">Risk Level</span>
                <span className={`font-medium ${result.risk_level === 'High' ? 'text-red-400' : result.risk_level === 'Low' ? 'text-emerald-400' : 'text-gray-300'}`}>
                  {result.risk_level}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                <span className="text-xs text-gray-400 block">Processing Time</span>
                <span className="text-white font-medium">{result.processing_time_sec}s</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-white/5 border border-white/10 text-sm text-gray-300 leading-relaxed mb-4">
              <p className="font-semibold text-white mb-1">Diagnostic Summary:</p>
              <p>{result.summary}</p>
            </div>

            <div className="text-xs text-gray-500 flex items-center justify-between flex-wrap gap-2">
              <span>Detector Pipeline: <code className="text-gray-400">{result.detector_name}</code></span>
              <span>Backend Status: {result.verified ? 'Active Real Inference' : 'Honest Unverified Stub'}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
