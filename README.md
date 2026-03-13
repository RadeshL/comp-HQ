# comp-HQ

comp-HQ is an AI-powered component sourcing assistant that finds the best products for a project. Users enter required components, and the system searches online stores, compares prices, sellers, ratings, and reviews, and shows the top options. Selected items are compiled into a report with seller details and prices, exportable as a Word document.

## Features

- 🤖 **AI-Powered Search**: Automatically searches multiple online retailers for components using intelligent web scraping with LangChain
- 📊 **Smart Ranking**: Products ranked using hybrid scoring algorithm (price, rating, reviews)
- 🛒 **Multi-Retailer Support**: Direct scraping from SparkFun, Adafruit, Digi-Key, Mouser, BangGood, and more
- 📋 **Interactive Selection**: User-friendly interface for product comparison and selection
- 📄 **Report Generation**: Export detailed procurement reports as Word documents
- 💾 **Session Management**: Track selections across multiple components

## Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Web framework with automatic API documentation
- **SQLAlchemy** - ORM for database operations
- **LangChain** - Intelligent web scraping with DuckDuckGo search
- **BeautifulSoup4** - HTML parsing and product extraction
- **Requests & Selenium** - HTTP client and browser automation
- **ThreadPoolExecutor** - Concurrent processing for performance
- **python-docx** - Word document generation

### Frontend
- **React js** - UI framework
- **TailwindCSS** - Styling
- **Axios** - API client

## Project Structure

```
comp-HQ/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database setup and connection
│   ├── models.py               # SQLAlchemy models and Pydantic schemas
│   ├── agents/
│   │   └── ranking_agent.py    # AI ranking logic
│   ├── tools/
│   │   ├── search_tool.py      # Product search across retailers
│   │   ├── scraper_tool.py     # Web scraping utilities
│   │   └── ranking_tool.py     # Product ranking algorithms
│   ├── services/
│   │   ├── component_service.py # Component workflow orchestration
│   │   └── report_service.py   # Report generation
│   └── api/
│       ├── component_routes.py # Component API endpoints
│       └── report_routes.py    # Report API endpoints
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React application
│   │   ├── api.js              # API client configuration
│   │   ├── index.css           # TailwindCSS styles
│   │   ├── components/
│   │   │   ├── ComponentInput.jsx    # Component input form
│   │   │   ├── ProductOptions.jsx    # Product selection cards
│   │   │   └── ReportView.jsx        # Report display and export
│   │   └── pages/
│   │       └── Dashboard.jsx         # Main application dashboard
│   ├── package.json            # Frontend dependencies
│   └── tailwind.config.js      # TailwindCSS configuration
│
└── requirements.txt            # Python dependencies
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   python main.py
   ```

   The backend will start on `http://localhost:8000`

4. **Verify API is working**
   ```bash
   curl http://localhost:8000/api/health
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the frontend development server**
   ```bash
   npm start
   ```

   The frontend will start on `http://localhost:3000`

### Alternative: Using PostCSS for TailwindCSS

If you encounter TailwindCSS warnings, set up PostCSS:

1. **Create PostCSS config**
   ```bash
   echo "module.exports = {
     plugins: {
       tailwindcss: {},
       autoprefixer: {},
     },
   }" > postcss.config.js
   ```

2. **Install PostCSS dependencies**
   ```bash
   npm install --save-dev postcss autoprefixer
   ```

## Usage

1. **Start both servers** (backend on port 8000, frontend on port 3000)

2. **Open your browser** and navigate to `http://localhost:3000`

3. **Enter components** you want to source (one per line):
   ```
   Arduino Uno
   ESP32
   Ultrasonic Sensor
   LED Strip
   Breadboard
   ```

4. **Review product options** for each component:
   - View top 3 ranked products
   - Check ratings, prices, and reviews
   - Read AI-powered ranking reasoning
   - Click "Select This Product" for your choice

5. **Generate procurement report**:
   - After all components are processed
   - View summary with total cost and average rating
   - Click "Generate Word Report" for detailed document
   - Download the report for your records

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

- `POST /api/components/` - Submit component list
- `GET /api/components/products/{component_name}` - Get ranked products
- `POST /api/components/select` - Save product selection
- `POST /api/reports/generate` - Generate procurement report
- `GET /api/reports/download/{filename}` - Download report

## Configuration

### Backend Settings (backend/config.py)

```python
# Database
DATABASE_URL = "sqlite:///./comp_hq.db"

# API
API_HOST = "0.0.0.0"
API_PORT = 8000

# Scraping
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 ..."

# Ranking
TOP_PRODUCTS_COUNT = 3

# Search sources
SEARCH_SOURCES = ["amazon", "digikey", "sparkfun", "adafruit"]
```

### Frontend Settings (frontend/src/api.js)

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## Development

### Adding New Retailers

1. **Add search method** in `backend/tools/search_tool.py`
2. **Add scraper method** in `backend/tools/scraper_tool.py`
3. **Update search sources** in `backend/config.py`

### Custom Ranking Logic

Modify the ranking algorithm in `backend/tools/ranking_tool.py`:
- Adjust weight coefficients
- Add new scoring factors
- Implement custom ranking rules

### Adding Report Features

Extend the report generation in `backend/services/report_service.py`:
- Add new sections
- Customize formatting
- Include additional metrics

## Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python version (3.8+)
   - Install all dependencies: `pip install -r requirements.txt`
   - Check for import errors in logs

2. **Frontend TailwindCSS warnings**
   - Install PostCSS: `npm install --save-dev postcss autoprefixer`
   - Create `postcss.config.js` file
   - Restart development server

3. **API connection errors**
   - Ensure backend is running on port 8000
   - Check CORS settings in `backend/main.py`
   - Verify API_BASE_URL in `frontend/src/api.js`

4. **Scraping issues**
   - Some websites may block scraping
   - Check USER_AGENT string in config
   - Respect rate limits when testing

### Debug Mode

Enable debug logging by modifying `backend/main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```



**comp-HQ** - Making component sourcing intelligent and efficient! 🚀
