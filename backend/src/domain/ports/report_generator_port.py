"""
ReportGeneratorPort - Domain Layer

Port for generating PDF and JSON reports.
"""
from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.tactical_report import TacticalReport


class ReportGeneratorPort(ABC):
    """
    Abstract interface for report generation.
    
    Concrete implementations will handle PDF rendering, JSON export, etc.
    """
    
    @abstractmethod
    def generate_pdf(self, report: TacticalReport) -> bytes:
        """
        Generate a PDF from the report.
        
        Args:
            report: TacticalReport entity
            
        Returns:
            PDF file as bytes
        """
        ...
    
    @abstractmethod
    def generate_json(self, report: TacticalReport) -> str:
        """
        Generate JSON export from the report.
        
        Args:
            report: TacticalReport entity
            
        Returns:
            JSON string
        """
        ...
