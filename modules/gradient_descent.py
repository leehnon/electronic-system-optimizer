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

    for i in range(max_iter):
        cost = cost_func(params)
        grad = grad_func(params)
        grad_norm = np.linalg.norm(grad)

        history["iteration"].append(i)
        history["cost"].append(cost)
        history["params"].append(params.copy())
        history["gradient_norm"].append(grad_norm)

        if grad_norm < tol:
            break

        params = params - learning_rate * grad

    return {
        "optimal_params": params,
        "final_cost": cost_func(params),
        "iterations": i + 1,
        "converged": grad_norm < tol,
        "history": history
    }


# ── Fungsi biaya untuk berbagai rangkaian ──────────────────────────────────────

def rlc_impedance_error(params, freq_array, Z_target):
    """
    Cost: MSE antara impedansi terukur vs Z_target
    params = [R, L, C]
    """
    R, L, C = params[0], params[1], params[2]
    errors = []
    for f, Zt in zip(freq_array, Z_target):
        omega = 2 * np.pi * f
        Z_calc = np.sqrt(R**2 + (omega * L - 1 / (omega * C + 1e-12))**2)
        errors.append((Z_calc - Zt)**2)
    return np.mean(errors)


def rlc_impedance_grad(params, freq_array, Z_target, eps=1e-6):
    """Gradien numerik (finite difference) untuk rlc_impedance_error."""
    grad = np.zeros_like(params, dtype=float)
    f0 = rlc_impedance_error(params, freq_array, Z_target)
    for k in range(len(params)):
        p_plus = params.copy()
        p_plus[k] += eps
        grad[k] = (rlc_impedance_error(p_plus, freq_array, Z_target) - f0) / eps
    return grad


def rc_voltage_error(params, time_array, V_target, V_in=5.0):
    """
    Cost: MSE tegangan kapasitor RC vs target.
    params = [R, C]
    """
    R, C = max(params[0], 1e-3), max(params[1], 1e-9)
    tau = R * C
    V_calc = V_in * (1 - np.exp(-time_array / tau))
    return np.mean((V_calc - V_target)**2)


def rc_voltage_grad(params, time_array, V_target, V_in=5.0, eps=1e-8):
    grad = np.zeros_like(params, dtype=float)
    f0 = rc_voltage_error(params, time_array, V_target, V_in)
    for k in range(len(params)):
        p_plus = params.copy()
        p_plus[k] += eps
        grad[k] = (rc_voltage_error(p_plus, time_array, V_target, V_in) - f0) / eps
    return grad


def amplifier_gain_error(params, freq_array, Gain_target):
    """
    Cost: MSE gain amplifier vs target.
    params = [A0, f_cutoff]  (gain DC dan frekuensi cutoff)
    """
    A0, fc = max(params[0], 1e-3), max(params[1], 1e-3)
    errors = []
    for f, Gt in zip(freq_array, Gain_target):
        G_calc = A0 / np.sqrt(1 + (f / fc)**2)
        errors.append((G_calc - Gt)**2)
    return np.mean(errors)


def amplifier_gain_grad(params, freq_array, Gain_target, eps=1e-6):
    grad = np.zeros_like(params, dtype=float)
    f0 = amplifier_gain_error(params, freq_array, Gain_target)
    for k in range(len(params)):
        p_plus = params.copy()
        p_plus[k] += eps
        grad[k] = (amplifier_gain_error(p_plus, freq_array, Gain_target) - f0) / eps
    return grad
