import numpy as np

def newton_raphson_scalar(f, df, x0, max_iter=100, tol=1e-8):
    """
    Newton-Raphson untuk satu variabel.

    Args:
        f       : fungsi f(x)
        df      : turunan f'(x)
        x0      : nilai awal
        max_iter: iterasi maksimum
        tol     : toleransi |f(x)| < tol

    Returns:
        dict dengan root, iterasi, dan history
    """
    x = float(x0)
    history = {"iteration": [], "x": [], "fx": [], "error": []}

    for i in range(max_iter):
        fx = f(x)
        dfx = df(x)

        history["iteration"].append(i)
        history["x"].append(x)
        history["fx"].append(fx)
        history["error"].append(abs(fx))

        if abs(dfx) < 1e-14:
            break

        x_new = x - fx / dfx
        if abs(x_new - x) < tol:
            x = x_new
            history["iteration"].append(i + 1)
            history["x"].append(x)
            history["fx"].append(f(x))
            history["error"].append(abs(f(x)))
            break
        x = x_new

    return {
        "root": x,
        "f_root": f(x),
        "iterations": i + 1,
        "converged": abs(f(x)) < tol,
        "history": history
    }


def newton_raphson_system(F_func, J_func, x0, max_iter=100, tol=1e-8):
    """
    Newton-Raphson untuk sistem persamaan nonlinear.

    Args:
        F_func  : fungsi vektor F(x) -> np.array
        J_func  : fungsi Jacobian J(x) -> np.matrix
        x0      : tebakan awal (np.array)
        max_iter: iterasi maksimum
        tol     : toleransi ||F(x)|| < tol

    Returns:
        dict dengan solusi, iterasi, dan history
    """
    x = np.array(x0, dtype=float)
    history = {"iteration": [], "x": [], "residual": []}

    for i in range(max_iter):
        F = F_func(x)
        J = J_func(x)
        residual = np.linalg.norm(F)

        history["iteration"].append(i)
        history["x"].append(x.copy())
        history["residual"].append(residual)

        if residual < tol:
            break

        try:
            delta_x = np.linalg.solve(J, -F)
        except np.linalg.LinAlgError:
            break

        x = x + delta_x

    return {
        "solution": x,
        "F_solution": F_func(x),
        "iterations": i + 1,
        "converged": residual < tol,
        "history": history
    }


# ── Aplikasi Newton-Raphson untuk rangkaian elektronika ───────────────────────

def find_diode_operating_point(V_s, R, I_s=1e-12, V_T=0.02585, max_iter=100):
    """
    Cari titik operasi dioda: V_s = V_D + I_D * R
    dengan I_D = I_s * (exp(V_D/V_T) - 1)
    """
    def f(V_D):
        I_D = I_s * (np.exp(V_D / V_T) - 1)
        return V_D + I_D * R - V_s

    def df(V_D):
        dI_D = (I_s / V_T) * np.exp(V_D / V_T)
        return 1 + dI_D * R

    x0 = V_s * 0.7  # tebakan awal
    result = newton_raphson_scalar(f, df, x0, max_iter)
    V_D = result["root"]
    I_D = I_s * (np.exp(V_D / V_T) - 1)
    result["V_D"] = V_D
    result["I_D"] = I_D
    return result


def find_rlc_resonance(L, C, target_freq=None, max_iter=100):
    """
    Cari frekuensi resonansi RLC: f_r = 1/(2*pi*sqrt(LC))
    Juga bisa solve untuk L atau C diberikan target_freq.
    """
    f_r = 1 / (2 * np.pi * np.sqrt(L * C))
    omega_r = 2 * np.pi * f_r

    result = {
        "resonance_freq_Hz": f_r,
        "resonance_omega": omega_r,
        "L": L,
        "C": C
    }

    if target_freq is not None:
        # Solve L diberikan target frekuensi dan C
        def f(L_val):
            return 1 / (2 * np.pi * np.sqrt(max(L_val, 1e-15) * C)) - target_freq

        def df(L_val):
            L_v = max(L_val, 1e-15)
            return -1 / (4 * np.pi * (L_v * C)**1.5 * C) * (-1)

        nr = newton_raphson_scalar(f, lambda x: (f(x + 1e-9) - f(x)) / 1e-9,
                                   L, max_iter)
        result["optimal_L_for_target_freq"] = nr["root"]
        result["nr_result"] = nr

    return result


def find_rc_time_constant(V_in, V_target_at_t, t, max_iter=100):
    """
    Cari tau (R*C) agar V_target = V_in*(1 - exp(-t/tau))
    """
    if V_target_at_t >= V_in:
        return None

    ratio = V_target_at_t / V_in

    def f(tau):
        return 1 - np.exp(-t / max(tau, 1e-15)) - ratio

    def df(tau):
        tau_v = max(tau, 1e-15)
        return -t / tau_v**2 * np.exp(-t / tau_v)

    x0 = t  # tebakan awal
    return newton_raphson_scalar(f, df, x0, max_iter)
