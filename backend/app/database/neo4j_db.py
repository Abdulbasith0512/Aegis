import logging
from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver, Session
from app.config.loader import settings

logger = logging.getLogger(__name__)

class MockNeo4jSession:
    """
    Mock session fallback to simulate Neo4j Cypher queries in testing
    and dev environments when Neo4j container database is offline.
    """
    def run(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Any:
        # Returns simple mock cursors that return lists
        class MockResult:
            def data(self) -> List[Dict[str, Any]]:
                return []
            def values(self) -> List[Any]:
                return []
        return MockResult()

    def close(self) -> None:
        pass

    def __enter__(self) -> "MockNeo4jSession":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

class Neo4jDatabaseManager:
    """
    Manages client driver lifecycles and query pools for Neo4j.
    """
    _instance = None

    def __new__(cls) -> "Neo4jDatabaseManager":
        if cls._instance is None:
            cls._instance = super(Neo4jDatabaseManager, cls).__new__(cls)
            cls._instance._init_driver()
        return cls._instance

    def _init_driver(self) -> None:
        self.driver: Optional[Driver] = None
        self.use_mock = False
        
        try:
            # Setup connections to standard URI configurations
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # Verify connectivity immediately
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j graph registry.")
        except Exception as e:
            logger.warning(
                f"Neo4j database failed connection check: {e}. "
                "Switching database instance to MockNeo4jSession mode."
            )
            self.use_mock = True

    def get_session(self) -> Any:
        """
        Retrieves a session execution handle.
        """
        if self.use_mock or not self.driver:
            return MockNeo4jSession()
        
        try:
            return self.driver.session()
        except Exception as e:
            logger.error(f"Error instantiating active session: {e}. Falling back to mock session.")
            return MockNeo4jSession()

    def close(self) -> None:
        """Frees the connection driver socket registry."""
        if self.driver:
            self.driver.close()
