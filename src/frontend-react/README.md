# Safety Event Classification System - React Frontend

A modern React/Next.js frontend for the AI-powered healthcare safety incident classification system.

## Features

- **Modern Tech Stack**: React 18, Next.js 15, Tailwind CSS
- **Authentication**: JWT-based login/register with role-based access control (RBAC)
- **Single Classification**: Interactive form for individual incident classification
- **Batch Processing**: CSV/Excel file upload for bulk classification
- **Audio Transcription**: 5-language audio-to-text with automatic translation
- **User Management**: Admin interface for managing system users
- **Responsive Design**: Mobile-first responsive UI with Radix UI components
- **Real-time Feedback**: Loading states, error handling, and success notifications

## Tech Stack

- **Framework**: Next.js 15.0.3 (App Router)
- **UI Library**: React 18.3.1
- **Styling**: Tailwind CSS 3.4.7
- **HTTP Client**: Axios 1.7.7
- **UI Components**: Radix UI primitives
- **Icons**: Lucide React 0.552.0
- **State Management**: React hooks (useState, useEffect)
- **Authentication**: JWT tokens in localStorage

## Project Structure

```
src/frontend-react/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.jsx          # Root layout with Header/Footer
│   │   ├── page.jsx            # Home page with feature cards
│   │   ├── login/page.jsx      # Login page
│   │   ├── register/page.jsx   # Registration page
│   │   ├── classify/page.jsx   # Single incident classification
│   │   ├── batch/page.jsx      # Batch CSV/Excel processing
│   │   ├── audio/page.jsx      # Audio transcription & classification
│   │   ├── users/page.jsx      # User management (admin only)
│   │   └── globals.css         # Global styles with Tailwind
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   │   ├── button.jsx
│   │   │   ├── card.jsx
│   │   │   ├── input.jsx
│   │   │   ├── label.jsx
│   │   │   ├── select.jsx
│   │   │   ├── textarea.jsx
│   │   │   └── tabs.jsx
│   │   └── layout/             # Layout components
│   │       ├── Header.jsx      # Navigation header
│   │       └── Footer.jsx      # Footer
│   └── lib/
│       ├── Common.js           # Auth utilities, token management
│       ├── DataService.js      # API service layer with axios
│       └── utils.js            # Utility functions (cn)
├── public/                     # Static assets
├── .env.development            # Development environment variables
├── .env.production             # Production environment variables
├── package.json                # Dependencies and scripts
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── postcss.config.js           # PostCSS configuration
├── jsconfig.json               # Path aliases
├── Dockerfile                  # Multi-stage production build
├── docker-shell.sh             # Development container script
└── README.md                   # This file
```

## Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:9000
- Docker (optional, for containerized deployment)

## Installation

### Option 1: Docker Deployment (Recommended)

1. **Build and run the container**
   ```bash
   ./docker-shell.sh
   ```

2. **Inside the container, install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   
   Open http://localhost:3001 in your browser

