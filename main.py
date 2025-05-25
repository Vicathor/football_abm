import logging
import pandas as pd
from datetime import datetime

from abm.simulation.football_simulation import FootballSimulation

def main():
    """Main execution function"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("🏈 Football Tactics Simulation Starting...")
    print("=" * 50)
    
    # Create and run simulation
    simulation = FootballSimulation(home_formation="4-4-2", away_formation="4-4-2")
    
    # Run a 2-minute match for testing
    events_df = simulation.run_simulation(duration_minutes=2)
    
    # Display results
    print(f"\n📊 Simulation Results:")
    print(f"Final Score: Home {simulation.score['home']} - {simulation.score['away']} Away")
    print(f"Total Events Logged: {len(events_df)}")
    print(f"Unique Possessions: {events_df['case_id'].nunique()}")
    
    # Display event summary
    print(f"\n📈 Event Summary:")
    print(events_df['activity'].value_counts().head(10))
    
    # Export data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"football_events_{timestamp}.csv"
    events_df.to_csv(csv_filename, index=False)
    print(f"\n💾 Events exported to: {csv_filename}")
    
    # Display sample events
    print(f"\n🔍 Sample Events:")
    print(events_df[['case_id', 'activity', 'player_role', 'team', 'pitch_zone', 'activity_result']].head(10))
    
    return events_df

if __name__ == "__main__":
    events_df = main()