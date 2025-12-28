"""
CrewAI Adapter - Infrastructure Layer

Implementation of AnalysisPort using CrewAI multi-agent system.
"""
from typing import List, Dict, Any
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os

from src.domain.ports.analysis_port import AnalysisPort
from src.infrastructure.worker.tasks.crewai_tasks import run_crewai_analysis_task


class CrewAIAdapter(AnalysisPort):
    """
    CrewAI-based implementation of the AnalysisPort.
    
    Uses a multi-agent system for match analysis.
    """
    
    def __init__(self):
        """Initialize CrewAI adapter with LLM configuration."""
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def create_agents(self) -> Dict[str, Agent]:
        """
        Create CrewAI agents for analysis.
        
        Returns:
            Dictionary of agents (analyst, writer)
        """
        analyst = Agent(
            role="Football Tactical Analyst",
            goal="Analyze match data and identify tactical patterns, strengths, and weaknesses",
            backstory=(
                "You are an expert football tactical analyst with deep knowledge of modern "
                "football tactics, formations, and player movements. You specialize in analyzing "
                "match data to extract actionable insights for coaches and performance analysts."
            ),
            llm=self.llm,
            verbose=True
        )
        
        writer = Agent(
            role="Sports Report Writer",
            goal="Transform analytical findings into clear, actionable reports for coaches",
            backstory=(
                "You are a professional sports journalist specialized in tactical analysis. "
                "You excel at taking complex data and turning it into compelling, easy-to-understand "
                "narratives that coaches can act upon."
            ),
            llm=self.llm,
            verbose=True
        )
        
        return {"analyst": analyst, "writer": writer}
    
    def create_tasks(self, agents: Dict[str, Agent], match_id: str, query: str) -> List[Task]:
        """
        Create analysis tasks for the crew.
        
        Args:
            agents: Dictionary of agents
            match_id: Match identifier
            query: User's analysis query
            
        Returns:
            List of CrewAI tasks
        """
        analysis_task = Task(
            description=f"""
            Analyze match {match_id} with focus on: {query}
            
            Review available match data including:
            - Player positions and movements
            - Tactical formations
            - Passing patterns
            - Defensive organization
            
            Provide detailed tactical insights.
            """,
            expected_output="Detailed tactical analysis with specific observations and patterns",
            agent=agents["analyst"]
        )
        
        report_task = Task(
            description=f"""
            Based on the tactical analysis, create a concise report for coaches.
            
            The report should include:
            1. Key findings (2-3 main points)
            2. Tactical recommendations
            3. Areas for improvement
            
            Keep it actionable and focused on {query}.
            """,
            expected_output="A concise, actionable report in markdown format",
            agent=agents["writer"]
        )
        
        return [analysis_task, report_task]
    
    def run_analysis(self, match_id: str, query: str) -> str:
        """
        Run CrewAI analysis synchronously.
        
        Args:
            match_id: Match identifier
            query: User's analysis query
            
        Returns:
            Analysis result as string
        """
        agents = self.create_agents()
        tasks = self.create_tasks(agents, match_id, query)
        
        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)
    
    def dispatch_analysis(self, match_id: str, query: str) -> str:
        """
        Dispatch analysis job to Celery worker.
        
        Args:
            match_id: Match identifier
            query: User's analysis query
            
        Returns:
            Job ID (Celery task ID)
        """
        task = run_crewai_analysis_task.delay(match_id, query)
        return task.id
