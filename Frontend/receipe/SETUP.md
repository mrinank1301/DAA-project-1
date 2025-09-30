# FlavorGraph Frontend Setup Guide

This guide will help you set up and run the FlavorGraph frontend application.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** 18.17 or later
- **npm** or **yarn** package manager
- The **FlavorGraph Backend** running on `http://localhost:8000`

## Step-by-Step Setup

### 1. Navigate to the Frontend Directory

```bash
cd "Frontend/receipe"
```

### 2. Install Dependencies

Install all required npm packages:

```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env.local` file in the `Frontend/receipe` directory:

```bash
# Windows PowerShell
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# macOS/Linux
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
```

Or manually create `.env.local` with the following content:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 4. Start the Backend API

Before running the frontend, make sure the backend is running:

```bash
# In a separate terminal, navigate to Backend directory
cd "Backend"

# Install backend dependencies (if not already done)
pip install -r requirements.txt

# Run the backend
python run.py
```

The backend should be accessible at `http://localhost:8000`.

### 5. Run the Development Server

Start the Next.js development server:

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

### 6. Open in Browser

Visit [http://localhost:3000](http://localhost:3000) in your web browser to use the application.

## Testing the Application

1. **Add Ingredients**: Type ingredient names and press Enter or click "Add"
   - Example: `tomato`, `pasta`, `garlic`, `olive oil`

2. **Set Filters** (optional):
   - Select dietary preferences
   - Choose meal type
   - Set difficulty level
   - Adjust max missing ingredients
   - Set max prep time

3. **Search**: Click "Find Recipes 🔍" to get recipe suggestions

4. **View Results**: Browse recipe cards with match scores

5. **View Details**: Click any recipe card to see full details

## Production Build

To create an optimized production build:

```bash
# Build the application
npm run build

# Start the production server
npm start
```

## Troubleshooting

### Issue: "Failed to fetch recipes" or Network Error

**Solution**: Ensure the backend API is running on `http://localhost:8000`

```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "FlavorGraph API",
  ...
}
```

### Issue: Port 3000 Already in Use

**Solution**: Use a different port

```bash
PORT=3001 npm run dev
```

### Issue: Module Not Found Errors

**Solution**: Reinstall dependencies

```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: TypeScript Errors

**Solution**: Check TypeScript configuration

```bash
npm run lint
```

## API Endpoints Used

The frontend communicates with these backend endpoints:

- `POST /api/v1/recipes/suggest` - Get recipe suggestions
- `GET /api/v1/recipes/{id}` - Get recipe details
- `GET /api/v1/recipes` - List all recipes
- `GET /api/v1/ingredients` - List ingredients
- `GET /api/v1/health` - Health check

## Features

✅ Smart ingredient-based recipe search  
✅ Advanced filtering options  
✅ Algorithm insights display  
✅ Detailed recipe view  
✅ Responsive design  
✅ Real-time search  
✅ Match score visualization  
✅ Nutritional information display  

## Next Steps

- Explore the recipe suggestions
- Try different ingredient combinations
- View detailed recipe information
- Check out the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

## Support

For issues or questions:
1. Check the backend logs
2. Review browser console for errors
3. Ensure all dependencies are installed correctly
4. Verify environment variables are set correctly

Happy cooking! 🍳 