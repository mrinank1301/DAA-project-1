# FlavorGraph - Quick Start Guide

Welcome to FlavorGraph! This guide will help you get both the backend and frontend running quickly.

## 🚀 Quick Start (5 minutes)

### Step 1: Start the Backend API

Open a terminal and run:

```bash
# Navigate to backend directory
cd Backend

# Install Python dependencies (first time only)
pip install -r requirements.txt

# Start the backend server
python run.py
```

The backend will start at `http://localhost:8000`

✅ **Verify**: Open `http://localhost:8000/docs` in your browser to see the API documentation

### Step 2: Start the Frontend

Open a **new terminal** (keep the backend running) and run:

```bash
# Navigate to frontend directory
cd "Frontend/receipe"

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

The frontend will start at `http://localhost:3000`

### Step 3: Use the Application

1. Open your browser to `http://localhost:3000`
2. Add ingredients you have (e.g., "tomato", "pasta", "garlic", "chicken")
3. Optionally set filters (dietary preferences, meal type, etc.)
4. Click "Find Recipes 🔍"
5. Browse results and click any recipe card for full details

## 📝 Example Usage

**Try searching for these ingredients:**
- `tomato, pasta, garlic, olive oil, basil`
- `chicken, rice, onion, bell pepper, soy sauce`
- `eggs, milk, flour, sugar, butter`

## 🎯 Features to Explore

### Main Features
- ✅ Intelligent recipe matching based on available ingredients
- ✅ Advanced filtering (dietary preferences, meal type, difficulty)
- ✅ Algorithm insights showing analysis time and recipes analyzed
- ✅ Recipe details with step-by-step instructions
- ✅ Nutritional information display
- ✅ Match scores showing how well recipes fit your ingredients

### Backend Algorithms
The system uses three powerful algorithms:
- **Graph Theory**: Models ingredient relationships
- **Backtracking**: Finds optimal recipe combinations
- **Greedy Algorithm**: Provides fast, near-optimal suggestions

## 🛠️ Project Structure

```
DAA Project -1/
├── Backend/                 # FastAPI backend
│   ├── algorithms/         # Core algorithms (graph, backtracking, greedy)
│   ├── api/                # API routes
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   └── run.py              # Backend entry point
│
├── Frontend/receipe/       # Next.js frontend
│   ├── app/                # Pages
│   ├── components/         # React components
│   ├── lib/                # API client
│   └── types/              # TypeScript types
│
└── QUICKSTART.md           # This file
```

## 📚 API Endpoints

The frontend uses these key endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/recipes/suggest` | POST | Get recipe suggestions |
| `/api/v1/recipes/{id}` | GET | Get recipe details |
| `/api/v1/recipes` | GET | List all recipes |
| `/api/v1/ingredients` | GET | List ingredients |
| `/api/v1/health` | GET | Health check |

## 🔧 Configuration

### Backend Configuration
- Default port: `8000`
- Config file: `Backend/config.py`
- Environment: Development mode by default

### Frontend Configuration
- Default port: `3000`
- API URL: Configured in `Frontend/receipe/.env.local`
- Current setting: `http://localhost:8000/api/v1`

## ⚠️ Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError`
```bash
# Solution: Install dependencies
cd Backend
pip install -r requirements.txt
```

**Issue**: `Port 8000 already in use`
```bash
# Solution: Kill the process or change port in config.py
```

### Frontend Issues

**Issue**: `Failed to fetch recipes`
```bash
# Solution: Ensure backend is running
curl http://localhost:8000/api/v1/health
```

**Issue**: `Port 3000 already in use`
```bash
# Solution: Use different port
cd "Frontend/receipe"
$env:PORT=3001; npm run dev  # PowerShell
# or
PORT=3001 npm run dev  # Mac/Linux
```

**Issue**: `Module not found errors`
```bash
# Solution: Reinstall dependencies
cd "Frontend/receipe"
rm -rf node_modules package-lock.json
npm install
```

## 📖 Documentation

- **Backend README**: `Backend/README.md`
- **Frontend README**: `Frontend/receipe/README.md`
- **Frontend Setup**: `Frontend/receipe/SETUP.md`
- **API Docs**: `http://localhost:8000/docs` (when backend is running)

## 🎨 Technology Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **Algorithms**: Graph Theory, Backtracking, Greedy
- **Data Validation**: Pydantic

### Frontend
- **Framework**: Next.js 15
- **Language**: TypeScript
- **UI**: React 19
- **Styling**: Tailwind CSS 4
- **State Management**: React Hooks

## 💡 Tips

1. **Better Results**: Add more common ingredients for better recipe matches
2. **Dietary Filters**: Use dietary preference tags to narrow down options
3. **Missing Ingredients**: Adjust the "Max Missing Ingredients" slider to see more or fewer recipes
4. **Quick Recipes**: Set "Max Prep Time" for faster meal options
5. **Algorithm Insights**: Check the analysis results to see which algorithm was used

## 🎯 Next Steps

1. ✅ Start both backend and frontend
2. ✅ Try searching with sample ingredients
3. ✅ Explore recipe details
4. ✅ Test different filters
5. ✅ View algorithm insights
6. 📖 Read the full documentation
7. 🔧 Customize the application for your needs

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review backend logs in the terminal
- Check browser console for frontend errors
- Refer to the detailed README files in each directory

---

**Happy Cooking with FlavorGraph! 🍳** 
