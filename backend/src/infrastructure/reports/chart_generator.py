"""
ChartGenerator - Infrastructure Layer

Generates tactical visualizations using mplsoccer.
"""
from typing import Optional, List, Dict, Any, Tuple
import io
import base64

# Lazy imports to avoid loading matplotlib in API
def _get_mplsoccer():
    from mplsoccer import Pitch, VerticalPitch
    return Pitch, VerticalPitch

def _get_plt():
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    return plt


class ChartGenerator:
    """
    Generates football pitch visualizations.
    
    Uses mplsoccer for pitch rendering and matplotlib for charts.
    """
    
    def __init__(self, dpi: int = 100, figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize chart generator.
        
        Args:
            dpi: Resolution for generated images
            figsize: Default figure size (width, height)
        """
        self.dpi = dpi
        self.figsize = figsize
    
    def generate_pass_network(
        self,
        passes: List[Dict[str, Any]],
        player_positions: Dict[str, Tuple[float, float]],
        team_name: str = "Team"
    ) -> bytes:
        """
        Generate a pass network visualization.
        
        Args:
            passes: List of passes with start/end positions
            player_positions: Average positions per player
            team_name: Name for title
            
        Returns:
            PNG image as bytes
        """
        Pitch, _ = _get_mplsoccer()
        plt = _get_plt()
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
        fig, ax = pitch.draw(figsize=self.figsize)
        
        # Draw player positions
        for player_id, (x, y) in player_positions.items():
            ax.scatter(x, y, s=300, c='white', edgecolors='black', zorder=3)
            ax.annotate(player_id[:3], (x, y), ha='center', va='center', fontsize=8)
        
        # Draw pass lines
        for p in passes:
            pitch.lines(
                p.get('start_x', 0), p.get('start_y', 0),
                p.get('end_x', 0), p.get('end_y', 0),
                ax=ax, comet=True, color='blue', alpha=0.5
            )
        
        ax.set_title(f"{team_name} Pass Network", fontsize=14)
        
        return self._fig_to_bytes(fig)
    
    def generate_heatmap(
        self,
        positions: List[Tuple[float, float]],
        title: str = "Player Heatmap"
    ) -> bytes:
        """
        Generate a heatmap of player positions.
        
        Args:
            positions: List of (x, y) positions
            title: Chart title
            
        Returns:
            PNG image as bytes
        """
        Pitch, _ = _get_mplsoccer()
        plt = _get_plt()
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
        fig, ax = pitch.draw(figsize=self.figsize)
        
        if positions:
            x_coords = [p[0] for p in positions]
            y_coords = [p[1] for p in positions]
            
            # KDE heatmap
            pitch.kdeplot(x_coords, y_coords, ax=ax, cmap='Reds', fill=True, levels=50, alpha=0.7)
        
        ax.set_title(title, fontsize=14)
        
        return self._fig_to_bytes(fig)
    
    def generate_pitch_control_frame(
        self,
        home_positions: List[Tuple[float, float]],
        away_positions: List[Tuple[float, float]],
        ball_position: Optional[Tuple[float, float]] = None,
        title: str = "Pitch Control"
    ) -> bytes:
        """
        Generate a pitch control visualization for a single frame.
        
        Args:
            home_positions: List of home team player positions
            away_positions: List of away team player positions
            ball_position: Optional ball position
            title: Chart title
            
        Returns:
            PNG image as bytes
        """
        Pitch, _ = _get_mplsoccer()
        plt = _get_plt()
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='white')
        fig, ax = pitch.draw(figsize=self.figsize)
        
        # Home team (blue)
        for x, y in home_positions:
            ax.scatter(x, y, s=200, c='blue', edgecolors='white', zorder=3)
        
        # Away team (red)
        for x, y in away_positions:
            ax.scatter(x, y, s=200, c='red', edgecolors='white', zorder=3)
        
        # Ball
        if ball_position:
            ax.scatter(ball_position[0], ball_position[1], s=100, c='yellow', 
                      edgecolors='black', zorder=4, marker='o')
        
        ax.set_title(title, fontsize=14, color='white')
        
        return self._fig_to_bytes(fig)
    
    def _fig_to_bytes(self, fig) -> bytes:
        """Convert matplotlib figure to PNG bytes."""
        plt = _get_plt()
        
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight', 
                   facecolor=fig.get_facecolor())
        plt.close(fig)
        buffer.seek(0)
        return buffer.getvalue()
    
    def fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        png_bytes = self._fig_to_bytes(fig)
        return base64.b64encode(png_bytes).decode('utf-8')
