"""
Index Match Data Use Case - Application Layer

Orchestrates embedding and storing match data for RAG retrieval.
"""
from dataclasses import dataclass
from typing import List, Dict, Any

from src.domain.ports.vector_store_port import VectorStorePort


@dataclass
class IndexingResult:
    """Result of indexing match data."""
    match_id: str
    documents_indexed: int
    status: str


class IndexMatchDataUseCase:
    """
    Use case for indexing match data into vector store.
    
    Prepares match context (events, metrics, insights) for RAG
    so the AI can retrieve relevant information during analysis.
    """
    
    def __init__(self, vector_store: VectorStorePort):
        """
        Initialize use case.
        
        Args:
            vector_store: Port for vector storage operations
        """
        self.vector_store = vector_store
    
    def execute(
        self, 
        match_id: str,
        match_events: List[Dict[str, Any]] = None,
        match_metrics: Dict[str, Any] = None,
        match_summary: str = None
    ) -> IndexingResult:
        """
        Index match data for RAG retrieval.
        
        Creates embeddings for:
        - Match summary
        - Key events (goals, assists, cards)
        - Tactical metrics (PPDA, pitch control snapshots)
        
        Args:
            match_id: Match identifier
            match_events: List of match events
            match_metrics: Dictionary of calculated metrics
            match_summary: Optional text summary of the match
            
        Returns:
            IndexingResult with count of indexed documents
        """
        documents = []
        metadatas = []
        
        # Index match summary if provided
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
        
        # Only index significant events
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
        
        # PPDA
        if "home_ppda" in metrics or "away_ppda" in metrics:
            home_ppda = metrics.get("home_ppda", 0)
            away_ppda = metrics.get("away_ppda", 0)
            texts.append(
                f"Pressing Intensity: Home team PPDA {home_ppda:.2f}, "
                f"Away team PPDA {away_ppda:.2f}. "
                f"{'Home team pressed more aggressively' if home_ppda < away_ppda else 'Away team pressed more aggressively'}."
            )
        
        # Physical metrics
        if "total_distance" in metrics:
            texts.append(
                f"Physical Output: Team covered {metrics['total_distance']:.1f} km. "
                f"Max sprint speed: {metrics.get('max_speed', 0):.1f} km/h."
            )
        
        # Possession
        if "possession" in metrics:
            home_poss = metrics["possession"].get("home", 50)
            texts.append(
                f"Possession: Home {home_poss}%, Away {100-home_poss}%."
            )
        
        # xT
        if "total_xt" in metrics:
            texts.append(
                f"Expected Threat: Total xT accumulated {metrics['total_xt']:.4f}. "
                f"Progressive passing was {'effective' if metrics['total_xt'] > 0.1 else 'limited'}."
            )
        
        return texts
