import numpy as np

def gradient_descent(cost_func, grad_func, params_init, learning_rate=0.01,
                     max_iter=1000, tol=1e-6):
    """
    Gradient Descent untuk optimasi parameter sistem elektronika.

    Args:
        cost_func   : fungsi biaya f(params) -> scalar
        grad_func   : fungsi gradien df(params) -> array
        params_init : nilai awal parameter (np.array)
        learning_rate: laju belajar (alpha)
        max_iter    : iterasi maksimum
        tol         : toleransi konvergensi

    Returns:
        dict berisi history iterasi, parameter optimal, dan cost akhir
    """
    params = np.array(params_init, dtype=float)
    history = {
        "iteration": [],
        "cost": [],
        "params": [],
        "gradient_norm": []
    }

    grad_norm = float("inf")
    last_i = 0
    for i in range(max_iter):
        last_i = i
        cost = cost_func(params)
        grad = grad_func(params)
        grad_norm = np.linalg.norm(grad)

        history["iteration"].append(i)
        history["cost"].append(cost)
        history["params"].append(params.copy())
        history["gradient_norm"].append(grad_norm)

        if grad_norm < tol or np.isnan(grad_norm):
            break

        # Update parameter dengan clipping untuk stabilitas numerik
        step = learning_rate * grad
        params = params - step

    return {
        "optimal_params": params,
        "final_cost": cost_func(params),
        "iterations": last_i + 1,
        "converged": bool(grad_norm < tol),
        "history": history
    }


# ── 1. RC Charging ─────────────────────────────────────────────────────────────
def rc_voltage_error(params, time_array, V_target, V_in=5.0):
    """Cost: MSE tegangan kapasitor RC charging vs target. params = [R, C]"""
    R, C = max(params[0], 1e-3), max(params[1], 1e-12)
    tau = R * C
    V_calc = V_in * (1 - np.exp(-time_array / tau))
    return float(np.mean((V_calc - V_target)**2))

def rc_voltage_grad(params, time_array, V_target, V_in=5.0, eps=1e-7):
    grad = np.zeros_like(params, dtype=float)
    f0 = rc_voltage_error(params, time_array, V_target, V_in)
    for k in range(len(params)):
        p_plus = params.copy()
        step = max(abs(params[k]) * 1e-5, eps)
        p_plus[k] += step
        grad[k] = (rc_voltage_error(p_plus, time_array, V_target, V_in) - f0) / step
    return grad


# ── 2. RC Discharging ──────────────────────────────────────────────────────────
def rc_discharge_error(params, time_array, V_target, V0=5.0):
    """Cost: MSE tegangan pengosongan kapasitor RC vs target. params = [R, C]"""
    R, C = max(params[0], 1e-3), max(params[1], 1e-12)
    tau = R * C
    V_calc = V0 * np.exp(-time_array / tau)
    return float(np.mean((V_calc - V_target)**2))

def rc_discharge_grad(params, time_array, V_target, V0=5.0, eps=1e-7):
    grad = np.zeros_like(params, dtype=float)
    f0 = rc_discharge_error(params, time_array, V_target, V0)
    for k in range(len(params)):
        p_plus = params.copy()
        step = max(abs(params[k]) * 1e-5, eps)
        p_plus[k] += step
        grad[k] = (rc_discharge_error(p_plus, time_array, V_target, V0) - f0) / step
    return grad


# ── 3. RLC Seri (Impedansi) ────────────────────────────────────────────────────
def rlc_impedance_error(params, freq_array, Z_target):
    """Cost: MSE antara impedansi terukur vs Z_target. params = [R, L, C]"""
    R = max(params[0], 1e-3)
    L = max(params[1], 1e-9)
    C = max(params[2], 1e-12)
    omega = 2 * np.pi * freq_array
    reactance = omega * L - 1.0 / (omega * C + 1e-15)
    Z_calc = np.sqrt(R**2 + reactance**2)
    return float(np.mean((Z_calc - Z_target)**2))

def rlc_impedance_grad(params, freq_array, Z_target, eps=1e-6):
    grad = np.zeros_like(params, dtype=float)
    f0 = rlc_impedance_error(params, freq_array, Z_target)
    for k in range(len(params)):
        p_plus = params.copy()
        step = max(abs(params[k]) * 1e-5, eps)
        p_plus[k] += step
        grad[k] = (rlc_impedance_error(p_plus, freq_array, Z_target) - f0) / step
    return grad


# ── 4. Band-Pass Filter (RLC) ─────────────────────────────────────────────────
def bandpass_filter_error(params, freq_array, Gain_target):
    """Cost: MSE gain filter bandpass H(f) vs target. params = [R, L, C]"""
    R = max(params[0], 1e-3)
    L = max(params[1], 1e-9)
    C = max(params[2], 1e-12)
    omega = 2 * np.pi * freq_array
    reactance = omega * L - 1.0 / (omega * C + 1e-15)
    H_calc = R / np.sqrt(R**2 + reactance**2)
    return float(np.mean((H_calc - Gain_target)**2))

def bandpass_filter_grad(params, freq_array, Gain_target, eps=1e-6):
    grad = np.zeros_like(params, dtype=float)
    f0 = bandpass_filter_error(params, freq_array, Gain_target)
    for k in range(len(params)):
        p_plus = params.copy()
        step = max(abs(params[k]) * 1e-5, eps)
        p_plus[k] += step
        grad[k] = (bandpass_filter_error(p_plus, freq_array, Gain_target) - f0) / step
    return grad


# ── 5. Amplifier (Single-Pole) ────────────────────────────────────────────────
def amplifier_gain_error(params, freq_array, Gain_target):
    """Cost: MSE gain amplifier vs target. params = [A0, f_cutoff]"""
    A0 = max(params[0], 1e-3)
    fc = max(params[1], 1e-3)
    G_calc = A0 / np.sqrt(1 + (freq_array / fc)**2)
    return float(np.mean((G_calc - Gain_target)**2))

def amplifier_gain_grad(params, freq_array, Gain_target, eps=1e-6):
    grad = np.zeros_like(params, dtype=float)
    f0 = amplifier_gain_error(params, freq_array, Gain_target)
    for k in range(len(params)):
        p_plus = params.copy()
        step = max(abs(params[k]) * 1e-5, eps)
        p_plus[k] += step
        grad[k] = (amplifier_gain_error(p_plus, freq_array, Gain_target) - f0) / step
    return grad


# ── 6. Transistor BJT (IC vs VBE) ─────────────────────────────────────────────
def bjt_collector_error(params, vbe_array, ic_target):
    """Cost: MSE arus kolektor BJT vs target. params = [I_s, V_T]"""
    Is = max(params[0], 1e-18)
    Vt = max(params[1], 0.005)
    ic_calc = Is * (np.exp(np.clip(vbe_array / Vt, 0, 40)) - 1)
    return float(np.mean((ic_calc - ic_target)**2))

def bjt_collector_grad(params, vbe_array, ic_target, eps=1e-12):
    grad = np.zeros_like(params, dtype=float)
    f0 = bjt_collector_error(params, vbe_array, ic_target)
    for k in range(len(params)):
        p_plus = params.copy()
        step = max(abs(params[k]) * 1e-5, eps)
        p_plus[k] += step
        grad[k] = (bjt_collector_error(p_plus, vbe_array, ic_target) - f0) / step
    return grad
