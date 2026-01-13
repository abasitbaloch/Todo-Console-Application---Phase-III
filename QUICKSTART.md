# Quick Start Guide - Todo Full-Stack Application

Get the application running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check Node.js version (need 18+)
node --version

# Check if you have a PostgreSQL database ready
# Recommended: Sign up for free at https://neon.tech
```

## Step 1: Clone and Navigate

```bash
cd Todo-Console-Application-main
```

## Step 2: Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -e .

# Create environment file
cp .env.example .env

# Edit .env with your database credentials
# Required: DATABASE_URL and JWT_SECRET
# Example DATABASE_URL: postgresql+asyncpg://user:pass@host:port/database
```

**Edit `backend/.env`:**
```env
DATABASE_URL=postgresql+asyncpg://your-connection-string-here
JWT_SECRET=your-super-secret-key-at-least-32-characters-long
CORS_ORIGINS=http://localhost:3000
```

```bash
# Run database migrations
python -m alembic upgrade head

# Verify backend works
uvicorn src.main:app --reload --port 8000
# Visit http://localhost:8000/docs to see API documentation
```

## Step 3: Frontend Setup (2 minutes)

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Edit .env.local with the SAME secret as backend
```

**Edit `frontend/.env.local`:**
```env
AUTH_SECRET=your-super-secret-key-at-least-32-characters-long
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
```

**⚠️ CRITICAL**: `AUTH_SECRET` MUST match backend's `JWT_SECRET`

```bash
# Start frontend
npm run dev
# Visit http://localhost:3000
```

## Step 4: Test the Application (1 minute)

1. **Open browser**: http://localhost:3000
2. **Register**: Click "Sign up" → Enter email and password → Submit
3. **Create task**: Enter task title → Click "Create Task"
4. **Test features**:
   - ✅ Check/uncheck to mark complete
   - ✏️ Click "Edit" to modify task
   - 🗑️ Click "Delete" to remove task
5. **Logout**: Click "Logout" button
6. **Login again**: Verify your tasks are still there

## Alternative: Run Both Servers Together

From the root directory:

```bash
# Install root dependencies
npm install

# Start both servers simultaneously
npm run dev
```

This will start:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## Troubleshooting

### "Database connection failed"
- Verify your DATABASE_URL is correct
- For Neon: Make sure you're using `postgresql+asyncpg://` (not just `postgresql://`)
- Check your database is accessible from your network

### "Authentication fails after login"
- Verify `AUTH_SECRET` (frontend) matches `JWT_SECRET` (backend)
- Both must be identical strings
- Restart both servers after changing environment variables

### "Module not found" errors
```bash
# Backend
cd backend && pip install -e .

# Frontend
cd frontend && rm -rf node_modules && npm install
```

### "Port already in use"
```bash
# Find and kill process on port 8000 (backend)
# Windows: netstat -ano | findstr :8000
# Mac/Linux: lsof -ti:8000 | xargs kill

# Find and kill process on port 3000 (frontend)
# Windows: netstat -ano | findstr :3000
# Mac/Linux: lsof -ti:3000 | xargs kill
```

## What You Get

### ✅ Complete Features
- User registration and authentication
- JWT-based secure sessions
- Create, read, update, delete tasks
- Inline editing of tasks
- Mark tasks complete/incomplete
- Data isolation (users only see their own tasks)
- Responsive design (mobile and desktop)
- Loading states and error handling
- Success feedback messages
- Smooth animations

### 🔒 Security Features
- Bcrypt password hashing
- JWT token authentication
- User data isolation
- Ownership validation
- CORS protection
- Input validation
- XSS prevention

### 📱 UI/UX Features
- Mobile-first responsive design
- Touch-friendly tap targets (44px minimum)
- Keyboard navigation support
- Focus indicators for accessibility
- Loading spinners
- Error messages
- Success notifications
- Smooth animations

## Next Steps

### For Development
1. Read `backend/README.md` for API documentation
2. Read `frontend/README.md` for component documentation
3. Visit http://localhost:8000/docs for interactive API docs
4. Explore the codebase structure in root `README.md`

### For Production
1. Set up production database
2. Configure production environment variables
3. Build frontend: `cd frontend && npm run build`
4. Deploy backend with production ASGI server
5. Deploy frontend with Vercel or similar platform

### For Testing
1. Create multiple user accounts
2. Test data isolation (users can't see each other's tasks)
3. Test on mobile devices
4. Test with slow network (throttle in DevTools)
5. Test accessibility with screen reader

## API Endpoints Quick Reference

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user

### Tasks (Requires Authentication)
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Health
- `GET /health` - Health check

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the detailed README files
3. Check the API documentation at http://localhost:8000/docs
4. Review the specification in `specs/001-fullstack-web-app/`

## Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can register new account
- [ ] Can login with credentials
- [ ] Can create tasks
- [ ] Can edit tasks inline
- [ ] Can mark tasks complete/incomplete
- [ ] Can delete tasks
- [ ] Can logout and login again
- [ ] Tasks persist after logout/login
- [ ] Different users see different tasks

If all items are checked, congratulations! Your application is fully functional! 🎉
