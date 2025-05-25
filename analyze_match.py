#!/usr/bin/env python3
"""
Football Match Process Mining Analysis Script
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from abm.simulation.football_simulation import FootballSimulation
from abm.analysis.process_mining import FootballProcessMining

def run_analysis():
    print("🏈 Football Process Mining Analysis")
    print("=" * 50)
    
    # Option 1: Analyze existing CSV file
    csv_files = [f for f in os.listdir('.') if f.startswith('football_events_') and f.endswith('.csv')]
    
    if csv_files:
        # Use the most recent file
        latest_file = max(csv_files, key=lambda f: os.path.getmtime(f))
        print(f"📂 Loading existing data: {latest_file}")
        events_df = pd.read_csv(latest_file)
        print(f"   - Events loaded: {len(events_df):,}")
        print(f"   - Possessions: {events_df['case_id'].nunique():,}")
        print(f"   - Teams: {', '.join(events_df['team'].unique())}")
    else:
        # Option 2: Run new simulation
        print("🎮 No existing data found. Running new simulation...")
        simulation = FootballSimulation(home_formation="4-4-2", away_formation="4-4-2")
        events_df = simulation.run_simulation(duration_minutes=5)
        
        # Save the data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"football_events_{timestamp}.csv"
        events_df.to_csv(csv_filename, index=False)
        print(f"💾 Data saved: {csv_filename}")
    
    # Initialize process mining analysis
    print("\n🔍 Initializing Process Mining Analysis...")
    pm_analyzer = FootballProcessMining(events_df)
    
    # Discover process models
    print("\n🧠 Discovering Process Models...")
    models = pm_analyzer.discover_process_models()
    if models:
        print(f"✅ Discovered {len(models)} process models: {list(models.keys())}")
    else:
        print("⚠️ No process models discovered (PM4Py may not be installed)")
    
    # Analyze tactical patterns
    print("\n⚽ Analyzing Tactical Patterns...")
    tactical_analysis = pm_analyzer.analyze_tactical_patterns()
    
    # Generate process map
    print("\n🗺️ Generating Process Map...")
    try:
        dfg_result = pm_analyzer.generate_process_map("football_process_map")
        if dfg_result[0] is not None:
            print("✅ Process map generated successfully")
        else:
            print("⚠️ Process map generation failed")
    except Exception as e:
        print(f"⚠️ Could not generate process map: {e}")
    
    # Create dashboard
    print("\n📊 Creating Tactical Dashboard...")
    try:
        dashboards = pm_analyzer.create_tactical_dashboard()
        if 'matplotlib_dashboard' in dashboards:
            print("✅ Matplotlib dashboard created")
        else:
            # Save plotly dashboards
            for name, fig in dashboards.items():
                filename = f"tactical_dashboard_{name}.html"
                fig.write_html(filename)
                print(f"✅ Dashboard saved: {filename}")
    except Exception as e:
        print(f"⚠️ Dashboard creation failed: {e}")
    
    # Export comprehensive report
    print("\n📝 Generating Analysis Report...")
    try:
        report_file = pm_analyzer.export_analysis_report("football_analysis_report.md")
        print(f"✅ Report saved: {report_file}")
    except Exception as e:
        print(f"⚠️ Report generation failed: {e}")
    
    # Export to XES for advanced PM tools
    print("\n📤 Exporting to XES format...")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        xes_filename = f"football_events_{timestamp}.xes"
        events_df_temp = events_df.copy()
        
        # Create a simple event logger instance to use export method
        from abm.logging.event_logger import FootballEventLogger
        temp_logger = FootballEventLogger()
        temp_logger.events = events_df.to_dict('records')
        temp_logger.export_to_xes(xes_filename)
        
    except Exception as e:
        print(f"⚠️ XES export failed: {e}")
    
    # Print summary
    print("\n" + "="*50)
    print("📈 ANALYSIS SUMMARY")
    print("="*50)
    print(f"📊 Total Events: {len(events_df):,}")
    print(f"🎯 Total Possessions: {events_df['case_id'].nunique():,}")
    print(f"⚽ Average Events per Possession: {len(events_df) / events_df['case_id'].nunique():.1f}")
    
    if 'possession_patterns' in tactical_analysis:
        poss = tactical_analysis['possession_patterns']
        print(f"⏱️ Average Possession Duration: {poss['avg_possession_duration']:.0f}ms")
        print(f"✅ Overall Success Rate: {poss['avg_success_rate']:.1%}")
    
    if 'attacking_patterns' in tactical_analysis:
        attack = tactical_analysis['attacking_patterns']
        if 'message' not in attack:
            print(f"⚔️ Attack Success Rate: {attack['attack_success_rate']:.1%}")
            print(f"🥅 Total Shots: {attack['total_shots']}")
            if attack['total_shots'] > 0:
                print(f"🎯 Shot Success Rate: {attack['shot_success_rate']:.1%}")
            print(f"📈 Total xG: {attack['xg_total']:.3f}")
    
    if 'team_comparison' in tactical_analysis:
        print("\n🏆 Team Performance:")
        for team, stats in tactical_analysis['team_comparison'].items():
            print(f"   {team.upper()}: {stats['success_rate']:.1%} success rate, {stats['total_xg']:.2f} xG")
    
    if 'zone_analysis' in tactical_analysis:
        zones = tactical_analysis['zone_analysis']
        print(f"\n🗺️ Most Active Zone: {zones['most_active_zone']}")
        print(f"🎯 Highest xG Zone: {zones['highest_xg_zone']}")
    
    print(f"\n🎊 Analysis complete! Check generated files for detailed insights.")
    
    return pm_analyzer, tactical_analysis

def install_dependencies():
    """Install required dependencies for process mining"""
    print("📦 Installing process mining dependencies...")
    
    try:
        import subprocess
        
        packages = ['pm4py', 'matplotlib', 'plotly', 'graphviz']
        for package in packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        print("✅ All dependencies installed successfully!")
        
    except Exception as e:
        print(f"⚠️ Error installing dependencies: {e}")
        print("Please manually install: pip install pm4py matplotlib plotly graphviz")

if __name__ == "__main__":
    # Check if user wants to install dependencies
    if len(sys.argv) > 1 and sys.argv[1] == '--install-deps':
        install_dependencies()
        sys.exit(0)
    
    try:
        analyzer, analysis = run_analysis()
    except ImportError as e:
        print(f"⚠️ Missing dependencies: {e}")
        print("Run with --install-deps to install required packages:")
        print("python analyze_match.py --install-deps")
