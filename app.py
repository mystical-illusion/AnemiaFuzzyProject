from flask import Flask, render_template, request, url_for, flash, redirect
# CRITICAL FIX: Set Matplotlib backend to non-interactive to prevent pop-up windows
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 

from skfuzzy import control as ctrl 
import plotly.graph_objs as go
import plotly.offline as pyo
import numpy as np
import sys
import os 
from io import BytesIO

# Import the fuzzy variables and control system from the logic file
try:
    from fuzzy_anemia import detect_anemia, hgb, mcv, mchc, system, anemia 
except ImportError as e:
    print(f"FATAL ERROR: Could not import fuzzy_anemia components: {e}", file=sys.stderr)
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'a_secure_random_string_for_flask_session' 


@app.route('/')
def home():
    """Renders the main input form (index.html)."""
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    """
    Receives form data, runs diagnosis, saves the fuzzy plot, and renders result.html.
    """
    try:
        # Input Processing
        hgb_val = float(request.form.get('hgb'))
        mcv_val = float(request.form.get('mcv'))
        mchc_val = float(request.form.get('mchc'))

        # Run Fuzzy Logic
        sim = ctrl.ControlSystemSimulation(system)
        sim.input['hgb'] = hgb_val
        sim.input['mcv'] = mcv_val
        sim.input['mchc'] = mchc_val
        sim.compute()
        anemia_type = detect_anemia(hgb_val, mcv_val, mchc_val)

        # Generate and Save the Fuzzy Diagnosis Plot
        fig, ax = plt.subplots(figsize=(7, 5))
        anemia.view(sim=sim, ax=ax) 
        ax.set_title(f'Diagnosis: {anemia_type} | Result Index: {sim.output["anemia"]:.2f}')

        plot_filename = f'diagnosis_plot_{os.getpid()}.png'
        plot_path = os.path.join(app.root_path, 'static', plot_filename)
        
        fig.savefig(plot_path, bbox_inches='tight')
        plt.close(fig) # Prevents desktop pop-up window
        
        plot_url = url_for('static', filename=plot_filename)
        
        return render_template('result.html', 
                               diagnosis=anemia_type,
                               hgb=hgb_val, 
                               mcv=mcv_val, 
                               mchc=mchc_val,
                               plot_url=plot_url)
    
    except Exception as e:
        flash(f"Error processing input: {e}. Please ensure all fields contain valid numbers.")
        return redirect(url_for('home'))


@app.route('/graph')
def graph():
    """Generates and displays Plotly graphs of the membership functions."""
    graphs = []
    
    for var, name in [(hgb, 'Hemoglobin (HGB)'), (mcv, 'MCV'), (mchc, 'MCHC')]:
        data = []
        for label, term in var.terms.items():
            # CRITICAL FIX: Convert NumPy arrays to Python lists for Plotly serialization
            x_data = var.universe.tolist()
            y_data = term.mf.tolist()
            
            data.append(go.Scatter(
                x=x_data,
                y=y_data,
                mode='lines',
                name=label
            ))
        
        layout = go.Layout(
            title=f'{name} Membership Function',
            xaxis=dict(title=f'{name} Values'),
            yaxis=dict(title='Membership Degree', range=[0, 1.05]),
            template='plotly_white',
            height=400 
        )
        
        fig = go.Figure(data=data, layout=layout)
        graphs.append(pyo.plot(fig, output_type='div', include_plotlyjs=False)) 

    return render_template('graph.html', graphs=graphs)


if __name__ == "__main__":
    app.run(debug=True)