"""
CrewAI Adapter - Infrastructure Layer

Implementation of AnalysisPort using CrewAI multi-agent system.
"""
from typing import List, Dict, Any
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os

from src.domain.ports.analysis_port import AnalysisPort


class CrewAIAdapter(AnalysisPort):
    """
    CrewAI-based implementation of the AnalysisPort.
    
    Uses a multi-agent system for match analysis.
    """
    
    def __init__(self):
        """Initialize CrewAI adapter with LLM configuration."""
        # LLM Provider Selection
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        if provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY is required for Gemini provider")
                
            self.llm = ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_MODEL", "gemini-pro"),
                temperature=0.7,
                google_api_key=api_key
            )
        else:
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
            goal="Analyze match data and identify tactical patterns, strengths, and weaknesses based on provided statistics",
            backstory=(
                "You are an expert football tactical analyst with deep knowledge of modern "
                "football tactics, formations, and player movements. You specialize in analyzing "
                "match data to extract actionable insights for coaches and performance analysts. "
                "CRITICAL: You MUST base your analysis on the specific match statistics provided to you. "
                "Do not make assumptions or provide generic football knowledge - cite the actual data points given."
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
                "narratives that coaches can act upon. Always reference specific statistics when making claims."
            ),
            llm=self.llm,
            verbose=True
        )
        
        return {"analyst": analyst, "writer": writer}
    
    def create_tasks(self, agents: Dict[str, Agent], match_id: str, query: str, match_context: str = "") -> List[Task]:
        """
        Create analysis tasks for the crew.
        
        Args:
            agents: Dictionary of agents
            match_id: Match identifier
            query: User's analysis query
            match_context: Formatted string with match statistics and context
            
        Returns:
            List of CrewAI tasks
        """
        context_section = f"""
        
MATCH CONTEXT AND STATISTICS:
{match_context if match_context else "No specific match data available. Provide general tactical analysis."}
        """ if match_context or True else ""
        
        analysis_task = Task(
            description=f"""
            Analyze match {match_id} with focus on: {query}
            {context_section}
            Review the provided match data and identify tactical patterns.
            
            Provide detailed tactical insights based on the statistics above.
            """,
            expected_output="Detailed tactical analysis with specific observations and patterns citing the provided statistics",
            agent=agents["analyst"]
        )
        
        report_task = Task(
            description=f"""
            Based on the tactical analysis, create a concise report for coaches.
            
            The report should include:
            1. Key findings (2-3 main points) with specific statistics
            2. Tactical recommendations
            3. Areas for improvement
            
            Keep it actionable and focused on {query}.
            """,
            expected_output="A concise, actionable report in markdown format with data-backed insights",
            agent=agents["writer"]
        )
        
        return [analysis_task, report_task]
    
    def run_analysis(self, match_id: str, query: str, match_context: str = "") -> str:
        """
        Run CrewAI analysis synchronously.
        
        Args:
            match_id: Match identifier
            query: User's analysis query
            match_context: Formatted string with match statistics
            
        Returns:
            Analysis result as string
        """
        agents = self.create_agents()
        tasks = self.create_tasks(agents, match_id, query, match_context)
        
        crew = Crew(
            agents=list(agents.values()),
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        return str(result)

    def dispatch_analysis(self, match_id: str, query: str) -> str:
        """
        Dispatch analysis job (Not supported by synchronous adapter).
        
        This adapter is designed to run within the worker context, 
        so dispatching is handled by CeleryAnalysisDispatcher.
        """
        raise NotImplementedError("CrewAIAdapter is for synchronous execution only. Use CeleryAnalysisDispatcher for dispatching.")
