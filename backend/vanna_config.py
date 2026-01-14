import os
import pickle
import uuid
import sqlite3
import logging
import numpy as np
import faiss
from typing import List
from openai import OpenAI
from vanna.base import VannaBase
from vanna.openai import OpenAI_Chat

logger = logging.getLogger(__name__)

class FAISS_VectorStore(VannaBase):
    def __init__(self, config=None):
        logger.debug("Initializing FAISS_VectorStore")
        VannaBase.__init__(self, config=config)
        if config is None:
            config = {}

        self.path = config.get('path', './data/faiss')
        os.makedirs(self.path, exist_ok=True)
        logger.debug(f"FAISS path: {self.path}")

        self.index_path = os.path.join(self.path, 'faiss.index')
        self.metadata_path = os.path.join(self.path, 'metadata.pkl')
        self.dimension_path = os.path.join(self.path, 'dimension.txt')

        # Embedding dimension - will be auto-detected from first embedding if not set
        self.dimension = config.get('embedding_dimension', None)

        # Initialize embedding client (using OpenAI-compatible API)
        self.embedding_api_key = config.get('embedding_api_key') or config.get('api_key')
        self.embedding_base_url = config.get('embedding_base_url', 'https://api.openai.com/v1')
        self.embedding_model = config.get('embedding_model', 'text-embedding-ada-002')
        logger.debug(f"Embedding config - base_url: {self.embedding_base_url}, model: {self.embedding_model}")

        # Initialize or load FAISS index
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            logger.info(f"Loading existing FAISS index from {self.index_path}")
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            # Load saved dimension
            if os.path.exists(self.dimension_path):
                with open(self.dimension_path, 'r') as f:
                    self.dimension = int(f.read().strip())
            else:
                self.dimension = self.index.d
            logger.info(f"Loaded {len(self.metadata)} records from FAISS index (dimension: {self.dimension})")
        else:
            logger.info("No existing FAISS index found, will create on first embedding")
            self.index = None
            self.metadata = []

    def _init_index(self, dimension: int):
        """Initialize FAISS index with the given dimension"""
        logger.info(f"Initializing FAISS index with dimension {dimension}")
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        # Save dimension for future reference
        with open(self.dimension_path, 'w') as f:
            f.write(str(dimension))

    def generate_embedding(self, text: str, **kwargs) -> List[float]:
        """Generate embedding for text using OpenAI-compatible API"""
        logger.debug(f"Generating embedding for text: {text[:50]}...")
        client = OpenAI(
            api_key=self.embedding_api_key,
            base_url=self.embedding_base_url
        )
        response = client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        embedding = response.data[0].embedding
        logger.debug(f"Embedding generated, dimension: {len(embedding)}")
        return embedding

    def add_embeddings(self, embeddings: List[float], metadata: dict):
        """Add embeddings to FAISS index"""
        # Auto-initialize index on first embedding
        if self.index is None:
            self._init_index(len(embeddings))

        # Verify dimension matches
        if len(embeddings) != self.dimension:
            raise ValueError(f"Embedding dimension {len(embeddings)} does not match index dimension {self.dimension}")

        logger.debug(f"Adding embedding to FAISS index, metadata type: {metadata.get('type')}")
        embedding_array = np.array([embeddings], dtype=np.float32)
        self.index.add(embedding_array)
        self.metadata.append(metadata)
        self._save()
        logger.debug(f"FAISS index now has {self.index.ntotal} vectors")

    def get_similar_embeddings(self, embedding: List[float], n: int = 5):
        """Retrieve similar embeddings from FAISS index"""
        if self.index is None or self.index.ntotal == 0:
            logger.debug("FAISS index is empty or not initialized, returning no results")
            return []

        logger.debug(f"Searching FAISS index for {n} similar vectors")
        embedding_array = np.array([embedding], dtype=np.float32)
        distances, indices = self.index.search(embedding_array, min(n, self.index.ntotal))

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        logger.debug(f"Found {len(results)} similar vectors")
        return results

    def _save(self):
        """Save FAISS index and metadata to disk"""
        logger.debug(f"Saving FAISS index to {self.index_path}")
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        logger.debug("FAISS index saved")

    def add_ddl(self, ddl: str, **kwargs) -> str:
        """Add DDL to training data"""
        logger.info(f"Adding DDL: {ddl[:100]}...")
        id = str(uuid.uuid4())
        embedding = self.generate_embedding(ddl)
        self.add_embeddings(embedding, {
            'id': id,
            'type': 'ddl',
            'content': ddl
        })
        logger.info(f"DDL added with id: {id}")
        return id

    def add_documentation(self, documentation: str, **kwargs) -> str:
        """Add documentation to training data"""
        logger.info(f"Adding documentation: {documentation[:100]}...")
        id = str(uuid.uuid4())
        embedding = self.generate_embedding(documentation)
        self.add_embeddings(embedding, {
            'id': id,
            'type': 'documentation',
            'content': documentation
        })
        logger.info(f"Documentation added with id: {id}")
        return id

    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        """Add question-SQL pair to training data"""
        logger.info(f"Adding question-SQL pair - Question: {question}")
        id = str(uuid.uuid4())
        embedding = self.generate_embedding(question)
        self.add_embeddings(embedding, {
            'id': id,
            'type': 'question_sql',
            'question': question,
            'sql': sql
        })
        logger.info(f"Question-SQL pair added with id: {id}")
        return id

    def get_related_ddl(self, question: str, **kwargs) -> List[str]:
        """Get DDL related to a question"""
        logger.debug(f"Getting related DDL for question: {question}")
        embedding = self.generate_embedding(question)
        results = self.get_similar_embeddings(embedding, n=10)
        ddl_results = [r['content'] for r in results if r.get('type') == 'ddl']
        logger.debug(f"Found {len(ddl_results)} related DDL records")
        return ddl_results

    def get_related_documentation(self, question: str, **kwargs) -> List[str]:
        """Get documentation related to a question"""
        logger.debug(f"Getting related documentation for question: {question}")
        embedding = self.generate_embedding(question)
        results = self.get_similar_embeddings(embedding, n=10)
        doc_results = [r['content'] for r in results if r.get('type') == 'documentation']
        logger.debug(f"Found {len(doc_results)} related documentation records")
        return doc_results

    def get_similar_question_sql(self, question: str, **kwargs) -> List[dict]:
        """Get similar question-SQL pairs"""
        logger.debug(f"Getting similar question-SQL pairs for: {question}")
        embedding = self.generate_embedding(question)
        results = self.get_similar_embeddings(embedding, n=10)
        sql_results = [
            {'question': r['question'], 'sql': r['sql']}
            for r in results if r.get('type') == 'question_sql'
        ]
        logger.debug(f"Found {len(sql_results)} similar question-SQL pairs")
        return sql_results

    def get_training_data(self, **kwargs):
        """Get all training data"""
        logger.debug(f"Getting all training data, count: {len(self.metadata)}")
        return self.metadata

    def remove_training_data(self, id: str, **kwargs):
        """Remove training data by id"""
        logger.warning(f"remove_training_data called for id {id}, but FAISS removal is not implemented")
        # FAISS doesn't support easy removal, would need to rebuild index
        pass

