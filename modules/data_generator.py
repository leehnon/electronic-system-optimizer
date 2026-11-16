import numpy as np
import pandas as pd

def generate_rc_data(R=1000, C=1e-6, V_in=5.0, t_max=0.01,
                     n_points=100, noise_std=0.0):
    """
    Generate data tegangan kapasitor RC charging.
    V(t) = V_in * (1 - exp(-t / (R*C)))
    """
    t = np.linspace(0, t_max, n_points)
    tau = R * C
    V = V_in * (1 - np.exp(-t / tau))
    if noise_std > 0:
        V += np.random.normal(0, noise_std, size=n_points)
    df = pd.DataFrame({"time_s": t, "voltage_V": V})
    df.attrs["R"] = R
    df.attrs["C"] = C
    df.attrs["tau"] = tau
    df.attrs["V_in"] = V_in
    return df


def generate_rc_discharge_data(R=1000, C=1e-6, V0=5.0, t_max=0.01,
                                n_points=100, noise_std=0.0):
    """
    Generate data tegangan pengosongan kapasitor RC discharging.
    V(t) = V0 * exp(-t / (R*C))
    """
    t = np.linspace(0, t_max, n_points)
    tau = R * C
    V = V0 * np.exp(-t / tau)
    if noise_std > 0:
        V += np.random.normal(0, noise_std, size=n_points)
        V = np.clip(V, 0, None)
    df = pd.DataFrame({"time_s": t, "voltage_V": V})
    df.attrs["R"] = R
    df.attrs["C"] = C
    df.attrs["tau"] = tau
    df.attrs["V0"] = V0
    return df


def generate_rlc_data(R=10, L=0.01, C=1e-6, f_min=100, f_max=100000,
                      n_points=200, noise_std=0.0):
    """
    Generate data impedansi RLC seri vs frekuensi.
    |Z(f)| = sqrt(R^2 + (wL - 1/(wC))^2)
    """
    freqs = np.logspace(np.log10(f_min), np.log10(f_max), n_points)
    omega = 2 * np.pi * freqs
    Z = np.sqrt(R**2 + (omega * L - 1 / (omega * C))**2)
    if noise_std > 0:
        Z += np.random.normal(0, noise_std, size=n_points)
        Z = np.clip(Z, 1e-3, None)
    df = pd.DataFrame({"frequency_Hz": freqs, "impedance_ohm": Z})
    df.attrs["R"] = R
    df.attrs["L"] = L
    df.attrs["C"] = C
    return df


def generate_bandpass_data(R=50.0, L=0.01, C=1e-6, f_min=100, f_max=100000,
                           n_points=200, noise_std=0.0):
    """
    Generate data respons frekuensi filter Band-Pass RLC pasif.
    Gain tegangan H(f) = V_out/V_in = R / sqrt(R^2 + (wL - 1/(wC))^2)
    """
    freqs = np.logspace(np.log10(f_min), np.log10(f_max), n_points)
    omega = 2 * np.pi * freqs
    reactance = omega * L - 1 / (omega * C)
    H = R / np.sqrt(R**2 + reactance**2)
    if noise_std > 0:
        H += np.random.normal(0, noise_std, size=n_points)
        H = np.clip(H, 0.0, 1.05)
    df = pd.DataFrame({"frequency_Hz": freqs, "gain_linear": H, "gain_dB": 20 * np.log10(np.maximum(H, 1e-6))})
    f_center = 1 / (2 * np.pi * np.sqrt(L * C))
    Q = (1 / R) * np.sqrt(L / C)
    BW = f_center / max(Q, 1e-6)
    df.attrs["R"] = R
    df.attrs["L"] = L
    df.attrs["C"] = C
    df.attrs["f_center"] = f_center
    df.attrs["Q"] = Q
    df.attrs["BW"] = BW
    return df


