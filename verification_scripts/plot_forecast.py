import sys
import os
import asyncio
import json
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WORKER_DIR = os.path.join(PROJECT_ROOT, 'forecastWorker')

# Add worker to path so we can import app modules
sys.path.append(WORKER_DIR)

# Change working directory so asset paths (app/assets/...) work correctly
os.chdir(WORKER_DIR)

# Import application logic from the worker codebase
from app.users.infrastructure.repositories import UserRepository
from app.forecastSystem.infrastructure.repositories import ForecastWorkerRepository

async def generate_plot():
    print("--- 1. Authenticating ---")
    
    # Load env vars from project root
    load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
    
    api_user = os.getenv("API_USER")
    api_pass = os.getenv("API_PASSWORD")
    
    # Force API URL to localhost since we are running on host
    os.environ["BACKEND_API_URL"] = "http://localhost:8000"
    
    if not api_user or not api_pass:
        print("Error: API_USER or API_PASSWORD not set in .env")
        return

    user_repo = UserRepository()
    try:
        user_session = await user_repo.login(api_user, api_pass)
        print(f"Logged in as {api_user}")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    repo = ForecastWorkerRepository()
    forecast_id = 1
    data_id = 10  # Obtained from DB query (max ID)
    
    print(f"--- 2. Fetching Data for System {forecast_id}, Data {data_id} ---")
    
    try:
        system = await repo.get_forecast_system(forecast_id, user_session)
        zones = await repo.get_forecast_zones(forecast_id, user_session)
        hindcast_data = await repo.get_hindcast_data(data_id, user_session)
        
        print(f"System: {system.name}")
        print(f"Zones: {len(zones)}")
        
        print("--- 3. Running Scientific Pipeline ---")
        
        # Calibration
        print("Calibrating...")
        calibrated_data = await repo.calibration_hindcast_data(
            download_data=hindcast_data,
            hinccast_point_id=system.hindcast_point_id,
            requester=user_session
        )
        
        # Hypercube
        print("Generating Hypercube...")
        hypercube = repo.create_hypercube(
            Hsig=[0.1, 1, 2, 3, 5, 7, 9, 11, 14],
            Tp=[5, 8, 10, 13, 16, 19, 25],
            Dir=[270, 292.5, 315, 337.5, 0, 22.5, 45, 67.5, 90],
            Nivel=[0, 4.5]
        )
        
        # Propagation
        print("Propagating...")
        results_json = repo.propagation(
            hindcast=calibrated_data,
            zones=zones,
            hypercube=hypercube
        )
        
        results = json.loads(results_json)
        
        print("--- 4. Generating Plot ---")
        
        # Plotting
        plt.figure(figsize=(12, 6))
        
        # --- Plot Input Data (Downloaded) ---
        input_hourly = hindcast_data.data.get("hourly", {})
        input_time = pd.to_datetime(input_hourly.get("time", []))
        
        # Find all wave height keys in input data
        for key in input_hourly.keys():
            if key.startswith("wave_height_"):
                model_name = key.replace("wave_height_", "")
                hs_values = input_hourly[key]
                # Plot input as dashed lines with lower opacity
                plt.plot(input_time, hs_values, linestyle='--', alpha=0.6, 
                         label=f"Input (Hindcast) - {model_name}")

        # --- Plot Output Data (Forecast) ---
        for model_name, model_data in results.items():
            if not model_data.get("timestamps"):
                continue
                
            timestamps = pd.to_datetime(model_data["timestamps"])
            
            for zone_name, zone_data in model_data["zones"].items():
                hs_values = zone_data["Hs"]
                label = f"Output (Forecast) - {model_name} - {zone_name}"
                plt.plot(timestamps, hs_values, label=label)
        
        plt.title(f"Wave Height Forecast (Input vs Output) - {system.name}")
        plt.xlabel("Date")
        plt.ylabel("Significant Wave Height (Hs) [m]")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        
        # Save to the verification script folder
        output_path = os.path.join(PROJECT_ROOT, "verification_scripts", "forecast_results.png")
        plt.savefig(output_path)
        print(f"Plot saved to: {output_path}")

        # --- 5. Generate Comparison Tables (Visual Style) ---
        print("--- 5. Generating Styled Comparison Tables ---")
        
        # Helper function for color scale (Wave Height)
        # Blue (<1m) -> Green (1-2m) -> Yellow (2-3m) -> Orange (3-5m) -> Red (>5m)
        def get_color(val):
            if pd.isna(val): return "#ffffff"
            if val < 0.5: return "#e0f7fa" # Light Cyan
            if val < 1.0: return "#b2ebf2" # Cyan
            if val < 1.5: return "#a5d6a7" # Green
            if val < 2.0: return "#fff59d" # Yellow
            if val < 3.0: return "#ffcc80" # Orange
            if val < 5.0: return "#ffab91" # Light Red
            return "#ef9a9a" # Red

        # Collect data structure as before
        input_hourly = hindcast_data.data.get("hourly", {})
        input_time = pd.to_datetime(input_hourly.get("time", []))
        
        # We'll create a DataFrame for each Zone where:
        # Index (Rows) = "Model Name (Input/Output)"
        # Columns = Time
        
        # Filter time range: Let's take the first 24h or 48h for readability, 
        # picking every 3rd hour to match the "3-hourly" look of the screenshot if dense,
        # or just hourly if it fits. The screenshot showed 4, 7, 10...
        
        # Let's align on common timestamps for all models/inputs
        # We assume 'results' dictates the relevant forecast period.
        timestamps = None
        for m in results.values():
            if m.get("timestamps"):
                timestamps = pd.to_datetime(m["timestamps"])
                break
        
        if timestamps is None:
            print("No output timestamps found.")
            return

        # Filter to a manageable window (e.g., first 24 hours) for the static image
        # and re-sample to 3-hourly to mimic the style
        display_times = timestamps[:24] # First 24 steps (assuming hourly)
        # If we want 3-hourly: 
        # display_times = [t for i, t in enumerate(timestamps) if i % 3 == 0][:10]
        
        # Prepare data map: zone -> { row_label: series }
        zone_rows = {} 
        
        for model_name, model_data in results.items():
            if not model_data.get("timestamps"):
                continue
                
            model_times = pd.to_datetime(model_data["timestamps"])
            
            # Input Data (Hindcast) for this model
            input_key = f"wave_height_{model_name}"
            input_series = None
            if input_key in input_hourly:
                 # Reindex input to match output times
                 temp_series = pd.Series(input_hourly[input_key], index=input_time)
                 # Reindex to the display times, filling missing with NaN
                 input_series = temp_series.reindex(display_times)

            for zone_name, z_data in model_data["zones"].items():
                if zone_name not in zone_rows:
                    zone_rows[zone_name] = {}
                
                # Output Series
                out_vals = pd.Series(z_data["Hs"], index=model_times).reindex(display_times)
                
                # Add rows. Group Input/Output for comparison
                # We prefix with model name to sort them together
                if input_series is not None:
                    zone_rows[zone_name][f"{model_name} [IN]"] = input_series
                zone_rows[zone_name][f"{model_name} [OUT]"] = out_vals

        # Generate styled plots for each zone
        for zone_name, rows_dict in zone_rows.items():
            print(f"Generating styled table for: {zone_name}")
            
            # Create DataFrame: Rows=Models, Cols=Time
            df_table = pd.DataFrame(rows_dict)
            # Transpose so Time is columns
            df_table = df_table.T
            
            # Sort index to keep IN/OUT pairs together
            df_table = df_table.sort_index()
            
            # Format Columns as HH:MM
            df_table.columns = df_table.columns.strftime('%d-%Hh')
            
            if df_table.empty:
                continue

            # Plot using Matplotlib
            num_cols = len(df_table.columns)
            num_rows = len(df_table)
            
            # Calculate size
            col_width = 1.2
            row_height = 0.6
            fig_width = max(10, num_cols * col_width + 3) # Add space for row labels
            fig_height = max(4, num_rows * row_height + 2)
            
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            ax.axis('off')
            
            # Create table
            # cellText values formatted to 2 decimals
            cell_text = df_table.round(2).fillna("-").astype(str).values
            
            the_table = ax.table(
                cellText=cell_text,
                rowLabels=df_table.index,
                colLabels=df_table.columns,
                loc='center',
                cellLoc='center'
            )
            
            # Styling
            the_table.auto_set_font_size(False)
            the_table.set_fontsize(11)
            the_table.scale(1, 1.8) # More padding height
            
            # Iterating cells to apply colors
            # Table cells are (row, col). Header is row=0.
            # Data cells start at (1, 0) in matplotlib table coordinates? 
            # Actually keys are (row, col). Row 0 is header. Cols start at -1 (row label).
            
            for (row, col), cell in the_table.get_celld().items():
                cell.set_edgecolor('white') # Clean look
                cell.set_linewidth(1)
                
                if row == 0:
                    # Header Row
                    cell.set_text_props(weight='bold', color='white')
                    cell.set_facecolor('#455a64') # Dark headers
                elif col == -1:
                    # Row Labels
                    cell.set_text_props(weight='bold')
                    cell.set_facecolor('#f5f5f5')
                else:
                    # Data Cells
                    try:
                        val_str = cell_text[row-1][col] # row-1 because table includes header
                        if val_str != "-":
                            val = float(val_str)
                            color = get_color(val)
                            cell.set_facecolor(color)
                        else:
                            cell.set_facecolor('#eceff1')
                    except Exception:
                        pass

            plt.title(f"Forecast Comparison - {zone_name}", fontsize=16, y=0.95)
            
            safe_zone_name = zone_name.replace(" ", "_")
            png_path = os.path.join(PROJECT_ROOT, "verification_scripts", f"styled_table_{safe_zone_name}.png")
            plt.savefig(png_path, bbox_inches='tight', dpi=150)
            print(f"   Styled Image saved: {png_path}")
            plt.close()


    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_plot())
