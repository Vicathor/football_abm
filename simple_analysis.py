#!/usr/bin/env python3
"""
Simple Football Process Mining Analysis
"""

import pandas as pd
import sys
import os
from datetime import datetime
import matplotlib.pyplot as plt

def analyze_football_data():
    print("🏈 Football Process Mining Analysis")
    print("=" * 50)
    
    # Load the most recent CSV file
    csv_files = [f for f in os.listdir('.') if f.startswith('football_events_') and f.endswith('.csv')]
    
    if not csv_files:
        print("❌ No football event files found!")
        return
    
    # Use the most recent file
    latest_file = max(csv_files, key=lambda f: os.path.getmtime(f))
    print(f"📂 Loading data from: {latest_file}")
    
    # Load data
    events_df = pd.read_csv(latest_file)
    print(f"📊 Loaded {len(events_df):,} events from {events_df['case_id'].nunique():,} possessions")
    
    # Basic Analysis
    print("\n🔍 BASIC ANALYSIS")
    print("=" * 30)
    
    # 1. Event distribution
    print("📈 Top 10 Activities:")
    activity_counts = events_df['activity'].value_counts().head(10)
    for activity, count in activity_counts.items():
        print(f"   {activity}: {count:,}")
    
    # 2. Team comparison
    print(f"\n⚖️ Team Performance:")
    team_stats = events_df.groupby('team').agg({
        'activity': 'count',
        'activity_result': lambda x: (x == 'success').mean(),
        'case_id': 'nunique',
        'xg_added': 'sum'
    }).round(3)
    
    for team in team_stats.index:
        stats = team_stats.loc[team]
        print(f"   {team.upper()}: {stats['activity']:,} actions, {stats['activity_result']:.1%} success, {stats['case_id']} possessions, {stats['xg_added']:.3f} xG")
    
    # 3. Possession analysis
    print(f"\n⚽ Possession Analysis:")
    possession_stats = events_df.groupby('case_id').agg({
        'activity': 'count',
        'team': 'first',
        'timestamp': ['min', 'max'],
        'activity_result': lambda x: (x == 'success').mean()
    })
    possession_stats.columns = ['events', 'team', 'start_time', 'end_time', 'success_rate']
    possession_stats['duration'] = possession_stats['end_time'] - possession_stats['start_time']
    
    print(f"   Average possession duration: {possession_stats['duration'].mean():.0f}ms")
    print(f"   Average events per possession: {possession_stats['events'].mean():.1f}")
    print(f"   Overall success rate: {possession_stats['success_rate'].mean():.1%}")
    
    # 4. Zone analysis
    print(f"\n🗺️ Spatial Analysis:")
    zone_stats = events_df['pitch_zone'].value_counts()
    for zone, count in zone_stats.items():
        percentage = (count / len(events_df)) * 100
        print(f"   {zone}: {count:,} events ({percentage:.1f}%)")
    
    # 5. Attack patterns
    print(f"\n⚔️ Attack Pattern Analysis:")
    attacking_events = events_df[events_df['activity'].isin(['pass', 'dribble', 'shot', 'cross'])]
    
    if len(attacking_events) > 0:
        # Find common zone progressions
        attack_progressions = {}
        for case_id in attacking_events['case_id'].unique():
            case_events = attacking_events[attacking_events['case_id'] == case_id]
            zones = case_events['pitch_zone'].tolist()
            
            for i in range(len(zones) - 1):
                progression = f"{zones[i]} → {zones[i+1]}"
                attack_progressions[progression] = attack_progressions.get(progression, 0) + 1
        
        print("   Top 5 zone progressions:")
        sorted_progressions = sorted(attack_progressions.items(), key=lambda x: x[1], reverse=True)
        for progression, count in sorted_progressions[:5]:
            print(f"     {progression}: {count} times")
    
    # 6. Shot analysis
    shots = events_df[events_df['activity'] == 'shot']
    if len(shots) > 0:
        goals = shots[shots['activity_result'] == 'goal']
        print(f"\n🥅 Shot Analysis:")
        print(f"   Total shots: {len(shots)}")
        print(f"   Goals scored: {len(goals)}")
        print(f"   Conversion rate: {len(goals)/len(shots):.1%}")
        print(f"   Total xG: {shots['xg_added'].sum():.3f}")
    
    # Create visualizations
    print(f"\n📊 Creating Visualizations...")
    create_basic_visualizations(events_df, latest_file.replace('.csv', ''))
    
    # Generate report
    generate_report(events_df, team_stats, possession_stats, zone_stats)
    
    print(f"\n✅ Analysis Complete!")
    print(f"📁 Check generated files: football_dashboard.png, analysis_report.md")