### Option 2: Local Installation

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   
   Create `.env.development` for local development:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:9000/api/v1
   ```

   Create `.env.production` for production:
   ```env
   NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```
   
   The application will be available at http://localhost:3001

## Test Accounts

Pre-configured test accounts for immediate use:

| Username | Password | Role | Department | Access Level |
|----------|----------|------|------------|--------------|
| admin | admin123 | Admin | Internal Medicine | Full system access |
| doctor1 | doctor123 | Doctor | Surgery | Classify, batch, audio |
| nurse1 | nurse123 | Nurse | OB/GYN/NICU | Classify, batch, audio |
| viewer1 | viewer123 | Viewer | Radiology/Imaging | Read-only |

You can also create new accounts via the registration page.

## Development

### Available Scripts

- `npm run dev` - Start development server on port 3001
- `npm run build` - Build production bundle
- `npm start` - Start production server
- `npm run lint` - Run ESLint

### Key Features

#### 1. Authentication
- JWT token-based authentication
- Token stored in localStorage
- Automatic token injection via axios interceptors
- Redirect to login on 401 errors

#### 2. Role-Based Access Control (RBAC)
- **Admin**: Full access to all features including user management
- **Doctor/Nurse**: Can classify incidents, batch process, and use audio
- **Viewer**: Read-only access to home page

#### 3. API Integration
All API calls are centralized in `src/lib/DataService.js`:
- **Auth**: login, register, password reset
- **Classification**: single, batch, audio
- **Audio**: transcribe, get supported languages
- **Users**: list, get, update, delete (admin only)

#### 4. UI Components
Reusable components built with Radix UI primitives:
- Button with variants (default, outline, ghost, destructive)
- Card with header, content, footer
- Input, Textarea, Label
- Select dropdown
- Tabs for multi-mode interfaces

#### 5. Styling
- Tailwind CSS with custom theme
- HSL-based color system
- Dark mode support (configurable)
- Responsive breakpoints (sm, md, lg, xl)
- Custom utility classes for classification codes

## API Endpoints Used

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset-password` - Reset password with token
- `POST /auth/verify-token` - Verify JWT token

### Classification
- `POST /classification/classify` - Single incident classification
- `POST /classification/batch` - Batch CSV/Excel processing
- `POST /classification/audio` - Audio transcription + classification

### Audio
- `POST /audio/transcribe` - Audio transcription only
- `GET /audio/languages` - Get supported languages

### Users (Admin Only)
- `GET /users` - List all users
- `GET /users/{username}` - Get user details
- `GET /users/me` - Get current user
- `PUT /users/{username}` - Update user
- `DELETE /users/{username}` - Delete user

## Docker Deployment

### Development
```bash
chmod +x docker-shell.sh
./docker-shell.sh
```

### Production
```bash
docker build -t safety-event-frontend-react .
docker run -p 3001:3001 safety-event-frontend-react
```

The Docker image uses a multi-stage build:
1. **Builder stage**: Installs deps and builds Next.js app
2. **Runner stage**: Production-ready Node.js image with standalone output

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API base URL (required)

## Classification Codes

The system uses a 4-level classification system (ranked by descending level of seriousness):
- **SSE** (Serious Safety Event) - Deviation reached the patient and caused moderate/severe harm or death
- **PSE** (Precursor Safety Event) - Deviation reached the patient with no or minimal harm
- **NME** (Near Miss Event) - Deviation occurred but did not reach the patient
- **NSE** (No Safety Event) - No deviation from Generally Accepted Performance Standards (GAPS)

## Supported Languages

Audio transcription supports 5 languages:
1. English (en-US)
2. Mandarin (zh-CN)
3. Cantonese (zh-HK)
4. French (fr-FR)
5. Spanish (es-ES)

Non-English audio is automatically translated to English for classification.

## Supported Departments

The system tracks 5 medical departments:
1. Internal Medicine
2. Surgery
3. OB/GYN/NICU
4. Radiology/Imaging
5. Outpatient/ER

## User Roles

Four role levels:
1. **Admin** - Full system access
2. **Doctor** - Classify, batch, audio access
3. **Nurse** - Classify, batch, audio access
4. **Viewer** - Read-only access

## Troubleshooting

### CORS Errors
Ensure the backend API has CORS configured to allow requests from http://localhost:3001

### Authentication Issues
- Check that JWT token is being stored in localStorage
- Verify token format in axios request headers
- Check backend API token validation

### Build Errors
- Delete `.next` folder and `node_modules`
- Run `npm install` again
- Ensure Node.js version is 18+

## Contributing

1. Follow the existing component structure
2. Use TypeScript-style JSDoc comments
3. Maintain consistent naming conventions
4. Test all API integrations
5. Ensure responsive design on mobile devices

## License

Part of the AC215_888 Safety Event Classification System
