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
    df = pd.DataFrame({"frequency_Hz": freqs, "impedance_ohm": Z})
    df.attrs["R"] = R
    df.attrs["L"] = L
    df.attrs["C"] = C
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


def ensure_default_data():
    """
    Inisialisasi data default agar halaman tidak pernah kosong
    saat user membuka atau me-refresh menu.
    """
    import streamlit as st
    if "data" not in st.session_state:
        R_val = 1000.0
        C_val = 1e-6
        V_in_val = 5.0
        df = generate_rc_data(R=R_val, C=C_val, V_in=V_in_val, t_max=5*R_val*C_val,
                              n_points=100, noise_std=0.05)
        st.session_state["data"] = df
        st.session_state["circuit"] = "RC Charging"
        st.session_state["true_params"] = {
            "R": R_val, "C": C_val, "tau": R_val*C_val, "V_in": V_in_val
        }

        # Jalankan optimasi default agar grafik dan evaluasi langsung terisi
        from modules.gradient_descent import (gradient_descent,
                                              rc_voltage_error, rc_voltage_grad)
        t = df["time_s"].values
        V = df["voltage_V"].values
        cost_f = lambda p: rc_voltage_error(p, t, V, V_in_val)
        grad_f = lambda p: rc_voltage_grad(p, t, V, V_in_val)
        res = gradient_descent(cost_f, grad_f, params_init=[1150.0, 0.85e-6],
                               learning_rate=1e-6, max_iter=300)
        st.session_state["gd_result"] = res
        st.session_state["gd_circuit"] = "RC Charging"
