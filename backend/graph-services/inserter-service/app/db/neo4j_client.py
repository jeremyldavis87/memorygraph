import asyncio
import time
from typing import List, Dict, Any, Optional
from neo4j import AsyncGraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jClient:
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

    async def insert_triples(self, triples: List[Dict[str, Any]], 
                           note_id: Optional[int] = None, 
                           user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Insert knowledge graph triples into Neo4j.
        """
        start_time = time.time()
        inserted_count = 0
        merged_count = 0
        errors = []
        
        async with self.driver.session(database=self.database) as session:
            for triple in triples:
                try:
                    # Create or merge nodes and relationships
                    if triple.get("relationship_type") == "INSTANCE_OF":
                        # This is an entity definition
                        result = await self._create_entity(session, triple, note_id, user_id)
                        if result["action"] == "created":
                            inserted_count += 1
                        else:
                            merged_count += 1
                    else:
                        # This is a relationship
                        result = await self._create_relationship(session, triple, note_id, user_id)
                        if result["action"] == "created":
                            inserted_count += 1
                        else:
                            merged_count += 1
                            
                except Exception as e:
                    errors.append(f"Failed to insert triple {triple}: {str(e)}")
        
        processing_time = time.time() - start_time
        
        return {
            "inserted_count": inserted_count,
            "merged_count": merged_count,
            "errors": errors,
            "processing_time": processing_time
        }

    async def bulk_insert_triples(self, triples: List[Dict[str, Any]], 
                                 note_id: Optional[int] = None, 
                                 user_id: Optional[int] = None,
                                 batch_size: int = 100) -> Dict[str, Any]:
        """
        Insert knowledge graph triples in batches for better performance.
        """
        start_time = time.time()
        inserted_count = 0
        merged_count = 0
        errors = []
        
        # Process in batches
        for i in range(0, len(triples), batch_size):
            batch = triples[i:i + batch_size]
            
            async with self.driver.session(database=self.database) as session:
                try:
                    # Use UNWIND for batch processing
                    result = await session.run("""
                        UNWIND $triples AS triple
                        CALL {
                            WITH triple
                            // Create or merge subject node
                            MERGE (s:Entity {name: triple.subject})
                            SET s.type = triple.entity_type,
                                s.properties = triple.properties,
                                s.updated_at = datetime(),
                                s.note_id = $note_id,
                                s.user_id = $user_id
                            
                            // Create or merge object node
                            MERGE (o:Entity {name: triple.object})
                            SET o.updated_at = datetime(),
                                o.note_id = $note_id,
                                o.user_id = $user_id
                            
                            // Create relationship
                            WITH s, o, triple
                            CALL apoc.create.relationship(s, triple.predicate, {
                                confidence: triple.confidence,
                                properties: triple.properties,
                                created_at: datetime(),
                                note_id: $note_id,
                                user_id: $user_id
                            }, o) YIELD rel
                            RETURN count(rel) as rel_count
                        }
                        RETURN sum(rel_count) as total_relationships
                    """, {
                        "triples": batch,
                        "note_id": note_id,
                        "user_id": user_id
                    })
                    
                    record = await result.single()
                    inserted_count += record["total_relationships"] or 0
                    
                except Exception as e:
                    errors.append(f"Batch {i//batch_size + 1} failed: {str(e)}")
        
        processing_time = time.time() - start_time
        
        return {
            "inserted_count": inserted_count,
            "merged_count": 0,  # Bulk operations don't track merges separately
            "errors": errors,
            "processing_time": processing_time
        }

    async def merge_entity(self, name: str, entity_type: str, 
                          properties: Dict[str, Any], strategy: str = "merge") -> Dict[str, Any]:
        """
        Merge or create an entity in the knowledge graph.
        """
        async with self.driver.session(database=self.database) as session:
            if strategy == "merge":
                # Merge existing entity or create new one
                result = await session.run("""
                    MERGE (e:Entity {name: $name})
                    SET e.type = $entity_type,
                        e.properties = $properties,
                        e.updated_at = datetime()
                    RETURN e, 
                           CASE WHEN e.created_at IS NULL THEN 'created' ELSE 'updated' END as action
                """, {
                    "name": name,
                    "entity_type": entity_type,
                    "properties": properties
                })
                
                record = await result.single()
                return {
                    "entity_id": str(record["e"].id),
                    "action": record["action"],
                    "properties": dict(record["e"])
                }
                
            elif strategy == "create":
                # Only create if doesn't exist
                result = await session.run("""
                    CREATE (e:Entity {
                        name: $name,
                        type: $entity_type,
                        properties: $properties,
                        created_at: datetime()
                    })
                    RETURN e
                """, {
                    "name": name,
                    "entity_type": entity_type,
                    "properties": properties
                })
                
                record = await result.single()
                return {
                    "entity_id": str(record["e"].id),
                    "action": "created",
                    "properties": dict(record["e"])
                }
                
            else:  # update
                # Only update if exists
                result = await session.run("""
                    MATCH (e:Entity {name: $name})
                    SET e.type = $entity_type,
                        e.properties = $properties,
                        e.updated_at = datetime()
                    RETURN e
                """, {
                    "name": name,
                    "entity_type": entity_type,
                    "properties": properties
                })
                
                record = await result.single()
                if record:
                    return {
                        "entity_id": str(record["e"].id),
                        "action": "updated",
                        "properties": dict(record["e"])
                    }
                else:
                    raise Exception("Entity not found for update")

    async def get_entity(self, entity_name: str) -> Dict[str, Any]:
        """
        Get an entity and its relationships from the knowledge graph.
        """
        async with self.driver.session(database=self.database) as session:
            result = await session.run("""
                MATCH (e:Entity {name: $name})
                OPTIONAL MATCH (e)-[r]-(related)
                RETURN e, collect({
                    relationship: type(r),
                    direction: CASE WHEN startNode(r) = e THEN 'outgoing' ELSE 'incoming' END,
                    target: CASE WHEN startNode(r) = e THEN related.name ELSE e.name END,
                    properties: properties(r)
                }) as relationships
            """, {"name": entity_name})
            
            record = await result.single()
            if not record:
                raise Exception("Entity not found")
            
            return {
                "entity": dict(record["e"]),
                "relationships": record["relationships"]
            }

    async def delete_entity(self, entity_name: str) -> int:
        """
        Delete an entity and its relationships from the knowledge graph.
        """
        async with self.driver.session(database=self.database) as session:
            result = await session.run("""
                MATCH (e:Entity {name: $name})
                OPTIONAL MATCH (e)-[r]-()
                DELETE r, e
                RETURN count(r) as deleted_relationships
            """, {"name": entity_name})
            
            record = await result.single()
            return record["deleted_relationships"]

    async def get_graph_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.
        """
        async with self.driver.session(database=self.database) as session:
            # Get node count
            node_result = await session.run("MATCH (n) RETURN count(n) as node_count")
            node_record = await node_result.single()
            
            # Get relationship count
            rel_result = await session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_record = await rel_result.single()
            
            # Get entity type distribution
            type_result = await session.run("""
                MATCH (e:Entity)
                RETURN e.type as entity_type, count(e) as count
                ORDER BY count DESC
            """)
            entity_types = [dict(record) for record in await type_result.data()]
            
            # Get relationship type distribution
            rel_type_result = await session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
            """)
            relationship_types = [dict(record) for record in await rel_type_result.data()]
            
            return {
                "total_nodes": node_record["node_count"],
                "total_relationships": rel_record["rel_count"],
                "entity_types": entity_types,
                "relationship_types": relationship_types
            }

    async def _create_entity(self, session, triple: Dict[str, Any], 
                           note_id: Optional[int], user_id: Optional[int]) -> Dict[str, str]:
        """Create or merge an entity node."""
        result = await session.run("""
            MERGE (e:Entity {name: $subject})
            SET e.type = $entity_type,
                e.properties = $properties,
                e.updated_at = datetime(),
                e.note_id = $note_id,
                e.user_id = $user_id
            RETURN e,
                   CASE WHEN e.created_at IS NULL THEN 'created' ELSE 'merged' END as action
        """, {
            "subject": triple["subject"],
            "entity_type": triple["entity_type"],
            "properties": triple.get("properties", {}),
            "note_id": note_id,
            "user_id": user_id
        })
        
        record = await result.single()
        return {"action": record["action"]}

    async def _create_relationship(self, session, triple: Dict[str, Any], 
                                note_id: Optional[int], user_id: Optional[int]) -> Dict[str, str]:
        """Create a relationship between entities."""
        result = await session.run("""
            MATCH (s:Entity {name: $subject})
            MATCH (o:Entity {name: $object})
            MERGE (s)-[r:RELATIONSHIP {type: $predicate}]->(o)
            SET r.confidence = $confidence,
                r.properties = $properties,
                r.created_at = datetime(),
                r.note_id = $note_id,
                r.user_id = $user_id
            RETURN r,
                   CASE WHEN r.created_at = datetime() THEN 'created' ELSE 'merged' END as action
        """, {
            "subject": triple["subject"],
            "object": triple["object"],
            "predicate": triple["predicate"],
            "confidence": triple.get("confidence", 0.5),
            "properties": triple.get("properties", {}),
            "note_id": note_id,
            "user_id": user_id
        })
        
        record = await result.single()
        return {"action": record["action"]}

    async def close(self):
        """Close the Neo4j driver connection."""
        await self.driver.close()
