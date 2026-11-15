import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Warna tema ──────────────────────────────────────────────────────────────
PRIMARY   = "#1f77b4"
SECONDARY = "#ff7f0e"
SUCCESS   = "#2ca02c"
DANGER    = "#d62728"
PURPLE    = "#9467bd"


def plot_rc_charging(time, V_measured, V_fitted=None, tau_true=None, tau_fitted=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time, y=V_measured, mode="markers",
                             name="Data (Simulasi/Riil)", marker=dict(color=PRIMARY, size=4)))
    if V_fitted is not None:
        fig.add_trace(go.Scatter(x=time, y=V_fitted, mode="lines",
                                 name=f"Model Fitted (τ={tau_fitted:.4f} s)" if tau_fitted else "Model Fitted",
                                 line=dict(color=SECONDARY, width=2)))
    if tau_true:
        fig.add_vline(x=tau_true, line_dash="dash", line_color=SUCCESS,
                      annotation_text=f"τ_true = {tau_true:.4f} s")
    fig.update_layout(title="RC Charging Curve", xaxis_title="Waktu (s)",
                      yaxis_title="Tegangan (V)", legend=dict(x=0.7, y=0.2),
                      template="plotly_white", height=400)
    return fig


def plot_rlc_impedance(freq, Z_measured, Z_fitted=None, f_resonance=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freq, y=Z_measured, mode="markers",
                             name="Data", marker=dict(color=PRIMARY, size=4)))
    if Z_fitted is not None:
        fig.add_trace(go.Scatter(x=freq, y=Z_fitted, mode="lines",
                                 name="Model Fitted", line=dict(color=SECONDARY, width=2)))
    if f_resonance:
        fig.add_vline(x=f_resonance, line_dash="dash", line_color=SUCCESS,
                      annotation_text=f"f_r = {f_resonance:.1f} Hz")
    fig.update_layout(title="Impedansi RLC vs Frekuensi", xaxis_title="Frekuensi (Hz)",
                      yaxis_title="|Z| (Ω)", xaxis_type="log",
                      template="plotly_white", height=400)
    return fig


def plot_amplifier_gain(freq, G_measured, G_fitted=None, f_cutoff=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=freq, y=20*np.log10(G_measured + 1e-14),
                             mode="markers", name="Data (dB)",
                             marker=dict(color=PRIMARY, size=4)))
    if G_fitted is not None:
        fig.add_trace(go.Scatter(x=freq, y=20*np.log10(G_fitted + 1e-14),
                                 mode="lines", name="Model Fitted (dB)",
                                 line=dict(color=SECONDARY, width=2)))
    if f_cutoff:
        fig.add_vline(x=f_cutoff, line_dash="dash", line_color=SUCCESS,
                      annotation_text=f"f_c = {f_cutoff:.1f} Hz")
    fig.update_layout(title="Gain Amplifier (Bode Plot)", xaxis_title="Frekuensi (Hz)",
                      yaxis_title="Gain (dB)", xaxis_type="log",
                      template="plotly_white", height=400)
    return fig


def plot_convergence(history, label="Cost"):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Konvergensi Cost Function",
                                        "Norm Gradien per Iterasi"])
    iters = history.get("iteration", list(range(len(history["cost"]))))
    fig.add_trace(go.Scatter(x=iters, y=history["cost"], mode="lines+markers",
                             name="Cost", line=dict(color=PRIMARY)),
                  row=1, col=1)
    if "gradient_norm" in history:
        fig.add_trace(go.Scatter(x=iters, y=history["gradient_norm"],
                                 mode="lines+markers", name="|∇f|",
                                 line=dict(color=SECONDARY)),
                      row=1, col=2)
    fig.update_xaxes(title_text="Iterasi")
    fig.update_yaxes(title_text="Cost", row=1, col=1)
    fig.update_yaxes(title_text="|∇f|", row=1, col=2)
    fig.update_layout(template="plotly_white", height=380, showlegend=False)
    return fig


def plot_newton_raphson_convergence(history):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Nilai x per Iterasi", "|f(x)| per Iterasi"])
    iters = history["iteration"]
    fig.add_trace(go.Scatter(x=iters, y=history["x"], mode="lines+markers",
                             name="x", line=dict(color=PRIMARY)),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=iters, y=history["error"], mode="lines+markers",
                             name="|f(x)|", line=dict(color=DANGER)),
                  row=1, col=2)
    fig.update_xaxes(title_text="Iterasi")
    fig.update_yaxes(title_text="x", row=1, col=1)
    fig.update_yaxes(title_text="|f(x)|", type="log", row=1, col=2)
    fig.update_layout(template="plotly_white", height=380, showlegend=False)
    return fig


def plot_residuals(residuals, y_true=None):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Residual vs Index", "Distribusi Residual"])
    idx = list(range(len(residuals)))
    fig.add_trace(go.Scatter(x=idx, y=residuals, mode="markers",
                             marker=dict(color=PRIMARY, size=4), name="Residual"),
                  row=1, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=1)
    fig.add_trace(go.Histogram(x=residuals, nbinsx=20,
                               marker_color=SECONDARY, name="Distribusi"),
                  row=1, col=2)
    fig.update_layout(template="plotly_white", height=350, showlegend=False)
    return fig


def plot_sensitivity(sensitivity_df):
    fig = px.bar(sensitivity_df, x="Parameter", y="Sensitivity Index",
                 color="Sensitivity Index",
                 color_continuous_scale="RdYlGn_r",
                 title="Analisis Sensitivitas Parameter")
    fig.update_layout(template="plotly_white", height=350)
    return fig


def plot_diode_iv(V_source, V_diode, I_diode):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=V_diode, y=I_diode * 1000,
                             mode="lines+markers",
                             line=dict(color=PRIMARY, width=2),
                             marker=dict(size=4),
                             name="Kurva I-V Dioda"))
    fig.update_layout(title="Karakteristik I-V Dioda",
                      xaxis_title="V_D (V)", yaxis_title="I_D (mA)",
                      template="plotly_white", height=400)
    return fig