class VannaConfig(FAISS_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        logger.debug("Initializing VannaConfig")
        # Extract client from config if present (OpenAI_Chat expects it as separate param)
        client = config.pop('client', None) if config else None
        FAISS_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, client=client, config=config)
        logger.debug("VannaConfig initialized")

# Global Vanna instance
_vanna_instance = None

def init_vanna():
    """Initialize Vanna with FAISS, SQLite, and DeepSeek API"""
    global _vanna_instance
    logger.info("init_vanna called")

    if _vanna_instance is not None:
        logger.debug("Returning existing Vanna instance")
        return _vanna_instance

    # Get configuration from environment variables
    base_dir = os.path.dirname(os.path.abspath(__file__))
    faiss_path = os.getenv('FAISS_PATH', os.path.join(base_dir, 'data', 'faiss'))
    sqlite_path = os.getenv('SQLITE_DB_PATH', os.path.join(base_dir, 'data', 'database.db'))

    # DeepSeek configuration (for chat/LLM)
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    deepseek_model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

    # Tongyi Qwen embedding configuration (separate from chat model)
    embedding_api_key = os.getenv('EMBEDDING_API_KEY')
    embedding_base_url = os.getenv('EMBEDDING_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-v3')

    # Convert to absolute paths
    faiss_path = os.path.abspath(faiss_path)
    sqlite_path = os.path.abspath(sqlite_path)

    logger.info(f"Configuration:")
    logger.info(f"  FAISS path: {faiss_path}")
    logger.info(f"  SQLite path: {sqlite_path}")
    logger.info(f"  DeepSeek base URL: {deepseek_base_url}")
    logger.info(f"  DeepSeek model: {deepseek_model}")
    logger.info(f"  DeepSeek API key: {'***' + deepseek_api_key[-4:] if deepseek_api_key else 'NOT SET'}")
    logger.info(f"  Embedding base URL: {embedding_base_url}")
    logger.info(f"  Embedding model: {embedding_model}")
    logger.info(f"  Embedding API key: {'***' + embedding_api_key[-4:] if embedding_api_key else 'NOT SET'}")

    # Ensure data directory exists
    logger.debug(f"Creating directories: {faiss_path}, {os.path.dirname(sqlite_path)}")
    os.makedirs(faiss_path, exist_ok=True)
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)

    # Create empty SQLite database if it doesn't exist
    if not os.path.exists(sqlite_path):
        logger.info(f"Creating empty SQLite database at {sqlite_path}")
        conn = sqlite3.connect(sqlite_path)
        conn.close()
    else:
        logger.info(f"SQLite database already exists at {sqlite_path}")

    # Create OpenAI client with DeepSeek base URL
    logger.debug("Creating OpenAI client for DeepSeek")
    deepseek_client = OpenAI(
        api_key=deepseek_api_key,
        base_url=deepseek_base_url
    )

    # Initialize Vanna with DeepSeek configuration
    logger.info("Creating VannaConfig instance")
    _vanna_instance = VannaConfig(config={
        'path': faiss_path,
        'model': deepseek_model,
        'client': deepseek_client,
        # Embedding configuration (Tongyi Qwen)
        'embedding_api_key': embedding_api_key,
        'embedding_base_url': embedding_base_url,
        'embedding_model': embedding_model,
    })

    # Connect to SQLite database
    logger.info(f"Connecting to SQLite database: {sqlite_path}")
    _vanna_instance.connect_to_sqlite(sqlite_path)
    logger.info("Successfully connected to SQLite database")

    return _vanna_instance

def get_vanna():
    """Get the Vanna instance, initializing if necessary"""
    if _vanna_instance is None:
        logger.debug("Vanna instance not initialized, calling init_vanna")
        return init_vanna()
    return _vanna_instance
