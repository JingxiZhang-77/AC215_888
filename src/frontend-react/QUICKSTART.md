# React Frontend - Quick Start Guide

## 🚀 Getting Started

### Option 1: Run with Docker (Recommended)

This is the recommended approach as it provides a consistent environment.

1. **Navigate to frontend directory**
   ```bash
   cd src/frontend-react
   ```

2. **Run docker shell script**
   ```bash
   ./docker-shell.sh
   ```

3. **Inside container, install dependencies**
   ```bash
   npm install
   ```

4. **Inside container, start dev server**
   ```bash
   npm run dev
   ```

5. **Open browser**
   Navigate to http://localhost:3001

### Option 2: Run Locally (Alternative)

If you prefer to run without Docker:

1. **Navigate to frontend directory**
   ```bash
   cd src/frontend-react
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open browser**
   Navigate to http://localhost:3001

## 📋 Prerequisites

Before running the frontend, ensure:

1. **Backend API is running**
   - The FastAPI backend must be running on http://localhost:9000
   - See `src/api/README.md` for backend setup instructions

2. **Node.js is installed**
   - Version 18 or higher
   - Check with: `node --version`

3. **npm is installed**
   - Usually comes with Node.js
   - Check with: `npm --version`

## Prerequisites

Before running the frontend, ensure:

1. **Backend API is running**
   - The FastAPI backend must be running on http://localhost:9000
   - See `src/api/README.md` for backend setup instructions

2. **Docker installed** (for Docker workflow)
   - Docker Desktop for Mac/Windows
   - Check with: `docker --version`

3. **Node.js installed** (for local workflow)
   - Version 18 or higher
   - Check with: `node --version`

## 🔐 Test Account Credentials

Use the bundled admin account while the MVP keeps registration disabled:

| Username | Password | Role | Department | Access Level |
|----------|----------|------|------------|--------------|
| admin | admin123 | Admin | Internal Medicine | Full system access |

> If you need additional roles later, re-enable `/auth/register` in the API and restore the `/register` page.

## 📱 Available Pages

After logging in, you can access:

- **Home** (/) - Dashboard with feature overview
- **Classify** (/classify) - Single incident classification
- **Batch** (/batch) - CSV/Excel batch processing
- **Audio** (/audio) - Audio transcription & classification
- **Users** (/users) - User management (admin only)

## 🎨 Features to Test

### 1. Single Classification
- Enter an incident description
- Select a department
- View classification result with rationales

### 2. Batch Processing
- Upload a CSV/Excel file with columns: `description`, `department`
- Download the starter file from the Batch page (`/batch`) if you need an example (`public/batch-template.csv`)
- View processing summary
- Download results file

### 3. Audio Transcription
- Upload an audio file (WAV, MP3, OGG, FLAC)
- Select language (English, Mandarin, Cantonese, French, Spanish)
- Enable auto-translation to English
- View transcription and classification

### 4. User Management (Admin Only)
- View all system users
- Edit user details (email, role, department)
- Delete users
- Search users by username/email/role

## 🔧 Configuration

Environment variables are in `.env.development`:

```env
NEXT_PUBLIC_API_URL=http://localhost:9000/api/v1
```

Change this if your backend runs on a different port or domain.

## 📦 Project Structure

```
src/frontend-react/
├── src/
│   ├── app/              # Next.js pages (login, classify, batch, etc.)
│   ├── components/       # Reusable UI components
│   └── lib/              # API service, utilities, auth helpers
├── public/               # Static assets
├── package.json          # Dependencies
├── tailwind.config.js    # Styling configuration
└── README.md             # Full documentation
```

## 🐛 Troubleshooting

### Cannot connect to API
- **Check**: Backend API is running on port 9000
- **Fix**: Start the backend with `cd src/api && ./docker-shell.sh`

### Login fails
- **Check**: Using correct credentials (admin/admin123)
- **Fix**: Check backend logs for authentication errors

### Page shows "Access Denied"
- **Check**: Your user role has permission for that page
- **Fix**: Login as admin for full access

### npm install fails
- **Check**: Node.js version 18+
- **Fix**: Update Node.js: `brew install node` (macOS)

## 📚 Next Steps

1. **Read full documentation**: See `README.md` in this directory
2. **Explore backend API**: See `src/api/README.md`
3. **Test classification**: Try sample incidents
4. **Upload batch file**: Use the template in `safety_incident_template.csv`

## 🎯 Development Tips

- **Hot reload**: Changes auto-refresh in dev mode
- **Console logs**: Open browser DevTools (F12) for debugging
- **API errors**: Check Network tab in DevTools
- **Component inspector**: Use React DevTools extension

## 🚨 Common Issues

1. **Port 3001 already in use**
   ```bash
   # Kill process using port 3001
   lsof -ti:3001 | xargs kill -9
   ```

2. **CSS not loading**
   ```bash
   # Rebuild Tailwind
   npm run dev
   ```

3. **Token expired**
   - Simply logout and login again
   - Tokens expire after 24 hours

## 📞 Support

For issues or questions:
1. Check the full README.md in this directory
2. Review backend API documentation
3. Check browser console for error messages
4. Verify backend API is accessible

---

**Happy Testing! 🎉**
