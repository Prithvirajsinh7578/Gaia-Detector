import express from 'express';
import multer from 'multer';
import cors from 'cors';
import { existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3001;

// Create tempdect folder if it doesn't exist
const uploadDir = join(__dirname, 'tempdect');
if (!existsSync(uploadDir)) {
  mkdirSync(uploadDir, { recursive: true });
}

// CORS for Vite dev server
app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:5174', 'http://localhost:3000'],
  methods: ['POST'],
}));

// Multer storage config
const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, uploadDir);
  },
  filename: (_req, file, cb) => {
    // Add timestamp prefix to avoid conflicts
    const uniqueName = `${Date.now()}-${file.originalname}`;
    cb(null, uniqueName);
  },
});

const upload = multer({
  storage,
  limits: { fileSize: 50 * 1024 * 1024 }, // 50MB limit
});

// Upload endpoint
app.post('/api/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  console.log(`✅ File saved: ${req.file.filename} (${(req.file.size / 1024).toFixed(1)} KB)`);
  console.log(`   Type: ${req.body.type || 'unknown'}`);
  console.log(`   Path: ${req.file.path}`);

  res.json({
    success: true,
    filename: req.file.filename,
    originalName: req.file.originalname,
    size: req.file.size,
    type: req.body.type,
    path: req.file.path,
  });
});

app.listen(PORT, () => {
  console.log('');
  console.log('🚀 Gaia Detector Upload Server');
  console.log(`   Running on http://localhost:${PORT}`);
  console.log(`   Upload directory: ${uploadDir}`);
  console.log('');
});
