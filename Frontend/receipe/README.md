# FlavorGraph Frontend

A modern, beautiful frontend for the FlavorGraph intelligent recipe recommendation system built with Next.js 15, React 19, and TypeScript.

## Features

- 🔍 **Smart Recipe Search**: Find recipes based on available ingredients
- 🎯 **Advanced Filtering**: Filter by dietary preferences, meal type, difficulty, and more
- 📊 **Algorithm Insights**: View analysis powered by Graph Theory, Backtracking & Greedy algorithms
- 📱 **Responsive Design**: Beautiful UI that works on all devices
- ⚡ **Real-time Search**: Fast and efficient recipe matching
- 🎨 **Modern UI**: Clean, intuitive interface with Tailwind CSS

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Update `.env.local` with your backend API URL (defaults to `http://localhost:8000/api/v1`)

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
Frontend/receipe/
├── app/                    # Next.js app directory
│   ├── page.tsx           # Home page with recipe search
│   ├── recipe/[id]/       # Recipe details page
│   ├── layout.tsx         # Root layout with navigation
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── RecipeCard.tsx     # Recipe card component
│   ├── IngredientSelector.tsx  # Ingredient input component
│   ├── LoadingSpinner.tsx # Loading state component
│   └── ErrorMessage.tsx   # Error state component
├── lib/                   # Utility functions
│   └── api.ts            # API client
├── types/                # TypeScript type definitions
│   └── api.ts           # API types
└── public/              # Static assets
```

## API Integration

The frontend communicates with the FlavorGraph backend API. Make sure the backend is running before starting the frontend.

Backend API endpoints used:
- `POST /api/v1/recipes/suggest` - Get recipe suggestions
- `GET /api/v1/recipes/{id}` - Get recipe details
- `GET /api/v1/ingredients` - List ingredients
- `GET /api/v1/health` - Health check

## Technologies

- **Framework**: Next.js 15 (App Router)
- **React**: 19.1.0
- **TypeScript**: 5+
- **Styling**: Tailwind CSS 4
- **HTTP Client**: Native Fetch API

## Features Overview

### Home Page
- Ingredient selector with easy add/remove functionality
- Advanced filters:
  - Dietary preferences (vegetarian, vegan, gluten-free, etc.)
  - Meal type selection
  - Difficulty level
  - Max missing ingredients slider
  - Max prep time input
- Real-time recipe search
- Algorithm analysis results display
- Grid of recipe cards with match scores

### Recipe Detail Page
- Full recipe information
- Step-by-step instructions
- Ingredient list with quantities
- Nutritional information
- Equipment needed
- Dietary tags and ratings
- Cooking tips

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License
