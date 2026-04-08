
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from src.core.config import get_settings

def get_qdrant_client( ) -> QdrantClient:
    
    return QdrantClient(url=get_settings().QDRANT_URL)

def retrieve_chunks_by_url(url: str) -> List[str]:
    """
     Retrieves text chunks from Qdrant based on a given URL
    """
    client = get_qdrant_client()
    settings = get_settings()
    
 
    search_result = client.scroll(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        scroll_filter=Filter(
            must=[
             
                FieldCondition(key="metadata.url", match=MatchValue(value=url))
            ]
        ),
        limit=100,
        with_payload=True,
        with_vectors=False 
    )
    
    chunks = []
   
    points = search_result[0] 
    
    for point in points:
       
        if point.payload and "page_content" in point.payload:
            chunks.append(point.payload["page_content"])
            
    return chunks
