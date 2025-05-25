from .base_agent import FootballAgent, Position, GameContext
from typing import Dict, List
import random

class Goalkeeper(FootballAgent):
    """Goalkeeper agent with specialized behaviors"""
    
    def _initialize_beliefs(self) -> Dict:
        return {
            'penalty_area_bounds': {'x_min': 0, 'x_max': 16, 'y_min': 37, 'y_max': 63},
            'goal_position': Position(0, 50),
            'shot_threat_level': 'none'
        }
    
    def _initialize_goals(self) -> List[str]:
        return ['prevent_goals', 'distribute_ball', 'organize_defense']
    
    def _initialize_plans(self) -> Dict:
        return {
            'shot_saving': ['position_for_shot', 'dive_to_ball'],
            'distribution': ['short_throw', 'long_kick', 'roll_out'],
            'positioning': ['stay_in_area', 'narrow_angle']
        }
    
    def _load_liveness_properties(self) -> List[str]:
        return [
            "eventually_distributes_ball_within_6_seconds",
            "always_attempts_save_when_shot_on_target",
            "continuously_communicates_with_defense"
        ]
    
    def _load_safety_constraints(self) -> List[str]:
        return [
            "never_leaves_penalty_area_during_open_play",
            "must_not_handle_ball_outside_penalty_area",
            "cannot_commit_leaving_goal_undefended"
        ]
    
    def decide_action(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        """Goalkeeper decision logic"""
        ball_distance = self.position.distance_to(game_context.ball_position)
        
        if self.has_ball:
            return self._decide_distribution(game_context, visible_agents)
        elif ball_distance < 5 and game_context.game_phase == 'defense':
            return 'save_attempt'
        else:
            return self._decide_positioning(game_context)
    
    def _decide_distribution(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        teammates = [a for a in visible_agents if a.team == self.team]
        if teammates:
            nearest_teammate = min(teammates, key=lambda t: self.position.distance_to(t.position))
            if self.position.distance_to(nearest_teammate.position) < 20:
                return 'short_pass'
            else:
                return 'long_kick'
        return 'long_kick'
    
    def _decide_positioning(self, game_context: GameContext) -> str:
        # Stay positioned based on ball location
        optimal_x = max(2, min(14, game_context.ball_position.x * 0.15))
        optimal_y = 50 + (game_context.ball_position.y - 50) * 0.3
        
        target_position = Position(optimal_x, optimal_y)
        if self.position.distance_to(target_position) > 2:
            return 'move_to_position'
        return 'maintain_position'

class CentreBack(FootballAgent):
    """Centre-back agent with defensive focus"""
    
    def _initialize_beliefs(self) -> Dict:
        return {
            'defensive_line': 25,
            'marking_assignment': None,
            'cover_partner': None
        }
    
    def _initialize_goals(self) -> List[str]:
        return ['defend_goal', 'win_aerial_duels', 'start_build_up']
    
    def _initialize_plans(self) -> Dict:
        return {
            'defending': ['close_down', 'intercept', 'clear_ball'],
            'build_up': ['short_pass', 'long_pass', 'carry_forward'],
            'positioning': ['hold_line', 'cover_partner', 'mark_opponent']
        }
    
    def _load_liveness_properties(self) -> List[str]:
        return [
            "eventually_clears_ball_when_under_pressure",
            "always_tracks_opponent_runs",
            "continuously_maintains_defensive_line"
        ]
    
    def _load_safety_constraints(self) -> List[str]:
        return [
            "never_both_centre_backs_commit_to_tackle",
            "must_not_leave_penalty_area_unmarked",
            "cannot_venture_beyond_halfway_when_partner_advanced"
        ]
    
    def decide_action(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        if self.has_ball:
            return self._decide_with_ball(game_context, visible_agents)
        else:
            return self._decide_without_ball(game_context, visible_agents)
    
    def _decide_with_ball(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        pressure = self.beliefs['pressure_level']
        
        if pressure in ['high', 'extreme']:
            return 'clear_ball'
        elif pressure == 'medium':
            return 'short_pass'
        else:
            # Look for build-up opportunity
            teammates = [a for a in visible_agents if a.team == self.team]
            advanced_teammates = [t for t in teammates if t.position.x > self.position.x + 10]
            
            if advanced_teammates:
                return 'forward_pass'
            else:
                return 'safe_pass'
    
    def _decide_without_ball(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        ball_distance = self.position.distance_to(game_context.ball_position)
        
        if ball_distance < 15 and game_context.game_phase == 'defense':
            return 'close_down'
        elif game_context.game_phase == 'attack':
            return 'maintain_position'
        else:
            return 'track_runner'

class Midfielder(FootballAgent):
    """Central midfielder with box-to-box responsibilities"""
    
    def _initialize_beliefs(self) -> Dict:
        return {
            'passing_options': [],
            'support_needed': False,
            'transition_opportunity': False
        }
    
    def _initialize_goals(self) -> List[str]:
        return ['control_tempo', 'create_chances', 'support_defense']
    
    def _initialize_plans(self) -> Dict:
        return {
            'attacking': ['through_pass', 'support_run', 'shoot'],
            'defending': ['intercept', 'track_back', 'press'],
            'circulation': ['switch_play', 'retain_possession', 'recycle_ball']
        }
    
    def _load_liveness_properties(self) -> List[str]:
        return [
            "eventually_distributes_ball_within_5_seconds",
            "always_provides_passing_option",
            "continuously_adjusts_position"
        ]
    
    def _load_safety_constraints(self) -> List[str]:
        return [
            "never_leaves_central_zone_unoccupied",
            "must_not_attempt_risky_passes_own_third",
            "cannot_ignore_defensive_duties"
        ]
    
    def decide_action(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        if self.has_ball:
            return self._decide_with_ball(game_context, visible_agents)
        else:
            return self._decide_without_ball(game_context, visible_agents)
    
    def _decide_with_ball(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        # Assess situation
        teammates = [a for a in visible_agents if a.team == self.team]
        attacking_teammates = [t for t in teammates if t.position.x > self.position.x]
        
        if self.position.x > 70:  # In attacking third
            if attacking_teammates:
                return 'through_pass'
            else:
                return 'shoot'
        elif self.position.x > 40:  # In middle third
            if len(attacking_teammates) >= 2:
                return 'forward_pass'
            else:
                return 'retain_possession'
        else:  # In defensive third
            return 'safe_pass'
    
    def _decide_without_ball(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        ball_distance = self.position.distance_to(game_context.ball_position)
        
        if game_context.game_phase == 'attack':
            return 'support_run'
        elif game_context.game_phase == 'defense':
            if ball_distance < 20:
                return 'press'
            else:
                return 'track_back'
        else:  # transition
            return 'find_space'

class Striker(FootballAgent):
    """Striker agent focused on goal scoring"""
    
    def _initialize_beliefs(self) -> Dict:
        return {
            'goal_distance': 100,
            'shooting_angle': 0,
            'marker_distance': 100
        }
    
    def _initialize_goals(self) -> List[str]:
        return ['score_goals', 'create_space', 'hold_up_play']
    
    def _initialize_plans(self) -> Dict:
        return {
            'scoring': ['shoot', 'one_touch_finish', 'header'],
            'creating': ['run_behind', 'drop_deep', 'drift_wide'],
            'linking': ['hold_up', 'lay_off', 'flick_on']
        }
    
    def _load_liveness_properties(self) -> List[str]:
        return [
            "eventually_attempts_shot_when_in_scoring_position",
            "always_makes_runs_to_stretch_defense",
            "continuously_holds_up_ball_for_support"
        ]
    
    def _load_safety_constraints(self) -> List[str]:
        return [
            "never_drops_too_deep_leaving_attack_without_focal_point",
            "must_not_attempt_shots_from_impossible_angles",
            "cannot_ignore_link_up_play_responsibilities"
        ]
    
    def decide_action(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        if self.has_ball:
            return self._decide_with_ball(game_context, visible_agents)
        else:
            return self._decide_without_ball(game_context, visible_agents)
    
    def _decide_with_ball(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        # Calculate goal distance and angle
        goal_position = Position(100, 50)
        goal_distance = self.position.distance_to(goal_position)
        
        if goal_distance < 20 and self.position.x > 80:
            return 'shoot'
        elif self.beliefs['pressure_level'] == 'low':
            return 'dribble_forward'
        else:
            # Look for support
            teammates = [a for a in visible_agents if a.team == self.team and a.position.x > 60]
            if teammates:
                return 'lay_off'
            else:
                return 'hold_up'
    
    def _decide_without_ball(self, game_context: GameContext, visible_agents: List[FootballAgent]) -> str:
        if game_context.game_phase == 'attack':
            # Make intelligent runs
            if self.position.x < 70:
                return 'run_behind'
            else:
                return 'find_space'
        else:
            return 'press_defender'