def create_basic_visualizations(events_df, filename_base):
    """Create basic visualizations using matplotlib"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Football Match Analysis Dashboard', fontsize=16)
    
    # 1. Activity distribution
    activity_counts = events_df['activity'].value_counts().head(10)
    axes[0, 0].bar(range(len(activity_counts)), activity_counts.values)
    axes[0, 0].set_title('Top 10 Activities')
    axes[0, 0].set_xticks(range(len(activity_counts)))
    axes[0, 0].set_xticklabels(activity_counts.index, rotation=45, ha='right')
    
    # 2. Zone distribution
    zone_counts = events_df['pitch_zone'].value_counts()
    axes[0, 1].pie(zone_counts.values, labels=zone_counts.index, autopct='%1.1f%%')
    axes[0, 1].set_title('Activity by Pitch Zone')
    
    # 3. Timeline
    events_df['match_minute'] = events_df['timestamp'] // 60000
    timeline = events_df.groupby('match_minute').size()
    axes[1, 0].plot(timeline.index, timeline.values, marker='o')
    axes[1, 0].set_title('Activity Over Time')
    axes[1, 0].set_xlabel('Match Minute')
    axes[1, 0].set_ylabel('Events')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Team comparison
    team_stats = events_df.groupby('team').agg({
        'activity': 'count',
        'activity_result': lambda x: (x == 'success').mean()
    })
    
    x = range(len(team_stats))
    bars = axes[1, 1].bar(x, team_stats['activity'], alpha=0.7, label='Total Actions')
    ax2 = axes[1, 1].twinx()
    line = ax2.plot(x, team_stats['activity_result'], 'ro-', label='Success Rate')
    
    axes[1, 1].set_title('Team Performance')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(team_stats.index)
    axes[1, 1].set_ylabel('Total Actions')
    ax2.set_ylabel('Success Rate')
    axes[1, 1].legend(loc='upper left')
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig('football_dashboard.png', dpi=300, bbox_inches='tight')
    print(f"   ✅ Dashboard saved: football_dashboard.png")

def generate_report(events_df, team_stats, possession_stats, zone_stats):
    """Generate a markdown analysis report"""
    
    report = f"""# Football Match Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Match Overview
- **Total Events**: {len(events_df):,}
- **Total Possessions**: {events_df['case_id'].nunique():,}
- **Match Duration**: {events_df['timestamp'].max() / 60000:.1f} minutes
- **Teams**: {', '.join(events_df['team'].unique())}

## ⚽ Key Statistics

### Team Performance
"""
    
    for team in team_stats.index:
        stats = team_stats.loc[team]
        report += f"""
**{team.upper()} Team:**
- Total Actions: {stats['activity']:,}
- Success Rate: {stats['activity_result']:.1%}
- Possessions: {stats['case_id']}
- Total xG: {stats['xg_added']:.3f}
"""
    
    report += f"""
### Possession Analysis
- Average Possession Duration: {possession_stats['duration'].mean():.0f}ms
- Average Events per Possession: {possession_stats['events'].mean():.1f}
- Overall Success Rate: {possession_stats['success_rate'].mean():.1%}

### Spatial Distribution
"""
    
    for zone, count in zone_stats.items():
        percentage = (count / len(events_df)) * 100
        report += f"- {zone}: {count:,} events ({percentage:.1f}%)\n"
    
    # Shot analysis
    shots = events_df[events_df['activity'] == 'shot']
    if len(shots) > 0:
        goals = shots[shots['activity_result'] == 'goal']
        report += f"""
### Shot Analysis
- Total Shots: {len(shots)}
- Goals Scored: {len(goals)}
- Conversion Rate: {len(goals)/len(shots):.1%}
- Total xG: {shots['xg_added'].sum():.3f}
"""
    
    report += f"""
## 📈 Top Activities
"""
    
    activity_counts = events_df['activity'].value_counts().head(10)
    for i, (activity, count) in enumerate(activity_counts.items(), 1):
        percentage = (count / len(events_df)) * 100
        report += f"{i}. {activity}: {count:,} ({percentage:.1f}%)\n"
    
    report += f"""
## 🎯 Key Insights

1. **Activity Distribution**: The match shows a balanced mix of tactical activities with {activity_counts.index[0]} being the most common action.

2. **Possession Quality**: Teams maintained an average of {possession_stats['events'].mean():.1f} events per possession with {possession_stats['success_rate'].mean():.1%} success rate.

3. **Spatial Patterns**: Most activity occurred in the {zone_stats.index[0]} ({zone_stats.iloc[0]:,} events).

4. **Match Tempo**: The simulation generated {len(events_df):,} events over {events_df['timestamp'].max() / 60000:.1f} minutes, averaging {len(events_df) / (events_df['timestamp'].max() / 60000):.0f} events per minute.

---
*Generated by Football ABM Process Mining Analysis*
"""
    
    with open('analysis_report.md', 'w') as f:
        f.write(report)
    
    print(f"   ✅ Report saved: analysis_report.md")

if __name__ == "__main__":
    try:
        analyze_football_data()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
