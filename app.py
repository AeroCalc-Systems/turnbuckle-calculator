from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    mode = data.get('mode', 'analysis') # Check if we are in 'design' or 'analysis' mode
    yield_strength = float(data['yield_strength'])

    # --- MODE 1: REVERSE DESIGN (Find the Bolt) ---
    if mode == 'design':
        required_load = float(data['load'])
        
        # Dictionary of Standard Metric Coarse Threads (Dia: Pitch)
        # We search through these to find the first one that fits.
        standard_sizes = {
            6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 
            20: 2.5, 24: 3.0, 30: 3.5, 36: 4.0
        }
        
        recommended_size = "M36+" # Default if load is huge
        safety_factor = 1.5 # Engineering standard buffer

        for d, p in standard_sizes.items():
            # Calculate capacity of this size
            stress_diameter = d - (0.938194 * p)
            area = (3.14159 / 4) * (stress_diameter ** 2)
            capacity = yield_strength * area
            
            # If this bolt is strong enough (including safety factor), pick it!
            if capacity >= (required_load * safety_factor):
                recommended_size = f"M{d} (Pitch {p}mm)"
                return jsonify({
                    'result_text': f"Recommended Size: {recommended_size}",
                    'details': f"Capacity: {round(capacity, 0)} N"
                })

        return jsonify({
            'result_text': "Load too high for standard bolts!",
            'details': "Try a higher strength material."
        })

    # --- MODE 2: ANALYSIS (Existing Logic) ---
    else:
        d = float(data['diameter'])
        p = float(data['pitch'])
        
        stress_diameter = d - (0.938194 * p)
        area = (3.14159 / 4) * (stress_diameter ** 2)
        failure_load = yield_strength * area

        return jsonify({
            'failure_load': round(failure_load, 2),
            'unit': 'N'
        })

if __name__ == '__main__':
    app.run(debug=True)