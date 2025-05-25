import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from ..agents.base_agent import Position, FootballAgent

@dataclass
class Ball:
    position: Position
    velocity: Tuple[float, float] = (0, 0)
    possession: Optional[str] = None  # agent_id who has the ball
    
class FootballPitch:
    """Football pitch environment with physics and rules"""
    
    def __init__(self, length: float = 100, width: float = 100):
        self.length = length  # 0-100
        self.width = width    # 0-100
        self.ball = Ball(Position(50, 50))
        
        # Pitch zones
        self.zones = {
            'defensive_third': (0, 33.33),
            'middle_third': (33.33, 66.67),
            'attacking_third': (66.67, 100)
        }
        
        # Goals
        self.home_goal = {'x': 0, 'y_min': 45, 'y_max': 55}
        self.away_goal = {'x': 100, 'y_min': 45, 'y_max': 55}
        
        # Penalty areas
        self.home_penalty_area = {'x_min': 0, 'x_max': 16, 'y_min': 37, 'y_max': 63}
        self.away_penalty_area = {'x_min': 84, 'x_max': 100, 'y_min': 37, 'y_max': 63}
    
    def get_zone(self, position: Position) -> str:
        """Determine which third of the pitch a position is in"""
        if position.x <= 33.33:
            return 'defensive_third'
        elif position.x <= 66.67:
            return 'middle_third'
        else:
            return 'attacking_third'
    
    def get_sub_zone(self, position: Position) -> str:
        """Determine left/central/right sub-zone"""
        if position.y <= 33.33:
            return 'left_flank'
        elif position.y <= 66.67:
            return 'central'
        else:
            return 'right_flank'
    
    def is_in_penalty_area(self, position: Position, team: str) -> bool:
        """Check if position is in penalty area"""
        if team == 'home':
            area = self.home_penalty_area
        else:
            area = self.away_penalty_area
            
        return (area['x_min'] <= position.x <= area['x_max'] and 
                area['y_min'] <= position.y <= area['y_max'])
    
    def is_goal_scored(self, ball_position: Position) -> Optional[str]:
        """Check if ball crossed goal line"""
        # Home goal (x=0)
        if (ball_position.x <= 0 and 
            self.home_goal['y_min'] <= ball_position.y <= self.home_goal['y_max']):
            return 'away'  # Away team scored
            
        # Away goal (x=100)
        if (ball_position.x >= 100 and 
            self.away_goal['y_min'] <= ball_position.y <= self.away_goal['y_max']):
            return 'home'  # Home team scored
            
        return None
    
    def update_ball_physics(self, dt: float = 0.1):
        """Update ball position based on velocity"""
        if self.ball.velocity != (0, 0):
            # Apply velocity
            new_x = self.ball.position.x + self.ball.velocity[0] * dt
            new_y = self.ball.position.y + self.ball.velocity[1] * dt
            
            # Boundary checking
            new_x = max(0, min(self.length, new_x))
            new_y = max(0, min(self.width, new_y))
            
            self.ball.position = Position(new_x, new_y)
            
            # Apply friction
            friction = 0.95
            self.ball.velocity = (
                self.ball.velocity[0] * friction,
                self.ball.velocity[1] * friction
            )
            
            # Stop if velocity is very low
            if abs(self.ball.velocity[0]) < 0.1 and abs(self.ball.velocity[1]) < 0.1:
                self.ball.velocity = (0, 0)