# Vanna AI 0.7 - SQL Query Assistant

A complete application built with Vanna AI 0.7, Flask backend, and React frontend that allows you to train an AI model on your database schema and ask questions in natural language to generate SQL queries.

## Features

- **Train with DDL**: Add database schema (CREATE TABLE statements) to teach Vanna about your data structure
- **Train with Questions**: Provide example question-SQL pairs to improve accuracy
- **Natural Language Queries**: Ask questions in plain English and get SQL queries + results
- **View Training Data**: See all the DDL and question-SQL pairs the model has learned
- **Execute Queries**: Automatically run generated SQL and display results in tables

## Tech Stack

- **Backend**: Flask, Vanna AI 0.7, FAISS, SQLite
- **Frontend**: React, Vite, Axios
- **AI**: DeepSeek (via OpenAI-compatible API)

## Project Structure

```
vanna/
├── backend/
│   ├── app.py                 # Flask application with API endpoints
│   ├── vanna_config.py        # Vanna initialization and configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   └── data/                 # SQLite database and FAISS storage
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── styles/          # CSS styles
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # React entry point
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   └── index.html           # HTML entry point
└── README.md
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** and **npm** - [Download Node.js](https://nodejs.org/)
- **DeepSeek API Key** - Get one from [DeepSeek Platform](https://platform.deepseek.com/)

## Installation & Setup

### 1. Backend Setup

#### Step 1.1: Navigate to the backend directory

```bash
cd vanna/backend
```

#### Step 1.2: Create a virtual environment (recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 1.3: Install Python dependencies

```bash
pip install -r requirements.txt
```

#### Step 1.4: Configure environment variables

Create a `.env` file by copying the example:

```bash
cp .env.example .env
```

**On Windows (if `cp` doesn't work):**
```bash
copy .env.example .env
```

Edit the `.env` file and add your DeepSeek API key:

```env
FAISS_PATH=./data/faiss
SQLITE_DB_PATH=./data/database.db
FLASK_PORT=5000
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

#### Step 1.5: Create data directory

```bash
mkdir data
```

**On Windows (if `mkdir` doesn't work):**
```bash
md data
```

### 2. Frontend Setup

#### Step 2.1: Navigate to the frontend directory

Open a **new terminal** and navigate to the frontend:

```bash
cd vanna/frontend
```

#### Step 2.2: Install Node dependencies

```bash
npm install
```

## Running the Application

You need to run both the backend and frontend servers simultaneously.

### Terminal 1: Start the Backend Server

```bash
cd vanna/backend

# Activate virtual environment first (if not already activated)
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

python app.py
```

You should see output similar to:
```
 * Running on http://0.0.0.0:5000
 * Restarting with stat
```

The backend API will be available at `http://localhost:5000`

### Terminal 2: Start the Frontend Development Server

```bash
cd vanna/frontend

npm run dev
```

You should see output similar to:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

The frontend will be available at `http://localhost:5173`

## Using the Application

### Step 1: Open the Application

Open your browser and go to `http://localhost:5173`

### Step 2: Train the Model

Click on the **"Train Model"** tab to add training data:

#### Option A: Add DDL (Database Schema)

Example DDL to train with:

```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    total_amount DECIMAL(10, 2),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

#### Option B: Add Question-SQL Pairs

Example training pairs:

| Question | SQL |
|----------|-----|
| How many customers do we have? | `SELECT COUNT(*) FROM customers;` |
| Show all orders from today | `SELECT * FROM orders WHERE DATE(order_date) = DATE('now');` |
| What is the total revenue? | `SELECT SUM(total_amount) FROM orders;` |

### Step 3: Ask Questions

Click on the **"Ask Questions"** tab and enter natural language questions:

- "How many customers are there?"
- "Show me the top 10 orders by amount"
- "What is the average order value?"

The app will:
1. Generate the appropriate SQL query
2. Execute it against your SQLite database
3. Display the results in a table

### Step 4: View Training Data

Click on the **"View Training Data"** tab to see all the DDL and question-SQL pairs the model has learned.

## API Endpoints

The backend provides the following REST API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/train/ddl` | Add DDL to training data |
| POST | `/api/train/query` | Add question-SQL pair |
| GET | `/api/training-data` | Retrieve all training data |
| POST | `/api/ask` | Ask question and get SQL + results |
| POST | `/api/execute` | Execute SQL query directly |

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'vanna'`
- **Solution**: Make sure you've activated the virtual environment and installed dependencies:
  ```bash
  pip install -r requirements.txt
  ```

**Problem**: `openai.error.AuthenticationError`
- **Solution**: Check that your DeepSeek API key is correctly set in the `.env` file

**Problem**: Port 5000 already in use
- **Solution**: Change the `FLASK_PORT` in `.env` to a different port (e.g., 5001)

### Frontend Issues

**Problem**: `npm: command not found`
- **Solution**: Install Node.js from https://nodejs.org/

**Problem**: Port 5173 already in use
- **Solution**: The dev server will automatically try the next available port

**Problem**: API calls failing with CORS errors
- **Solution**: Make sure the backend server is running on port 5000

## Building for Production

### Backend

The Flask backend can be deployed using:
- **Gunicorn**: `gunicorn app:app`
- **Docker**: Create a Dockerfile based on Python image
- **Platform**: Heroku, Railway, Render, etc.

### Frontend

Build the frontend for production:

```bash
cd vanna/frontend
npm run build
```

The built files will be in the `dist/` directory and can be served by any static file server.

## Configuration Options

### Environment Variables (Backend)

- `FAISS_PATH`: Path to FAISS vector storage (default: `./data/faiss`)
- `SQLITE_DB_PATH`: Path to SQLite database (default: `./data/database.db`)
- `FLASK_PORT`: Backend server port (default: `5000`)
- `DEEPSEEK_API_KEY`: Your DeepSeek API key (required)
- `DEEPSEEK_BASE_URL`: DeepSeek API base URL (default: `https://api.deepseek.com`)
- `DEEPSEEK_MODEL`: Model to use (default: `deepseek-chat`, can also use `deepseek-coder`)

### Vite Configuration (Frontend)

Edit `vite.config.js` to change:
- Dev server port
- Backend proxy target
- Build options

## Database

By default, the application uses SQLite as the target database. The database file will be created at `backend/data/database.db`.

To use your own existing SQLite database, update the `SQLITE_DB_PATH` in `.env` to point to your database file.

### Switching to Other Databases

To use PostgreSQL, MySQL, or other databases, modify `vanna_config.py`:

```python
# For PostgreSQL
_vanna_instance.connect_to_postgres(
    host='localhost',
    dbname='your_db',
    user='your_user',
    password='your_password',
    port=5432
)
```

## License

This project is created for educational and development purposes.

## Support

For issues related to:
- **Vanna AI**: Visit [Vanna Documentation](https://vanna.ai/docs/)
- **Flask**: Visit [Flask Documentation](https://flask.palletsprojects.com/)
- **React**: Visit [React Documentation](https://react.dev/)

## Credits

Built with:
- [Vanna AI](https://vanna.ai/) - Text-to-SQL using RAG
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [React](https://react.dev/) - UI library
- [Vite](https://vitejs.dev/) - Frontend build tool
- [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search library
- [DeepSeek](https://www.deepseek.com/) - LLM provider (OpenAI-compatible API)
