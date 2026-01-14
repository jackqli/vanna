from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

from vanna_config import get_vanna

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend
logger.info("Flask app initialized with CORS")

# Initialize Vanna
logger.info("Initializing Vanna...")
try:
    vn = get_vanna()
    logger.info("Vanna initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Vanna: {e}")
    logger.error(traceback.format_exc())
    raise

@app.before_request
def log_request():
    """Log incoming requests"""
    logger.info(f"{request.method} {request.path} - Body: {request.get_json(silent=True)}")

@app.after_request
def log_response(response):
    """Log outgoing responses"""
    logger.info(f"Response: {response.status}")
    return response

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return jsonify({'status': 'healthy', 'message': 'Vanna API is running'})

@app.route('/api/train/ddl', methods=['POST'])
def train_ddl():
    """Add DDL to training data"""
    try:
        data = request.get_json()
        ddl = data.get('ddl')
        logger.info(f"Training DDL: {ddl[:100]}..." if ddl and len(ddl) > 100 else f"Training DDL: {ddl}")

        if not ddl:
            logger.warning("DDL training failed: DDL is required")
            return jsonify({'error': 'DDL is required'}), 400

        vn.train(ddl=ddl)
        logger.info("DDL training successful")

        return jsonify({
            'success': True,
            'message': 'DDL added to training data successfully'
        })
    except Exception as e:
        logger.error(f"DDL training failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/train/query', methods=['POST'])
def train_query():
    """Add question-SQL pair to training data"""
    try:
        data = request.get_json()
        question = data.get('question')
        sql = data.get('sql')
        logger.info(f"Training query - Question: {question}, SQL: {sql}")

        if not question or not sql:
            logger.warning("Query training failed: Both question and SQL are required")
            return jsonify({'error': 'Both question and SQL are required'}), 400

        vn.train(question=question, sql=sql)
        logger.info("Query training successful")

        return jsonify({
            'success': True,
            'message': 'Question-SQL pair added to training data successfully'
        })
    except Exception as e:
        logger.error(f"Query training failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/training-data', methods=['GET'])
def get_training_data():
    """Retrieve all training data"""
    try:
        logger.info("Retrieving training data")
        training_data = vn.get_training_data()
        logger.info(f"Retrieved {len(training_data) if training_data else 0} training records")

        return jsonify({
            'success': True,
            'data': training_data
        })
    except Exception as e:
        logger.error(f"Failed to retrieve training data: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask a question and get SQL + results"""
    try:
        data = request.get_json()
        question = data.get('question')
        logger.info(f"Ask question: {question}")

        if not question:
            logger.warning("Ask failed: Question is required")
            return jsonify({'error': 'Question is required'}), 400

        # Generate SQL from question
        logger.debug("Generating SQL from question...")
        sql = vn.generate_sql(question=question)
        logger.info(f"Generated SQL: {sql}")

        # Execute the SQL and get results
        logger.debug("Executing SQL...")
        df = vn.run_sql(sql=sql)
        logger.info(f"SQL execution returned {len(df) if df is not None else 0} rows")

        # Convert DataFrame to dict for JSON serialization
        results = df.to_dict('records') if df is not None else []

        return jsonify({
            'success': True,
            'question': question,
            'sql': sql,
            'results': results,
            'columns': list(df.columns) if df is not None else []
        })
    except Exception as e:
        logger.error(f"Ask question failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/execute', methods=['POST'])
def execute_sql():
    """Execute SQL query directly"""
    try:
        data = request.get_json()
        sql = data.get('sql')
        logger.info(f"Execute SQL: {sql}")

        if not sql:
            logger.warning("Execute failed: SQL is required")
            return jsonify({'error': 'SQL is required'}), 400

        # Execute the SQL
        logger.debug("Executing SQL...")
        df = vn.run_sql(sql=sql)
        logger.info(f"SQL execution returned {len(df) if df is not None else 0} rows")

        # Convert DataFrame to dict for JSON serialization
        results = df.to_dict('records') if df is not None else []

        return jsonify({
            'success': True,
            'sql': sql,
            'results': results,
            'columns': list(df.columns) if df is not None else []
        })
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
