import numpy as np
import pandas as pd

def evaluate_metrics(y_true, y_pred):
    """
    Hitung metrik evaluasi numerik.
    """
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    residuals = y_true - y_pred

    mse  = np.mean(residuals**2)
    rmse = np.sqrt(mse)
    mae  = np.mean(np.abs(residuals))

    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    r2 = 1 - ss_res / (ss_tot + 1e-14)

    mape = np.mean(np.abs(residuals / (y_true + 1e-14))) * 100

    return {
        "MSE":  mse,
        "RMSE": rmse,
        "MAE":  mae,
        "R²":   r2,
        "MAPE (%)": mape,
        "Max Error": np.max(np.abs(residuals)),
        "Residuals": residuals
    }


def parameter_sensitivity(cost_func, optimal_params, param_names,
                           perturbation=0.05):
    """
    Analisis sensitivitas: ubah tiap parameter ±5% dan lihat perubahan cost.
    """
    base_cost = cost_func(optimal_params)
    results = []
    for i, name in enumerate(param_names):
        p_plus  = optimal_params.copy(); p_plus[i]  *= (1 + perturbation)
        p_minus = optimal_params.copy(); p_minus[i] *= (1 - perturbation)
        c_plus  = cost_func(p_plus)
        c_minus = cost_func(p_minus)
        sensitivity = (c_plus - c_minus) / (2 * perturbation * base_cost + 1e-14)
        results.append({
            "Parameter": name,
            "Optimal Value": optimal_params[i],
            f"Cost (+{int(perturbation*100)}%)": c_plus,
            f"Cost (-{int(perturbation*100)}%)": c_minus,
            "Sensitivity Index": sensitivity
        })
    return pd.DataFrame(results)


def convergence_rate(cost_history):
    """
    Estimasi laju konvergensi dari history cost.
    """
    costs = np.array(cost_history)
    if len(costs) < 3:
        return None
    ratios = []
    for i in range(1, len(costs) - 1):
        if costs[i-1] > 1e-14 and costs[i] > 1e-14:
            ratios.append(costs[i+1] / costs[i])
    return np.mean(ratios) if ratios else None
