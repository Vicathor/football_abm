import sys
import os
import numpy as np
import pandas as pd
from typing import List, Dict
import logging
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from abm.environment.pitch import FootballPitch, Ball
from abm.agents.base_agent import FootballAgent, GameContext, Position
from abm.agents.field_players import Goalkeeper, CentreBack, Midfielder, Striker
from abm.logging.event_logger import FootballEventLogger

class FootballSimulation:
    """Main simulation engine for football match"""
    
    def __init__(self, home_formation: str = "4-4-2", away_formation: str = "4-4-2"):
        self.pitch = FootballPitch()
        self.match_time = 0  # milliseconds
        self.match_duration = 90 * 60 * 1000  # 90 minutes in milliseconds
        self.timestep = 100  # 100ms per step
        
        self.score = {'home': 0, 'away': 0}
        self.game_phase = 'kickoff'
        
        # Initialize teams
        self.home_team = self._create_team('home', home_formation)
        self.away_team = self._create_team('away', away_formation)
        self.all_agents = self.home_team + self.away_team
        
        # Event logging
        self.event_logger = FootballEventLogger()
        
        # Statistics tracking
        self.match_stats = {
            'possession': {'home': 0, 'away': 0},
            'passes': {'home': 0, 'away': 0},
            'shots': {'home': 0, 'away': 0}
        }
        
    def _create_team(self, team_name: str, formation: str) -> List[FootballAgent]:
        """Create team with specified formation"""
        formations = {
            '4-4-2': {
                'GK': Position(5 if team_name == 'home' else 95, 50),
                'CB_L': Position(20 if team_name == 'home' else 80, 30),
                'CB_R': Position(20 if team_name == 'home' else 80, 70),
                'LB': Position(15 if team_name == 'home' else 85, 10),
                'RB': Position(15 if team_name == 'home' else 85, 90),
                'CM_L': Position(50 if team_name == 'home' else 50, 35),
                'CM_R': Position(50 if team_name == 'home' else 50, 65),
                'LW': Position(70 if team_name == 'home' else 30, 20),
                'RW': Position(70 if team_name == 'home' else 30, 80),
                'ST1': Position(85 if team_name == 'home' else 15, 40),
                'ST2': Position(85 if team_name == 'home' else 15, 60)
            }
        }
        
        if formation not in formations:
            raise ValueError(f"Formation {formation} not implemented")
        
        positions = formations[formation]
        team = []
        
        for i, (role, pos) in enumerate(positions.items()):
            agent_id = f"{team_name}_{role}_{i}"
            
            if role == 'GK':
                agent = Goalkeeper(agent_id, role, team_name, pos)
            elif role in ['CB_L', 'CB_R', 'LB', 'RB']:
                agent = CentreBack(agent_id, role, team_name, pos)
            elif role in ['CM_L', 'CM_R', 'LW', 'RW']:
                agent = Midfielder(agent_id, role, team_name, pos)
            elif role in ['ST1', 'ST2']:
                agent = Striker(agent_id, role, team_name, pos)
            else:
                raise ValueError(f"Unknown role: {role}")
                
            team.append(agent)
            
        return team
    
    def run_simulation(self, duration_minutes: int = 90) -> pd.DataFrame:
        """Run complete football simulation"""
        self.match_duration = duration_minutes * 60 * 1000
        logging.info(f"Starting {duration_minutes}-minute simulation")
        
        # Kickoff
        self._kickoff()
        
        # Main simulation loop
        while self.match_time < self.match_duration:
            self._simulation_step()
            self.match_time += self.timestep
            
            # Check for goals
            goal_scorer = self.pitch.is_goal_scored(self.pitch.ball.position)
            if goal_scorer:
                self._handle_goal(goal_scorer)
        
        logging.info(f"Simulation complete. Final score: Home {self.score['home']} - {self.score['away']} Away")
        
        # Return event log as DataFrame
        return self.event_logger.get_dataframe()
    
    def _kickoff(self):
        """Initialize match with kickoff"""
        self.pitch.ball = Ball(Position(50, 50))
        self.pitch.ball.possession = self.home_team[0].agent_id  # Give to first player
        self.home_team[0].has_ball = True
        self.game_phase = 'attack'
        
        # Log kickoff event
        self.event_logger.log_event(
            agent=self.home_team[0],
            action_type='kickoff',
            result='success',
            ball_position=self.pitch.ball.position,
            game_context=self._get_game_context()
        )
    
    def _simulation_step(self):
        """Execute one simulation timestep"""
        # Update game context
        game_context = self._get_game_context()
        
        # Each agent makes a decision
        for agent in self.all_agents:
            # Update agent beliefs
            visible_agents = self._get_visible_agents(agent)
            agent.update_beliefs(game_context, visible_agents)
            
            # Agent decides action
            action = agent.decide_action(game_context, visible_agents)
            
            # Execute action
            self._execute_action(agent, action, game_context)
        
        # Update ball physics
        self.pitch.update_ball_physics(self.timestep / 1000.0)
        
        # Update game phase
        self._update_game_phase()
    
    def _get_game_context(self) -> GameContext:
        """Get current game context"""
        return GameContext(
            match_time=self.match_time,
            time_remaining=(self.match_duration - self.match_time) // 1000,
            score=self.score.copy(),
            ball_position=self.pitch.ball.position,
            game_phase=self.game_phase,
            formation="4-4-2"  # Simplified
        )
    
    def _get_visible_agents(self, agent: FootballAgent) -> List[FootballAgent]:
        """Get agents visible to given agent (simplified - all agents visible)"""
        return [a for a in self.all_agents if a.agent_id != agent.agent_id]
    
    def _execute_action(self, agent: FootballAgent, action: str, game_context: GameContext):
        """Execute agent's chosen action"""
        result = 'failure'  # Default
        
        if action == 'pass' and agent.has_ball:
            result = self._execute_pass(agent)
        elif action == 'shoot' and agent.has_ball:
            result = self._execute_shot(agent)
        elif action == 'dribble' and agent.has_ball:
            result = self._execute_dribble(agent)
        elif action in ['move_to_position', 'support_run', 'track_back']:
            result = self._execute_movement(agent, action)
        elif action in ['close_down', 'press', 'intercept']:
            result = self._execute_defensive_action(agent, action)
        
        # Log the action
        if action != 'maintain_position':  # Don't log every position maintenance
            self.event_logger.log_event(
                agent=agent,
                action_type=action,
                result=result,
                ball_position=self.pitch.ball.position,
                game_context=game_context
            )
    
    def _execute_pass(self, agent: FootballAgent) -> str:
        """Execute a pass action"""
        # Find nearest teammate
        teammates = [a for a in self.all_agents if a.team == agent.team and a.agent_id != agent.agent_id]
        if not teammates:
            return 'failure'
        
        # Simple pass success calculation
        target = min(teammates, key=lambda t: agent.position.distance_to(t.position))
        pass_distance = agent.position.distance_to(target.position)
        pressure = agent.beliefs.get('pressure_level', 'low')
        
        # Success probability based on distance and pressure
        base_success = 0.8
        distance_penalty = min(0.3, pass_distance / 100)
        pressure_penalty = {'low': 0, 'medium': 0.1, 'high': 0.2, 'extreme': 0.3}.get(pressure, 0)
        
        success_prob = base_success - distance_penalty - pressure_penalty
        
        if np.random.random() < success_prob:
            # Successful pass
            agent.has_ball = False
            target.has_ball = True
            self.pitch.ball.possession = target.agent_id
            self.pitch.ball.position = target.position
            self.match_stats['passes'][agent.team] += 1
            return 'success'
        else:
            # Failed pass - ball goes to random position
            agent.has_ball = False
            self.pitch.ball.possession = None
            # Move ball to intermediate position
            new_x = (agent.position.x + target.position.x) / 2 + np.random.normal(0, 5)
            new_y = (agent.position.y + target.position.y) / 2 + np.random.normal(0, 5)
            self.pitch.ball.position = Position(
                max(0, min(100, new_x)),
                max(0, min(100, new_y))
            )
            return 'failure'
    
    def _execute_shot(self, agent: FootballAgent) -> str:
        """Execute a shot action"""
        # Determine target goal
        if agent.team == 'home':
            goal_pos = Position(100, 50)
        else:
            goal_pos = Position(0, 50)
        
        shot_distance = agent.position.distance_to(goal_pos)
        
        # Simple shot success calculation
        if shot_distance > 30:
            success_prob = 0.05  # Very low from distance
        elif shot_distance > 20:
            success_prob = 0.15
        elif shot_distance > 10:
            success_prob = 0.25
        else:
            success_prob = 0.4  # Best chance close to goal
        
        self.match_stats['shots'][agent.team] += 1
        
        if np.random.random() < success_prob:
            # Goal scored!
            self.score[agent.team] += 1
            agent.has_ball = False
            self.pitch.ball.possession = None
            return 'goal'
        else:
            # Shot saved/missed
            agent.has_ball = False
            self.pitch.ball.possession = None
            # Ball goes to random position near goal
            self.pitch.ball.position = Position(
                goal_pos.x + np.random.normal(0, 10),
                goal_pos.y + np.random.normal(0, 10)
            )
            return 'saved'
    
    def _execute_dribble(self, agent: FootballAgent) -> str:
        """Execute a dribble action"""
        # Simple dribble - move player and ball forward
        if agent.team == 'home':
            new_x = min(100, agent.position.x + np.random.uniform(2, 5))
        else:
            new_x = max(0, agent.position.x - np.random.uniform(2, 5))
        
        new_y = agent.position.y + np.random.uniform(-2, 2)
        new_y = max(0, min(100, new_y))
        
        agent.position = Position(new_x, new_y)
        self.pitch.ball.position = agent.position
        
        return 'success'
    
    def _execute_movement(self, agent: FootballAgent, action: str) -> str:
        """Execute movement actions"""
        # Simple movement towards appropriate position
        if action == 'support_run':
            # Move towards ball
            direction_x = (self.pitch.ball.position.x - agent.position.x) * 0.1
            direction_y = (self.pitch.ball.position.y - agent.position.y) * 0.1
        elif action == 'track_back':
            # Move towards own goal
            target_x = 25 if agent.team == 'home' else 75
            direction_x = (target_x - agent.position.x) * 0.1
            direction_y = (50 - agent.position.y) * 0.05
        else:  # move_to_position
            # Move towards home position
            direction_x = (agent.home_position.x - agent.position.x) * 0.1
            direction_y = (agent.home_position.y - agent.position.y) * 0.1
        
        new_x = max(0, min(100, agent.position.x + direction_x))
        new_y = max(0, min(100, agent.position.y + direction_y))
        agent.position = Position(new_x, new_y)
        
        return 'success'
    
    def _execute_defensive_action(self, agent: FootballAgent, action: str) -> str:
        """Execute defensive actions"""
        ball_distance = agent.position.distance_to(self.pitch.ball.position)
        
        if action == 'intercept' and ball_distance < 3:
            # Attempt to win ball
            if np.random.random() < 0.3:  # 30% chance to intercept
                # Find current ball holder
                for other_agent in self.all_agents:
                    if other_agent.has_ball:
                        other_agent.has_ball = False
                        break
                
                agent.has_ball = True
                self.pitch.ball.possession = agent.agent_id
                self.pitch.ball.position = agent.position
                return 'success'
        
        # For other defensive actions, just move towards ball
        direction_x = (self.pitch.ball.position.x - agent.position.x) * 0.2
        direction_y = (self.pitch.ball.position.y - agent.position.y) * 0.2
        
        new_x = max(0, min(100, agent.position.x + direction_x))
        new_y = max(0, min(100, agent.position.y + direction_y))
        agent.position = Position(new_x, new_y)
        
        return 'success'
    
    def _update_game_phase(self):
        """Update current game phase based on ball position"""
        ball_x = self.pitch.ball.position.x
        
        if ball_x < 33:
            self.game_phase = 'defense' if self.pitch.ball.possession in [a.agent_id for a in self.home_team] else 'attack'
        elif ball_x > 67:
            self.game_phase = 'attack' if self.pitch.ball.possession in [a.agent_id for a in self.home_team] else 'defense'
        else:
            self.game_phase = 'transition'
    
    def _handle_goal(self, scoring_team: str):
        """Handle goal scoring"""
        logging.info(f"GOAL! {scoring_team} team scores!")
        self.score[scoring_team] += 1
        
        # Reset for kickoff
        self._kickoff()