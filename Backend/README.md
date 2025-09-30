# FlavorGraph: Intelligent Recipe Navigator with Algorithmic Insights

An intelligent recipe recommendation system that leverages graph theory, backtracking, and greedy algorithms to suggest recipes based on available ingredients, provide ingredient gap analysis, and offer substitution recommendations.

## Features

- **Graph-based Recipe Matching**: Uses graph theory to model ingredient relationships and recipe networks
- **Intelligent Recipe Suggestions**: Employs backtracking and greedy algorithms for optimal recipe recommendations
- **Ingredient Gap Analysis**: Identifies missing ingredients and suggests alternatives
- **Substitution Engine**: Recommends ingredient substitutions based on flavor profiles and nutritional content
- **RESTful API**: Clean API endpoints for easy integration
- **Algorithmic Insights**: Provides detailed analysis of recommendation decisions

## Architecture

### Core Algorithms

1. **Graph Theory**: Models ingredients and recipes as nodes with weighted edges representing compatibility
2. **Backtracking Algorithm**: Explores all possible recipe combinations to find optimal matches
3. **Greedy Algorithm**: Provides fast, near-optimal suggestions for real-time recommendations
4. **Similarity Matching**: Uses cosine similarity and Jaccard index for ingredient matching

### Key Components

- `models/`: Data models for recipes, ingredients, and graph structures
- `algorithms/`: Implementation of core algorithms (graph, backtracking, greedy)
- `services/`: Business logic for recipe matching and analysis
- `api/`: RESTful API endpoints
- `utils/`: Helper functions and utilities

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd flavorgraph
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

- `POST /recipes/suggest` - Get recipe suggestions based on available ingredients
- `GET /recipes/{recipe_id}` - Get detailed recipe information
- `POST /ingredients/analyze` - Analyze ingredient gaps and substitutions
- `GET /ingredients/substitutes/{ingredient_id}` - Get substitution recommendations
- `POST /graph/analyze` - Get graph-based analysis of ingredient relationships

## Example Usage

```python
import requests

# Get recipe suggestions
response = requests.post("http://localhost:8000/recipes/suggest", json={
    "available_ingredients": ["tomato", "onion", "garlic", "pasta"],
    "dietary_preferences": ["vegetarian"],
    "max_missing_ingredients": 2
})

suggestions = response.json()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 