import numpy as np
from skfuzzy import control as ctrl
import skfuzzy as fuzz

# --------------------------------------------------------------------------
# Define Antecedent/Consequent Variables with wide ranges for Plotly
# --------------------------------------------------------------------------
# HGB: Range 5 to 19 g/dL
hgb = ctrl.Antecedent(np.arange(5, 19.1, 0.1), 'hgb')  
# MCV: Range 60 to 121 fL
mcv = ctrl.Antecedent(np.arange(60, 121, 0.1), 'mcv') 
# MCHC: Range 28 to 41 g/dL
mchc = ctrl.Antecedent(np.arange(28, 41.1, 0.1), 'mchc') 
# Anemia Output: Range 0 to 9 (Represents 9 types)
anemia = ctrl.Consequent(np.arange(0, 9.1, 0.1), 'anemia')

# --- HGB Membership Functions ---
hgb['low'] = fuzz.trapmf(hgb.universe, [5, 5, 10, 12])
hgb['normal'] = fuzz.trimf(hgb.universe, [11, 14, 16])
hgb['high'] = fuzz.trapmf(hgb.universe, [15, 17, 19.1, 19.1])

# --- MCV Membership Functions ---
mcv['low'] = fuzz.trapmf(mcv.universe, [60, 60, 70, 80])
mcv['normal'] = fuzz.trimf(mcv.universe, [78, 95, 110])
mcv['high'] = fuzz.trapmf(mcv.universe, [100, 115, 121, 121])

# --- MCHC Membership Functions ---
mchc['low'] = fuzz.trapmf(mchc.universe, [28, 28, 30, 32])
mchc['normal'] = fuzz.trimf(mchc.universe, [31, 34, 37])
mchc['high'] = fuzz.trapmf(mchc.universe, [35, 38, 41.1, 41.1])

# --- Anemia Output Membership Functions ---
anemia['Normal'] = fuzz.trimf(anemia.universe, [0, 0.5, 1])
anemia['Micro_Hypo'] = fuzz.trimf(anemia.universe, [0.5, 1.5, 2.5])
anemia['Micro_Normo'] = fuzz.trimf(anemia.universe, [1.5, 2.5, 3.5])
anemia['Micro_Hyper'] = fuzz.trimf(anemia.universe, [2.5, 3.5, 4.5])
anemia['Normo_Hypo'] = fuzz.trimf(anemia.universe, [3.5, 4.5, 5.5])
anemia['Normo_Normo'] = fuzz.trimf(anemia.universe, [4.5, 5.5, 6.5])
anemia['Normo_Hyper'] = fuzz.trimf(anemia.universe, [5.5, 6.5, 7.5])
anemia['Macro_Hypo'] = fuzz.trimf(anemia.universe, [6.5, 7.5, 8.5])
anemia['Macro_Normo'] = fuzz.trimf(anemia.universe, [7.5, 8.5, 9])
anemia['Macro_Hyper'] = fuzz.trimf(anemia.universe, [8, 9, 9])

# --------------------------------------------------------------------------
# RULES - Define a small set of rules
# --------------------------------------------------------------------------
rule1 = ctrl.Rule(hgb['normal'] & mcv['normal'] & mchc['normal'], anemia['Normal'])
rule2 = ctrl.Rule(hgb['normal'] & mcv['low'] & mchc['low'], anemia['Normo_Hypo'])
rule3 = ctrl.Rule(hgb['normal'] & mcv['high'] & mchc['high'], anemia['Normo_Hyper'])
rule4 = ctrl.Rule(hgb['low'] & mcv['low'] & mchc['low'], anemia['Micro_Hypo'])
rule5 = ctrl.Rule(hgb['low'] & mcv['normal'] & mchc['normal'], anemia['Micro_Normo'])
rule6 = ctrl.Rule(hgb['low'] & mcv['high'] & mchc['high'], anemia['Macro_Hyper'])

# CRITICAL FIX: The rules must be passed as a LIST to the ControlSystem
rules_list = [rule1, rule2, rule3, rule4, rule5, rule6]
system = ctrl.ControlSystem(rules_list) 


# Output Mapping Function
anemia_map = {
    (0, 1): "Normal", (1, 2): "Microcytic Hypochromic", (2, 3): "Microcytic Normochromic",
    (3, 4): "Microcytic Hyperchromic", (4, 5): "Normocytic Hypochromic", (5, 6): "Normocytic Normochromic",
    (6, 7): "Normocytic Hyperchromic", (7, 8): "Macrocytic Hypochromic", (8, 9): "Macrocytic Normochromic",
    (9, 10): "Macrocytic Hyperchromic"
}

def detect_anemia(hgb_val, mcv_val, mchc_val):
    sim = ctrl.ControlSystemSimulation(system)
    sim.input['hgb'] = hgb_val
    sim.input['mcv'] = mcv_val
    sim.input['mchc'] = mchc_val
    sim.compute()
    result = sim.output['anemia']
    
    for (low, high), name in anemia_map.items():
        if low <= result < high:
            return name
    return "Diagnosis Inconclusive"