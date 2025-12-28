"""
MatchDataIndexer - Application Layer

Use Case orchestrating match data indexing for RAG.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from src.domain.ports.vector_store_port import VectorStorePort


@dataclass
class IndexingResult:
    """Result of indexing match data."""
    match_id: str
    documents_indexed: int
    status: str


class MatchDataIndexer:
    """
    Use Case: Index match data.
    
    Prepares match context (events, metrics, insights) and persists for RAG.
    """
    
    def __init__(self, vector_store: VectorStorePort):
        """
        Initialize with vector store port.
        """
        self.vector_store = vector_store
    
    def execute(
        self, 
        match_id: str,
        match_events: Optional[List[Dict[str, Any]]] = None,
        match_metrics: Optional[Dict[str, Any]] = None,
        match_summary: Optional[str] = None
    ) -> IndexingResult:
        """
        Index match data for RAG retrieval.
        
        Args:
            match_id: Match identifier
            match_events: List of match events
            match_metrics: Dictionary of calculated metrics
            match_summary: Optional text summary
            
        Returns:
            IndexingResult
        """
        documents = []
        metadatas = []
        
        # Index match summary
        if match_summary:
            documents.append(f"Match Summary: {match_summary}")
            metadatas.append({
                "match_id": match_id,
                "type": "summary",
                "source": "summary"
            })
        
        # Index key events
        if match_events:
            for event in match_events:
                event_text = self._format_event(event)
                if event_text:
                    documents.append(event_text)
                    metadatas.append({
                        "match_id": match_id,
                        "type": "event",
                        "event_type": event.get("type", "unknown"),
                        "minute": event.get("minute", 0)
                    })
        
        # Index metrics
        if match_metrics:
            metrics_text = self._format_metrics(match_metrics)
            for text in metrics_text:
                documents.append(text)
                metadatas.append({
                    "match_id": match_id,
                    "type": "metrics",
                    "source": "tactical_analysis"
                })
        
        if not documents:
            return IndexingResult(
                match_id=match_id,
                documents_indexed=0,
                status="no_documents"
            )
        
        # Index documents
        ids = self.vector_store.add_documents(documents, metadatas)
        
        return IndexingResult(
            match_id=match_id,
            documents_indexed=len(ids),
            status="success"
        )
    
    def _format_event(self, event: Dict[str, Any]) -> str:
        """Format a single event for indexing."""
        event_type = event.get("type", "").lower()
        significant_events = {"goal", "shot", "assist", "red_card", "yellow_card", "substitution"}
        
        if event_type not in significant_events:
            return ""
        
        player = event.get("player", "Unknown")
        team = event.get("team", "Unknown")
        minute = event.get("minute", 0)
        
        return f"Minute {minute}: {player} ({team}) - {event_type.replace('_', ' ').title()}"
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> List[str]:
        """Format metrics into indexable text chunks."""
        texts = []
        # Logic kept identical to original
        if "home_ppda" in metrics or "away_ppda" in metrics:
            home = metrics.get("home_ppda", 0)
            away = metrics.get("away_ppda", 0)
            texts.append(f"Pressing Intensity: Home PPDA {home:.2f}, Away PPDA {away:.2f}.")
            
        if "total_distance" in metrics:
            texts.append(f"Physical Output: {metrics['total_distance']:.1f} km covered.")
            
        if "possession" in metrics:
            home = metrics["possession"].get("home", 50)
            texts.append(f"Possession: Home {home}%, Away {100-home}%.")
            
        if "total_xt" in metrics:
            texts.append(f"Expected Threat: {metrics['total_xt']:.4f} xT.")
            
        return texts
