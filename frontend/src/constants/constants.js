// Placeholder data constants for the entire application

export const NAV_LINKS = [
  { name: 'Home', path: '/' },
  { name: 'Features', path: '/features' },
  { name: 'How It Works', path: '/how-it-works' },
  { name: 'About', path: '/about' },
  { name: 'Contact', path: '/contact' },
];

export const HERO_BADGES = [
  { label: 'AI Powered', icon: '⚡' },
  { label: 'Secure Upload', icon: '🔒' },
  { label: 'Fast Analysis', icon: '🚀' },
  { label: 'Multi Format Support', icon: '📄' },
];

export const STATS = [
  { label: 'Files Analyzed', value: 100000, suffix: '+', displayValue: '100K+' },
  { label: 'Accuracy', value: 95, suffix: '%', displayValue: '95%' },
  { label: 'Supported Formats', value: 10, suffix: '+', displayValue: '10+' },
  { label: 'Response Time', value: 5, prefix: '<', suffix: ' sec', displayValue: '<5 sec' },
];

export const FEATURES = [
  {
    title: 'AI Text Detection',
    description: 'Analyze written content and estimate AI-generated probability with advanced NLP models.',
    icon: 'text',
  },
  {
    title: 'Image Detection',
    description: 'Detect AI-generated images using advanced forensic analysis and deep learning.',
    icon: 'image',
  },
  {
    title: 'Video Analysis',
    description: 'Analyze video frames to identify synthetic or manipulated content in real-time.',
    icon: 'video',
  },
  {
    title: 'Document Scanner',
    description: 'Extract text and images from PDF and DOCX files for comprehensive authenticity analysis.',
    icon: 'document',
  },
];

export const UPLOAD_TABS = [
  { id: 'text', label: 'Text', formats: ['TXT', 'PDF', 'DOCX'], accept: '.txt,.pdf,.docx' },
  { id: 'image', label: 'Image', formats: ['PNG', 'JPG', 'JPEG', 'WEBP'], accept: '.png,.jpg,.jpeg,.webp' },
  { id: 'video', label: 'Video', formats: ['MP4', 'MOV', 'AVI'], accept: '.mp4,.mov,.avi' },
  { id: 'document', label: 'Document', formats: ['PDF', 'DOCX', 'TXT'], accept: '.pdf,.docx,.txt' },
];

export const DETECTION_RESULT = {
  contentType: 'Image',
  status: 'Likely AI Generated',
  confidence: 92,
  processingTime: '2.4 sec',
  riskLevel: 'High',
  summary: 'The analyzed image shows strong indicators of AI generation, including consistent noise patterns, unusual frequency distributions, and metadata inconsistencies typical of generative models.',
};

export const HOW_IT_WORKS_STEPS = [
  {
    step: 1,
    title: 'Upload',
    description: 'Upload your file through our secure drag-and-drop interface. We support 10+ file formats.',
    icon: 'upload',
  },
  {
    step: 2,
    title: 'Processing',
    description: 'Our system preprocesses your file, extracting relevant features and metadata for analysis.',
    icon: 'processing',
  },
  {
    step: 3,
    title: 'AI Analysis',
    description: 'Advanced AI models analyze content patterns, artifacts, and signatures to determine authenticity.',
    icon: 'analysis',
  },
  {
    step: 4,
    title: 'Detailed Report',
    description: 'Receive a comprehensive report with confidence scores, risk indicators, and detailed findings.',
    icon: 'report',
  },
];

export const WHY_CHOOSE_US = [
  { title: 'Secure', description: 'End-to-end encryption with zero data retention policy.', icon: 'secure' },
  { title: 'Fast', description: 'Results in under 5 seconds with optimized AI pipelines.', icon: 'fast' },
  { title: 'Accurate', description: '95%+ accuracy powered by state-of-the-art models.', icon: 'accurate' },
  { title: 'Multi-format', description: 'Support for text, images, videos, and documents.', icon: 'multiformat' },
  { title: 'Easy to Use', description: 'Intuitive drag-and-drop interface. No setup required.', icon: 'easy' },
  { title: 'Cloud Ready', description: 'Scalable cloud infrastructure for enterprise needs.', icon: 'cloud' },
];

export const SUPPORTED_FORMATS = [
  'TXT', 'PDF', 'DOCX', 'PNG', 'JPG', 'JPEG', 'MP4', 'MOV', 'AVI', 'WEBP',
];

export const TESTIMONIALS = [
  {
    name: 'Arjun Sharma',
    role: 'Student',
    avatar: null,
    rating: 5,
    review: 'Gaia Detector helped me verify the authenticity of research papers for my thesis. The accuracy is impressive and the interface is incredibly intuitive.',
  },
  {
    name: 'Dr. Priya Mehta',
    role: 'Professor',
    avatar: null,
    rating: 5,
    review: 'As an educator, detecting AI-generated submissions is crucial. Gaia Detector provides detailed analysis that helps maintain academic integrity.',
  },
  {
    name: 'Rahul Verma',
    role: 'Researcher',
    avatar: null,
    rating: 4,
    review: 'The multi-format support is a game changer. Being able to analyze text, images, and documents in one platform saves hours of work.',
  },
];

export const FAQ_ITEMS = [
  {
    question: 'What files are supported?',
    answer: 'Gaia Detector supports a wide range of file formats including TXT, PDF, DOCX for text documents, PNG, JPG, JPEG, WEBP for images, and MP4, MOV, AVI for video files. We are continuously adding support for more formats.',
  },
  {
    question: 'How accurate is the analysis?',
    answer: 'Our AI models achieve over 95% accuracy in detecting AI-generated content. We use ensemble methods combining multiple detection strategies to minimize false positives and false negatives.',
  },
  {
    question: 'Is my data secure?',
    answer: 'Absolutely. We use end-to-end encryption for all file uploads and processing. Your files are automatically deleted after analysis is complete, and we never store or share your data with third parties.',
  },
  {
    question: 'Do you store uploaded files?',
    answer: 'No. Uploaded files are processed in real-time and immediately deleted from our servers after analysis. We maintain a strict zero data retention policy for maximum privacy.',
  },
];

export const FOOTER_LINKS = {
  quickLinks: [
    { name: 'Home', path: '/' },
    { name: 'Features', path: '/features' },
    { name: 'How It Works', path: '/how-it-works' },
    { name: 'About', path: '/about' },
  ],
  resources: [
    { name: 'Documentation', path: '#' },
    { name: 'API Reference', path: '#' },
    { name: 'Blog', path: '#' },
    { name: 'FAQ', path: '#' },
  ],
  contact: [
    { name: 'support@gaiadetector.com', path: 'mailto:support@gaiadetector.com' },
    { name: 'GitHub', path: 'https://github.com' },
    { name: 'LinkedIn', path: 'https://linkedin.com' },
  ],
};
