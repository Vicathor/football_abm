import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import matplotlib.pyplot as plt

# Optional imports - will handle gracefully if not available
try:
    import pm4py
    PM4PY_AVAILABLE = True
except ImportError:
    PM4PY_AVAILABLE = False
    print("PM4Py not available. Install with: pip install pm4py")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly not available. Install with: pip install plotly")


class FootballProcessMining:
    """Process mining analysis for football simulation data"""
    
    def __init__(self, events_df: pd.DataFrame):
        self.events_df = events_df.copy()
        self.event_log = None
        if PM4PY_AVAILABLE:
            self._prepare_event_log()
    
    def _prepare_event_log(self):
        """Prepare event log for PM4Py"""
        if not PM4PY_AVAILABLE:
            print("PM4Py not available - skipping event log preparation")
            return
            
        try:
            # Convert timestamp to datetime for PM4Py
            df_temp = self.events_df.copy()
            df_temp['time:timestamp'] = pd.to_datetime(df_temp['timestamp'], unit='ms')
            
            # Format for PM4Py
            self.event_log = pm4py.format_dataframe(
                df_temp,
                case_id='case_id',
                activity_key='activity',
                timestamp_key='time:timestamp'
            )
        except Exception as e:
            print(f"Error preparing event log: {e}")
    
    def discover_process_models(self) -> Dict:
        """Discover different process models"""
        if not PM4PY_AVAILABLE:
            print("PM4Py not available - cannot discover process models")
            return {}
            
        models = {}
        
        try:
            # Inductive Miner - most robust for real data
            print("Discovering process model with Inductive Miner...")
            net, im, fm = pm4py.discover_petri_net_inductive(self.event_log)
            models['inductive'] = {'net': net, 'im': im, 'fm': fm}
            print("✅ Inductive miner successful")
        except Exception as e:
            print(f"⚠️ Inductive miner failed: {e}")
        
        try:
            # Heuristics Miner - good for complex processes
            print("Discovering process model with Heuristics Miner...")
            net, im, fm = pm4py.discover_petri_net_heuristics(self.event_log)
            models['heuristics'] = {'net': net, 'im': im, 'fm': fm}
            print("✅ Heuristics miner successful")
        except Exception as e:
            print(f"⚠️ Heuristics miner failed: {e}")
        
        return models
    
    def analyze_tactical_patterns(self) -> Dict:
        """Analyze tactical patterns in football"""
        print("🔍 Analyzing tactical patterns...")
        analysis = {}
        
        # 1. Possession flow analysis
        analysis['possession_patterns'] = self._analyze_possession_patterns()
        
        # 2. Attacking patterns
        analysis['attacking_patterns'] = self._analyze_attacking_patterns()
        
        # 3. Defensive patterns
        analysis['defensive_patterns'] = self._analyze_defensive_patterns()
        
        # 4. Team comparison
        analysis['team_comparison'] = self._compare_teams()
        
        # 5. Temporal analysis
        analysis['temporal_patterns'] = self._analyze_temporal_patterns()
        
        # 6. Zone analysis
        analysis['zone_analysis'] = self._analyze_zones()
        
        return analysis
    
    def _analyze_possession_patterns(self) -> Dict:
        """Analyze possession flow patterns"""
        print("📊 Analyzing possession patterns...")
        
        # Group by possession (case_id)
        possession_stats = self.events_df.groupby('case_id').agg({
            'activity': 'count',
            'team': 'first',
            'timestamp': ['min', 'max'],
            'pitch_zone': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'unknown',
            'activity_result': lambda x: (x == 'success').mean() if len(x) > 0 else 0
        }).round(3)
        
        possession_stats.columns = ['event_count', 'team', 'start_time', 'end_time', 'main_zone', 'success_rate']
        possession_stats['duration'] = possession_stats['end_time'] - possession_stats['start_time']
        
        return {
            'total_possessions': len(possession_stats),
            'avg_possession_duration': possession_stats['duration'].mean(),
            'avg_events_per_possession': possession_stats['event_count'].mean(),
            'possession_by_team': possession_stats['team'].value_counts().to_dict(),
            'avg_success_rate': possession_stats['success_rate'].mean()
        }
    
    def _analyze_attacking_patterns(self) -> Dict:
        """Analyze attacking patterns"""
        print("⚔️ Analyzing attacking patterns...")
        
        attacking_events = self.events_df[
            self.events_df['activity'].isin(['pass', 'dribble', 'shot', 'cross', 'run_behind'])
        ]
        
        if len(attacking_events) == 0:
            return {'message': 'No attacking events found'}
        
        # Attack progression patterns
        attack_sequences = attacking_events.groupby('case_id')['pitch_zone'].apply(list)
        
        # Common attack patterns
        common_progressions = {}
        for seq in attack_sequences:
            if len(seq) >= 2:
                for i in range(len(seq) - 1):
                    pattern = f"{seq[i]} -> {seq[i+1]}"
                    common_progressions[pattern] = common_progressions.get(pattern, 0) + 1
        
        # Sort by frequency
        sorted_patterns = sorted(common_progressions.items(), key=lambda x: x[1], reverse=True)
        
        # Shot analysis
        shots = attacking_events[attacking_events['activity'] == 'shot']
        
        return {
            'total_attacking_events': len(attacking_events),
            'common_progressions': sorted_patterns[:10],
            'attack_success_rate': (attacking_events['activity_result'] == 'success').mean(),
            'total_shots': len(shots),
            'shot_success_rate': (shots['activity_result'] == 'goal').mean() if len(shots) > 0 else 0,
            'xg_total': attacking_events['xg_added'].sum()
        }
    
    def _analyze_defensive_patterns(self) -> Dict:
        """Analyze defensive patterns"""
        print("🛡️ Analyzing defensive patterns...")
        
        defensive_events = self.events_df[
            self.events_df['activity'].isin(['press_defender', 'track_runner', 'intercept', 'tackle', 'close_down'])
        ]
        
        if len(defensive_events) == 0:
            return {'message': 'No defensive events found'}
        
        # Defensive intensity by zone
        zone_pressure = defensive_events.groupby('pitch_zone').size()
        
        # Defensive success by action type
        defensive_success = defensive_events.groupby('activity')['activity_result'].apply(
            lambda x: (x == 'success').mean()
        )
        
        return {
            'total_defensive_events': len(defensive_events),
            'pressure_by_zone': zone_pressure.to_dict(),
            'defensive_success_rate': (defensive_events['activity_result'] == 'success').mean(),
            'success_by_action': defensive_success.to_dict(),
            'avg_defensive_actions_per_possession': len(defensive_events) / self.events_df['case_id'].nunique()
        }
    
    def _compare_teams(self) -> Dict:
        """Compare team performance"""
        print("⚖️ Comparing team performance...")
        
        team_stats = self.events_df.groupby('team').agg({
            'activity': 'count',
            'activity_result': lambda x: (x == 'success').mean(),
            'case_id': 'nunique',
            'xg_added': 'sum',
            'pitch_zone': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'unknown'
        }).round(3)
        
        team_stats.columns = ['total_actions', 'success_rate', 'possessions', 'total_xg', 'most_active_zone']
        
        return team_stats.to_dict('index')
    
    def _analyze_temporal_patterns(self) -> Dict:
        """Analyze patterns over time"""
        print("⏱️ Analyzing temporal patterns...")
        
        # Convert timestamp to minutes
        self.events_df['match_minute'] = self.events_df['timestamp'] // 60000
        
        # Activity intensity over time (events per minute)
        temporal_intensity = self.events_df.groupby('match_minute').size()
        
        # Success rate over time
        temporal_success = self.events_df.groupby('match_minute')['activity_result'].apply(
            lambda x: (x == 'success').mean()
        )
        
        # xG accumulation over time
        temporal_xg = self.events_df.groupby(['match_minute', 'team'])['xg_added'].sum().unstack(fill_value=0)
        
        return {
            'activity_intensity': temporal_intensity.to_dict(),
            'success_rate_over_time': temporal_success.to_dict(),
            'xg_over_time': temporal_xg.to_dict() if not temporal_xg.empty else {},
            'peak_activity_minute': temporal_intensity.idxmax() if not temporal_intensity.empty else 0
        }
    
    def _analyze_zones(self) -> Dict:
        """Analyze spatial patterns by pitch zones"""
        print("🗺️ Analyzing spatial zones...")
        
        zone_analysis = self.events_df.groupby('pitch_zone').agg({
            'activity': 'count',
            'activity_result': lambda x: (x == 'success').mean(),
            'xg_added': 'sum',
            'team': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'unknown'
        }).round(3)
        
        zone_analysis.columns = ['total_events', 'success_rate', 'total_xg', 'dominant_team']
        
        # Sub-zone analysis
        subzone_analysis = self.events_df.groupby('sub_zone').size()
        
        return {
            'zone_stats': zone_analysis.to_dict('index'),
            'subzone_distribution': subzone_analysis.to_dict(),
            'most_active_zone': zone_analysis['total_events'].idxmax(),
            'highest_xg_zone': zone_analysis['total_xg'].idxmax()
        }
    
    def generate_process_map(self, save_path: str = "football_process_map"):
        """Generate and save process map"""
        if not PM4PY_AVAILABLE:
            print("PM4Py not available - cannot generate process map")
            return
            
        try:
            print("🗺️ Generating process map...")
            
            # Create Directly-Follows Graph
            dfg, start_activities, end_activities = pm4py.discover_dfg(self.event_log)
            
            # Save visualization
            pm4py.save_vis_dfg(dfg, start_activities, end_activities, f"{save_path}.png")
            print(f"✅ Process map saved: {save_path}.png")
            
            return dfg, start_activities, end_activities
            
        except Exception as e:
            print(f"⚠️ Error generating process map: {e}")
            return None, None, None
    
    def create_tactical_dashboard(self) -> dict:
        """Create tactical analysis visualizations"""
        if not PLOTLY_AVAILABLE:
            print("Plotly not available - creating matplotlib visualizations instead")
            return self._create_matplotlib_dashboard()
        
        print("📊 Creating interactive tactical dashboard...")
        
        dashboards = {}
        
        # 1. Activity distribution by zone
        zone_counts = self.events_df['pitch_zone'].value_counts()
        fig1 = go.Figure(data=[go.Bar(x=zone_counts.index, y=zone_counts.values)])
        fig1.update_layout(title='Activity Distribution by Pitch Zone')
        dashboards['zone_activity'] = fig1
        
        # 2. Team performance comparison
        team_stats = self.events_df.groupby('team').agg({
            'activity': 'count',
            'activity_result': lambda x: (x == 'success').mean()
        })
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='Total Actions',
            x=team_stats.index,
            y=team_stats['activity'],
            yaxis='y'
        ))
        fig2.add_trace(go.Scatter(
            name='Success Rate',
            x=team_stats.index,
            y=team_stats['activity_result'],
            yaxis='y2',
            mode='markers+lines'
        ))
        fig2.update_layout(
            title='Team Performance Comparison',
            yaxis=dict(title='Total Actions'),
            yaxis2=dict(title='Success Rate', overlaying='y', side='right')
        )
        dashboards['team_performance'] = fig2
        
        # 3. Activity timeline
        self.events_df['match_minute'] = self.events_df['timestamp'] // 60000
        timeline = self.events_df.groupby('match_minute').size()
        
        fig3 = go.Figure(data=go.Scatter(x=timeline.index, y=timeline.values, mode='lines'))
        fig3.update_layout(title='Activity Intensity Over Time', xaxis_title='Match Minute', yaxis_title='Events')
        dashboards['timeline'] = fig3
        
        return dashboards
    
    def _create_matplotlib_dashboard(self) -> dict:
        """Create dashboard using matplotlib when plotly is not available"""
        print("📊 Creating matplotlib dashboard...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Football Tactical Analysis Dashboard', fontsize=16)
        
        # 1. Activity by zone
        zone_counts = self.events_df['pitch_zone'].value_counts()
        axes[0, 0].bar(zone_counts.index, zone_counts.values)
        axes[0, 0].set_title('Activity Distribution by Zone')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Team comparison
        team_stats = self.events_df.groupby('team').agg({
            'activity': 'count',
            'activity_result': lambda x: (x == 'success').mean()
        })
        
        x = range(len(team_stats))
        axes[0, 1].bar(x, team_stats['activity'], alpha=0.7, label='Total Actions')
        ax2 = axes[0, 1].twinx()
        ax2.plot(x, team_stats['activity_result'], 'ro-', label='Success Rate')
        axes[0, 1].set_title('Team Performance')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(team_stats.index)
        axes[0, 1].legend(loc='upper left')
        ax2.legend(loc='upper right')
        
        # 3. Activity timeline
        self.events_df['match_minute'] = self.events_df['timestamp'] // 60000
        timeline = self.events_df.groupby('match_minute').size()
        axes[1, 0].plot(timeline.index, timeline.values)
        axes[1, 0].set_title('Activity Over Time')
        axes[1, 0].set_xlabel('Match Minute')
        axes[1, 0].set_ylabel('Events')
        
        # 4. Action type distribution
        action_counts = self.events_df['activity'].value_counts().head(10)
        axes[1, 1].pie(action_counts.values, labels=action_counts.index, autopct='%1.1f%%')
        axes[1, 1].set_title('Top 10 Action Types')
        
        plt.tight_layout()
        plt.savefig('football_dashboard.png', dpi=300, bbox_inches='tight')
        print("✅ Dashboard saved: football_dashboard.png")
        
        return {'matplotlib_dashboard': 'football_dashboard.png'}
    
    def export_analysis_report(self, filename: str = "football_analysis_report.md"):
        """Export comprehensive analysis report"""
        print("📝 Generating comprehensive analysis report...")
        
        analysis = self.analyze_tactical_patterns()
        
        report = f"""# Football Process Mining Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 Overview
- **Total Events**: {len(self.events_df):,}
- **Total Possessions**: {self.events_df['case_id'].nunique():,}
- **Teams**: {', '.join(self.events_df['team'].unique())}
- **Match Duration**: {self.events_df['timestamp'].max() / 60000:.1f} minutes

## ⚽ Possession Analysis
"""
        
        if 'possession_patterns' in analysis:
            poss = analysis['possession_patterns']
            report += f"""- **Average Possession Duration**: {poss['avg_possession_duration']:.0f}ms
- **Average Events per Possession**: {poss['avg_events_per_possession']:.1f}
- **Overall Success Rate**: {poss['avg_success_rate']:.1%}
- **Possessions by Team**: 
"""
            for team, count in poss['possession_by_team'].items():
                report += f"  - {team.upper()}: {count} possessions\n"
        
        report += "\n## ⚔️ Attacking Patterns\n"
        if 'attacking_patterns' in analysis:
            attack = analysis['attacking_patterns']
            if 'message' not in attack:
                report += f"""- **Total Attacking Events**: {attack['total_attacking_events']:,}
- **Attack Success Rate**: {attack['attack_success_rate']:.1%}
- **Total Shots**: {attack['total_shots']}
- **Shot Success Rate**: {attack['shot_success_rate']:.1%}
- **Total xG**: {attack['xg_total']:.3f}

### Top Attack Progressions:
"""
                for i, (pattern, count) in enumerate(attack['common_progressions'][:5], 1):
                    report += f"{i}. {pattern}: {count} times\n"
        
        report += "\n## 🛡️ Defensive Analysis\n"
        if 'defensive_patterns' in analysis:
            defense = analysis['defensive_patterns']
            if 'message' not in defense:
                report += f"""- **Total Defensive Events**: {defense['total_defensive_events']:,}
- **Defensive Success Rate**: {defense['defensive_success_rate']:.1%}
- **Avg Defensive Actions per Possession**: {defense['avg_defensive_actions_per_possession']:.1f}

### Pressure by Zone:
"""
                for zone, pressure in defense['pressure_by_zone'].items():
                    report += f"- {zone}: {pressure} defensive actions\n"
        
        report += "\n## ⚖️ Team Comparison\n"
        if 'team_comparison' in analysis:
            for team, stats in analysis['team_comparison'].items():
                report += f"""
### {team.upper()} Team:
- **Total Actions**: {stats['total_actions']:,}
- **Success Rate**: {stats['success_rate']:.1%}
- **Possessions**: {stats['possessions']}
- **Total xG**: {stats['total_xg']:.3f}
- **Most Active Zone**: {stats['most_active_zone']}
"""
        
        report += "\n## 🗺️ Spatial Analysis\n"
        if 'zone_analysis' in analysis:
            zones = analysis['zone_analysis']
            report += f"""- **Most Active Zone**: {zones['most_active_zone']}
- **Highest xG Zone**: {zones['highest_xg_zone']}

### Zone Statistics:
"""
            for zone, stats in zones['zone_stats'].items():
                report += f"""**{zone}**:
- Events: {stats['total_events']}, Success Rate: {stats['success_rate']:.1%}, xG: {stats['total_xg']:.3f}
"""
        
        report += "\n## ⏱️ Temporal Analysis\n"
        if 'temporal_patterns' in analysis:
            temporal = analysis['temporal_patterns']
            report += f"- **Peak Activity Minute**: {temporal['peak_activity_minute']}\n"
        
        report += f"""
## 🎯 Key Insights

1. **Tactical Dominance**: Analysis of possession and zone control
2. **Attacking Efficiency**: xG generation and shot conversion rates
3. **Defensive Organization**: Pressure patterns and success rates
4. **Process Patterns**: Most common tactical sequences

---
*Generated by Football ABM Process Mining Analysis*
"""
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"✅ Analysis report saved: {filename}")
        return filename
