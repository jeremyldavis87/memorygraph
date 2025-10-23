import time
from typing import List, Dict, Any, Optional
from neo4j import AsyncGraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class GraphQueries:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        
        # Initialize driver
        self.driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password)
        )

    async def test_connection(self):
        """Test the Neo4j connection."""
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run("RETURN 1 as test")
                record = await result.single()
                return record["test"] == 1
        except Exception as e:
            raise Exception(f"Neo4j connection failed: {str(e)}")

    async def execute_query(self, query: str, limit: int = 50, 
                          user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a custom Cypher query against the knowledge graph.
        """
        start_time = time.time()
        
        # Add user filter if provided
        if user_id:
            # Add user filtering to the query
            query = f"""
            {query}
            {'WHERE' if 'WHERE' not in query.upper() else 'AND'} 
            (n.user_id = $user_id OR n.user_id IS NULL)
            """
        
        async with self.driver.session(database=self.database) as session:
            result = await session.run(query, {"user_id": user_id})
            records = await result.data()
            
            # Limit results
            limited_records = records[:limit]
            
            query_time = time.time() - start_time
            
            return {
                "results": limited_records,
                "query_time": query_time,
                "result_count": len(limited_records)
            }

    async def get_related_entities(self, entity_name: str, max_depth: int = 2, 
                                  limit: int = 50, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get entities related to a specific entity within a certain depth.
        """
        start_time = time.time()
        
        async with self.driver.session(database=self.database) as session:
            # Get the entity and its relationships
            result = await session.run("""
                MATCH (e:Entity {name: $entity_name})
                OPTIONAL MATCH path = (e)-[r*1..$max_depth]-(related:Entity)
                WHERE (related.user_id = $user_id OR related.user_id IS NULL OR $user_id IS NULL)
                RETURN e as entity,
                       collect(DISTINCT {
                           entity: related,
                           path: [rel in relationships(path) | {
                               type: type(rel),
                               properties: properties(rel)
                           }],
                           distance: length(path)
                       }) as related_entities
                LIMIT $limit
            """, {
                "entity_name": entity_name,
                "max_depth": max_depth,
                "user_id": user_id,
                "limit": limit
            })
            
            record = await result.single()
            if not record:
                raise Exception("Entity not found")
            
            # Extract relationships
            relationships = []
            for rel_data in record["related_entities"]:
                for rel in rel_data["path"]:
                    relationships.append({
                        "type": rel["type"],
                        "properties": rel["properties"]
                    })
            
            query_time = time.time() - start_time
            
            return {
                "entity": dict(record["entity"]),
                "related_entities": [rel["entity"] for rel in record["related_entities"]],
                "relationships": relationships,
                "query_time": query_time
            }

    async def get_graph_context(self, note_id: Optional[int] = None, 
                               entity_names: List[str] = [], max_depth: int = 2,
                               limit: int = 50, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get contextual information for a note or set of entities.
        """
        start_time = time.time()
        
        async with self.driver.session(database=self.database) as session:
            if note_id:
                # Get context for a specific note
                result = await session.run("""
                    MATCH (n:Note {id: $note_id})
                    OPTIONAL MATCH (n)-[:MENTIONED_IN]-(e:Entity)
                    OPTIONAL MATCH path = (e)-[r*1..$max_depth]-(related:Entity)
                    WHERE (related.user_id = $user_id OR related.user_id IS NULL OR $user_id IS NULL)
                    RETURN collect(DISTINCT e) as entities,
                           collect(DISTINCT {
                               from: startNode(rel),
                               to: endNode(rel),
                               type: type(rel),
                               properties: properties(rel)
                           }) as relationships
                    LIMIT $limit
                """, {
                    "note_id": note_id,
                    "max_depth": max_depth,
                    "user_id": user_id,
                    "limit": limit
                })
            else:
                # Get context for specific entities
                result = await session.run("""
                    MATCH (e:Entity)
                    WHERE e.name IN $entity_names
                    OPTIONAL MATCH path = (e)-[r*1..$max_depth]-(related:Entity)
                    WHERE (related.user_id = $user_id OR related.user_id IS NULL OR $user_id IS NULL)
                    RETURN collect(DISTINCT e) as entities,
                           collect(DISTINCT {
                               from: startNode(rel),
                               to: endNode(rel),
                               type: type(rel),
                               properties: properties(rel)
                           }) as relationships
                    LIMIT $limit
                """, {
                    "entity_names": entity_names,
                    "max_depth": max_depth,
                    "user_id": user_id,
                    "limit": limit
                })
            
            record = await result.single()
            entities = [dict(entity) for entity in record["entities"]]
            relationships = record["relationships"]
            
            # Generate context summary
            context_summary = self._generate_context_summary(entities, relationships)
            
            query_time = time.time() - start_time
            
            return {
                "entities": entities,
                "relationships": relationships,
                "context_summary": context_summary,
                "query_time": query_time
            }

    async def get_entity_details(self, entity_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific entity.
        """
        async with self.driver.session(database=self.database) as session:
            result = await session.run("""
                MATCH (e:Entity {name: $entity_name})
                OPTIONAL MATCH (e)-[r]-(related)
                RETURN e as entity,
                       collect({
                           relationship: type(r),
                           direction: CASE WHEN startNode(r) = e THEN 'outgoing' ELSE 'incoming' END,
                           target: CASE WHEN startNode(r) = e THEN related.name ELSE e.name END,
                           properties: properties(r)
                       }) as relationships,
                       count(r) as relationship_count
            """, {"entity_name": entity_name})
            
            record = await result.single()
            if not record:
                raise Exception("Entity not found")
            
            return {
                "entity": dict(record["entity"]),
                "relationships": record["relationships"],
                "relationship_count": record["relationship_count"]
            }

    async def search_entities(self, search_term: str, limit: int = 20) -> Dict[str, Any]:
        """
        Search for entities by name or properties.
        """
        async with self.driver.session(database=self.database) as session:
            result = await session.run("""
                MATCH (e:Entity)
                WHERE e.name CONTAINS $search_term 
                   OR any(prop IN keys(e.properties) WHERE e.properties[prop] CONTAINS $search_term)
                RETURN e as entity,
                       CASE 
                           WHEN e.name CONTAINS $search_term THEN 1.0
                           ELSE 0.5
                       END as relevance_score
                ORDER BY relevance_score DESC, e.name
                LIMIT $limit
            """, {
                "search_term": search_term,
                "limit": limit
            })
            
            records = await result.data()
            return {
                "results": records,
                "count": len(records)
            }

    async def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.
        """
        async with self.driver.session(database=self.database) as session:
            # Get basic stats
            stats_result = await session.run("""
                MATCH (n)
                RETURN count(n) as total_nodes,
                       count(CASE WHEN n:Entity THEN 1 END) as entity_count,
                       count(CASE WHEN n:Note THEN 1 END) as note_count
            """)
            stats_record = await stats_result.single()
            
            # Get relationship stats
            rel_result = await session.run("""
                MATCH ()-[r]->()
                RETURN count(r) as total_relationships,
                       count(DISTINCT type(r)) as relationship_types
            """)
            rel_record = await rel_result.single()
            
            # Get entity type distribution
            type_result = await session.run("""
                MATCH (e:Entity)
                RETURN e.type as entity_type, count(e) as count
                ORDER BY count DESC
            """)
            entity_types = [dict(record) for record in await type_result.data()]
            
            return {
                "total_nodes": stats_record["total_nodes"],
                "entity_count": stats_record["entity_count"],
                "note_count": stats_record["note_count"],
                "total_relationships": rel_record["total_relationships"],
                "relationship_types": rel_record["relationship_types"],
                "entity_type_distribution": entity_types
            }

    async def get_recommendations(self, entity_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get recommendations based on graph structure and relationships.
        """
        async with self.driver.session(database=self.database) as session:
            # Find entities that are connected through common relationships
            result = await session.run("""
                MATCH (e:Entity {name: $entity_name})-[r1]-(common)-[r2]-(recommended:Entity)
                WHERE recommended <> e
                WITH recommended, count(common) as common_connections, 
                     collect(DISTINCT type(r1)) as relationship_types
                RETURN recommended as entity,
                       common_connections,
                       relationship_types,
                       (common_connections * 1.0 / count(*)) as recommendation_score
                ORDER BY recommendation_score DESC, common_connections DESC
                LIMIT $limit
            """, {
                "entity_name": entity_name,
                "limit": limit
            })
            
            records = await result.data()
            return {
                "recommendations": records,
                "count": len(records)
            }

    def _generate_context_summary(self, entities: List[Dict[str, Any]], 
                                relationships: List[Dict[str, Any]]) -> str:
        """
        Generate a human-readable summary of the graph context.
        """
        if not entities:
            return "No entities found in context."
        
        # Group entities by type
        entity_types = {}
        for entity in entities:
            entity_type = entity.get("type", "Unknown")
            if entity_type not in entity_types:
                entity_types[entity_type] = []
            entity_types[entity_type].append(entity.get("name", "Unknown"))
        
        # Create summary
        summary_parts = []
        for entity_type, names in entity_types.items():
            if len(names) == 1:
                summary_parts.append(f"1 {entity_type}: {names[0]}")
            else:
                summary_parts.append(f"{len(names)} {entity_type}s: {', '.join(names[:3])}{'...' if len(names) > 3 else ''}")
        
        relationship_count = len(relationships)
        if relationship_count > 0:
            summary_parts.append(f"{relationship_count} relationships")
        
        return "Context includes: " + "; ".join(summary_parts)

    async def close(self):
        """Close the Neo4j driver connection."""
        await self.driver.close()
