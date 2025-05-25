import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

@dataclass
class Position:
    x: float  # 0-100 (length of pitch)
    y: float  # 0-100 (width of pitch)
    
    def distance_to(self, other: 'Position') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class GameContext:
    match_time: int  # milliseconds
    time_remaining: int  # seconds
    score: Dict[str, int]  # {'home': 0, 'away': 1}
    ball_position: Position
    game_phase: str  # 'attack', 'defense', 'transition'
    formation: str  # '4-4-2', '4-3-3', etc.

class FootballAgent(ABC):
    """Base agent class implementing Prometheus agent architecture"""
    
    def __init__(self, agent_id: str, role: str, team: str, initial_position: Position):
        self.agent_id = agent_id
        self.role = role
        self.team = team
        self.position = initial_position
        self.home_position = initial_position  # Formation position
        self.has_ball = False
        self.stamina = 100.0
        self.decision_history = []
        
        # Prometheus components
        self.beliefs = self._initialize_beliefs()
        self.goals = self._initialize_goals()
        self.plans = self._initialize_plans()
        
        # Gaia properties
        self.liveness_goals = self._load_liveness_properties()
        self.safety_constraints = self._load_safety_constraints()
        
    @abstractmethod
    def _initialize_beliefs(self) -> Dict:
        """Initialize agent's beliefs about world state"""
        pass
        
    @abstractmethod
    def _initialize_goals(self) -> List[str]:
        """Initialize agent's goals based on role"""
        pass
        
    @abstractmethod
    def _initialize_plans(self) -> Dict:
        """Initialize agent's action plans"""
        pass
        
    @abstractmethod
    def decide_action(self, game_context: GameContext, visible_agents: List['FootballAgent']) -> str:
        """Main decision-making method"""
        pass
        
    def update_beliefs(self, game_context: GameContext, visible_agents: List['FootballAgent']):
        """Update agent's beliefs based on observations"""
        self.beliefs['ball_position'] = game_context.ball_position
        self.beliefs['teammates'] = [a for a in visible_agents if a.team == self.team]
        self.beliefs['opponents'] = [a for a in visible_agents if a.team != self.team]
        self.beliefs['pressure_level'] = self._calculate_pressure(visible_agents)
        
    def _calculate_pressure(self, visible_agents: List['FootballAgent']) -> str:
        """Calculate pressure level based on opponent proximity"""
        if not self.has_ball:
            return "none"
            
        nearest_opponent_distance = min([
            self.position.distance_to(agent.position) 
            for agent in visible_agents 
            if agent.team != self.team
        ], default=100)
        
        if nearest_opponent_distance < 2:
            return "extreme"
        elif nearest_opponent_distance < 5:
            return "high"
        elif nearest_opponent_distance < 10:
            return "medium"
        else:
            return "low"