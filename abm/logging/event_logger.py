import pandas as pd
from typing import List, Dict
from datetime import datetime
import csv

from ..agents.base_agent import FootballAgent, GameContext, Position

class FootballEventLogger:
    """Event logger for process mining compatibility"""
    
    def __init__(self):
        self.events = []
        self.current_possession_id = 0
        self.event_counter = 0
        self.possession_start_time = 0
        self.current_possession_team = None
        self.current_possession_sequence = 0
        
    def log_event(self, agent: FootballAgent, action_type: str, result: str, 
                  ball_position: Position, game_context: GameContext):
        """Log a single event"""
        
        # Check for possession change
        if self._is_possession_change(agent, action_type, result):
            self.current_possession_id += 1
            self.possession_start_time = game_context.match_time
            self.current_possession_team = agent.team
            self.current_possession_sequence = 1
        else:
            self.current_possession_sequence += 1
        
        event = {
            # Case identification
            'case_id': f"possession_{self.current_possession_id:03d}",
            'process_type': self._determine_process_type(action_type, game_context),
            
            # Event identification
            'event_id': f"evt_{self.event_counter:06d}",
            'timestamp': game_context.match_time,
            'sequence_number': self.current_possession_sequence,
            
            # Core football action
            'activity': action_type,
            'activity_result': result,
            
            # Agent information
            'player_id': agent.agent_id,
            'player_role': agent.role,
            'team': agent.team,
            
            # Spatial context
            'start_x': agent.position.x,
            'start_y': agent.position.y,
            'end_x': ball_position.x,
            'end_y': ball_position.y,
            'pitch_zone': self._calculate_pitch_zone(ball_position.x),
            'sub_zone': self._calculate_sub_zone(ball_position.y),
            
            # Tactical context
            'pressure_level': agent.beliefs.get('pressure_level', 'unknown'),
            'numerical_situation': 'equal',  # Simplified for now
            'team_formation': game_context.formation,
            'game_state': self._determine_game_state(game_context.score, agent.team),
            'time_remaining': game_context.time_remaining,
            
            # Performance attributes
            'action_duration': 100,  # Fixed timestep for now
            'distance_covered': self._calculate_distance(agent.position, ball_position),
            'opponents_beaten': 0,  # Simplified
            'xg_added': self._calculate_xg_contribution(action_type, ball_position, result)
        }
        
        self.events.append(event)
        self.event_counter += 1
    
    def _is_possession_change(self, agent: FootballAgent, action_type: str, result: str) -> bool:
        """Determine if this event represents a possession change"""
        if self.current_possession_team is None:
            return True
        
        if agent.team != self.current_possession_team:
            return True
            
        if action_type in ['pass', 'dribble', 'shot'] and result == 'failure':
            return True
            
        return False
    
    def _determine_process_type(self, action_type: str, game_context: GameContext) -> str:
        """Determine the type of tactical process"""
        if action_type == 'kickoff':
            return 'possession'
        elif game_context.game_phase == 'attack':
            return 'possession'
        elif action_type in ['press', 'close_down', 'intercept']:
            return 'pressing'
        else:
            return 'possession'
    
    def _calculate_pitch_zone(self, x_coordinate: float) -> str:
        """Calculate which third of pitch"""
        if x_coordinate < 33.33:
            return 'defensive_third'
        elif x_coordinate < 66.67:
            return 'middle_third'
        else:
            return 'attacking_third'
    
    def _calculate_sub_zone(self, y_coordinate: float) -> str:
        """Calculate left/central/right zone"""
        if y_coordinate < 33.33:
            return 'left_flank'
        elif y_coordinate < 66.67:
            return 'central'
        else:
            return 'right_flank'
    
    def _determine_game_state(self, score: Dict[str, int], team: str) -> str:
        """Determine if team is winning/drawing/losing"""
        team_score = score[team]
        opponent_score = score['away' if team == 'home' else 'home']
        
        if team_score > opponent_score:
            return 'winning'
        elif team_score < opponent_score:
            return 'losing'
        else:
            return 'drawing'
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """Calculate distance between positions"""
        return pos1.distance_to(pos2)
    
    def _calculate_xg_contribution(self, action_type: str, ball_position: Position, result: str) -> float:
        """Calculate expected goal contribution of action"""
        if action_type == 'shot':
            if result == 'goal':
                return 1.0
            else:
                # Distance-based xG
                goal_distance = min(
                    ball_position.distance_to(Position(0, 50)),
                    ball_position.distance_to(Position(100, 50))
                )
                if goal_distance < 10:
                    return 0.4
                elif goal_distance < 20:
                    return 0.2
                else:
                    return 0.05
        elif action_type == 'pass' and result == 'success':
            # Small contribution for successful passes in attacking third
            if ball_position.x > 67:
                return 0.01
        
        return 0.0
    
    def get_dataframe(self) -> pd.DataFrame:
        """Return events as pandas DataFrame"""
        return pd.DataFrame(self.events)
    
    def export_to_csv(self, filename: str):
        """Export events to CSV file"""
        df = self.get_dataframe()
        df.to_csv(filename, index=False)
    
    def export_to_xes(self, filename: str):
        """Export events to XES format for PM4Py"""
        try:
            import pm4py
            
            # Prepare dataframe for XES
            df_xes = self.get_dataframe().copy()
            
            # Convert timestamp to datetime
            df_xes['time:timestamp'] = pd.to_datetime(df_xes['timestamp'], unit='ms')
            
            # Format for PM4Py
            event_log = pm4py.format_dataframe(
                df_xes,
                case_id='case_id',
                activity_key='activity',
                timestamp_key='time:timestamp'
            )
            
            # Export to XES
            pm4py.write_xes(event_log, filename)
            print(f"Successfully exported to XES: {filename}")
            
        except ImportError:
            print("PM4Py not installed. Run: pip install pm4py")
        except Exception as e:
            print(f"Error exporting to XES: {e}")