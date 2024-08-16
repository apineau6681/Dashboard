import subprocess
import os

# Define a function to run a script
def run_script(script_name):
    try:
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, script_name)
        result = subprocess.run(['python', script_path], check=True, capture_output=True, text=True,cwd=".")
        print(f"Output of {script_name}:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}:")
        print(e.stderr)

# List of scripts to be executed
scripts = ['get_BTC_data.py', 'get_BTC_ROI.py', 'get_crypto_prices.py','get_youtube_subscribers.py','get_google_trends.py','get_google_trends_nb_days.py','get_futures_rates']

# Execute each script
for script in scripts:
    run_script(script)