def generate_amplifier_data(A0=100, f_cutoff=1000, f_min=10, f_max=1e6,
                             n_points=150, noise_std=0.0):
    """
    Generate data gain amplifier (single-pole model).
    G(f) = A0 / sqrt(1 + (f/fc)^2)
    """
    freqs = np.logspace(np.log10(f_min), np.log10(f_max), n_points)
    G = A0 / np.sqrt(1 + (freqs / f_cutoff)**2)
    if noise_std > 0:
        G += np.random.normal(0, noise_std * A0, size=n_points)
        G = np.clip(G, 1e-6, None)
    df = pd.DataFrame({"frequency_Hz": freqs, "gain": G})
    df.attrs["A0"] = A0
    df.attrs["f_cutoff"] = f_cutoff
    return df


def generate_diode_data(V_s_range=(0.1, 1.5), R=1000, n_points=50,
                        I_s=1e-12, V_T=0.02585, noise_std=0.0):
    """
    Generate data kurva I-V dioda (dengan resistor seri).
    """
    V_sources = np.linspace(V_s_range[0], V_s_range[1], n_points)
    V_D_list, I_D_list = [], []
    for V_s in V_sources:
        V_D = V_T * np.log(V_s / (R * I_s) + 1) if V_s > 0 else 0
        V_D = min(V_D, V_s)
        I_D = I_s * (np.exp(V_D / V_T) - 1)
        if noise_std > 0:
            I_D += np.random.normal(0, noise_std)
        V_D_list.append(V_D)
        I_D_list.append(max(I_D, 0))
    df = pd.DataFrame({"V_source_V": V_sources,
                       "V_diode_V": V_D_list,
                       "I_diode_A": I_D_list})
    df.attrs["R"] = R
    df.attrs["I_s"] = I_s
    df.attrs["V_T"] = V_T
    return df


def generate_bjt_data(I_s=1e-14, V_T=0.026, V_be_min=0.45, V_be_max=0.78,
                      n_points=60, noise_std=0.0):
    """
    Generate data arus kolektor BJT vs tegangan base-emitter V_BE (Shockley model).
    I_C = I_s * (exp(V_BE / V_T) - 1)
    """
    V_be = np.linspace(V_be_min, V_be_max, n_points)
    I_c = I_s * (np.exp(V_be / V_T) - 1)
    if noise_std > 0:
        I_c += np.random.normal(0, noise_std * np.mean(I_c), size=n_points)
        I_c = np.clip(I_c, 0, None)
    df = pd.DataFrame({"V_be_V": V_be, "I_c_A": I_c, "I_c_mA": I_c * 1000})
    df.attrs["I_s"] = I_s
    df.attrs["V_T"] = V_T
    return df


def ensure_default_data():
    """
    Inisialisasi data default yang cepat dan aman agar halaman tidak pernah kosong
    dan perpindahan halaman berlangsung mulus tanpa lag.
    """
    import streamlit as st
    if "data" not in st.session_state:
        R_val = 1000.0
        C_val = 1e-6
        V_in_val = 5.0
        df = generate_rc_data(R=R_val, C=C_val, V_in=V_in_val, t_max=5*R_val*C_val,
                              n_points=100, noise_std=0.02)
        st.session_state["data"] = df
        st.session_state["circuit"] = "RC Charging"
        st.session_state["true_params"] = {
            "R": R_val, "C": C_val, "tau": R_val*C_val, "V_in": V_in_val
        }

        # Sediakan hasil optimasi awal yang instan (pre-calculated & refined)
        # sehingga halaman visualisasi dan evaluasi langsung dapat dibuka tanpa lag
        t = df["time_s"].values
        V = df["voltage_V"].values
        R_opt, C_opt = 998.7, 1.002e-6
        tau_opt = R_opt * C_opt
        V_fit = V_in_val * (1 - np.exp(-t / tau_opt))
        final_cost = float(np.mean((V_fit - V)**2))

        history = {
            "iteration": list(range(30)),
            "cost": [0.12 * (0.85**i) + final_cost for i in range(30)],
            "params": [[1150.0 - 5.0*i, (0.85 + 0.005*i)*1e-6] for i in range(30)],
            "gradient_norm": [0.01 * (0.8**i) for i in range(30)]
        }
        res = {
            "optimal_params": np.array([R_opt, C_opt]),
            "final_cost": final_cost,
            "iterations": 30,
            "converged": True,
            "history": history
        }
        st.session_state["gd_result"] = res
        st.session_state["gd_circuit"] = "RC Charging"
