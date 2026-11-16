import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Design token ─────────────────────────────────────────────────────────────
PRIMARY   = "#1f6feb"   # blue
SECONDARY = "#fb8f44"   # orange
SUCCESS   = "#1a7f37"   # green
DANGER    = "#cf222e"   # red
PURPLE    = "#8250df"   # purple
CYAN      = "#0284c7"   # cyan

# Plotly layout base — clean, minimal, matches app theme
_LAYOUT_BASE = dict(
    template="plotly_white",
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f8fafc",
    font=dict(family="Inter, -apple-system, sans-serif", size=12, color="#0f172a"),
    title_font=dict(size=14, color="#0f172a", family="Inter, sans-serif"),
    legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#e2e8f0",
                borderwidth=1, font=dict(size=11)),
    xaxis=dict(gridcolor="#e2e8f0", linecolor="#cbd5e1", tickcolor="#cbd5e1",
               title_font=dict(size=12, color="#334155")),
    yaxis=dict(gridcolor="#e2e8f0", linecolor="#cbd5e1", tickcolor="#cbd5e1",
               title_font=dict(size=12, color="#334155")),
    margin=dict(t=50, l=15, r=15, b=15),
)


def _apply_base(fig, title="", height=400, **kwargs):
    layout = {**_LAYOUT_BASE, "height": height}
    if title:
        layout["title"] = dict(text=title, font=dict(size=14, color="#0f172a", family="Inter, sans-serif"))
    layout.update(kwargs)
    fig.update_layout(**layout)
    return fig


# ── 1. RC Charging ─────────────────────────────────────────────────────────────
def plot_rc_charging(time, V_measured, V_fitted=None, tau_true=None, tau_fitted=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time, y=V_measured, mode="markers", name="Data Terukur",
        marker=dict(color=PRIMARY, size=5, opacity=0.75)))
    if V_fitted is not None:
        fig.add_trace(go.Scatter(
            x=time, y=V_fitted, mode="lines",
            name=f"Model Fitted (τ = {tau_fitted:.4f} s)" if tau_fitted else "Model Fitted",
            line=dict(color=SECONDARY, width=2.5)))
    if tau_true:
        fig.add_vline(x=tau_true, line_dash="dot", line_color=SUCCESS, line_width=1.5,
                      annotation_text=f"τ_true = {tau_true:.4f} s",
                      annotation_font_size=11)
    fig = _apply_base(fig, title="RC Charging — Tegangan Kapasitor vs Waktu",
                      xaxis_title="Waktu (s)", yaxis_title="Tegangan (V)")
    return fig


# ── 2. RC Discharging ──────────────────────────────────────────────────────────
def plot_rc_discharging(time, V_measured, V_fitted=None, tau_true=None, tau_fitted=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time, y=V_measured, mode="markers", name="Data Terukur",
        marker=dict(color="#0284c7", size=5, opacity=0.75)))
    if V_fitted is not None:
        fig.add_trace(go.Scatter(
            x=time, y=V_fitted, mode="lines",
            name=f"Model Fitted (τ = {tau_fitted:.4f} s)" if tau_fitted else "Model Fitted",
            line=dict(color=DANGER, width=2.5)))
    if tau_true:
        fig.add_vline(x=tau_true, line_dash="dot", line_color=SUCCESS, line_width=1.5,
                      annotation_text=f"τ = {tau_true:.4f} s (36.8%)",
                      annotation_font_size=11)
    fig = _apply_base(fig, title="RC Discharging — Pengosongan Kapasitor vs Waktu",
                      xaxis_title="Waktu (s)", yaxis_title="Tegangan (V)")
    return fig


# ── 3. RLC Seri (Impedansi) ────────────────────────────────────────────────────
def plot_rlc_impedance(freq, Z_measured, Z_fitted=None, f_resonance=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freq, y=Z_measured, mode="markers", name="Data Terukur",
        marker=dict(color=PRIMARY, size=5, opacity=0.75)))
    if Z_fitted is not None:
        fig.add_trace(go.Scatter(
            x=freq, y=Z_fitted, mode="lines", name="Model Fitted",
            line=dict(color=SECONDARY, width=2.5)))
    if f_resonance:
        fig.add_vline(x=f_resonance, line_dash="dot", line_color=SUCCESS, line_width=1.5,
                      annotation_text=f"f_r = {f_resonance:.1f} Hz",
                      annotation_font_size=11)
    fig = _apply_base(fig, title="Impedansi RLC vs Frekuensi",
                      xaxis_title="Frekuensi (Hz)", yaxis_title="|Z| (Ω)",
                      xaxis=dict(**_LAYOUT_BASE["xaxis"], type="log"))
    return fig


# ── 4. Band-Pass Filter (RLC) ─────────────────────────────────────────────────
def plot_bandpass_filter(freq, H_measured, H_fitted=None, f_center=None, bw=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freq, y=H_measured, mode="markers", name="Gain Terukur H(f)",
        marker=dict(color=PURPLE, size=5, opacity=0.75)))
    if H_fitted is not None:
        fig.add_trace(go.Scatter(
            x=freq, y=H_fitted, mode="lines", name="Model Fitted",
            line=dict(color=SECONDARY, width=2.5)))
    if f_center:
        fig.add_vline(x=f_center, line_dash="dot", line_color=SUCCESS, line_width=1.5,
                      annotation_text=f"f_center = {f_center:.1f} Hz",
                      annotation_font_size=11)
    fig.add_hline(y=1.0/np.sqrt(2), line_dash="dash", line_color="#94a3b8", line_width=1.2,
                  annotation_text="-3 dB (0.707)", annotation_font_size=10)
    fig = _apply_base(fig, title="Respons Frekuensi Filter Band-Pass RLC Pasif",
                      xaxis_title="Frekuensi (Hz)", yaxis_title="Gain Tegangan H(f) = Vout/Vin",
                      xaxis=dict(**_LAYOUT_BASE["xaxis"], type="log"))
    return fig


# ── 5. Amplifier (Single-Pole) ────────────────────────────────────────────────
def plot_amplifier_gain(freq, G_measured, G_fitted=None, f_cutoff=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freq, y=20*np.log10(np.maximum(G_measured, 1e-14)), mode="markers", name="Data Terukur",
        marker=dict(color=PRIMARY, size=5, opacity=0.75)))
    if G_fitted is not None:
        fig.add_trace(go.Scatter(
            x=freq, y=20*np.log10(np.maximum(G_fitted, 1e-14)), mode="lines", name="Model Fitted",
            line=dict(color=SECONDARY, width=2.5)))
    if f_cutoff:
        fig.add_vline(x=f_cutoff, line_dash="dot", line_color=SUCCESS, line_width=1.5,
                      annotation_text=f"f_c = {f_cutoff:.1f} Hz",
                      annotation_font_size=11)
    fig = _apply_base(fig, title="Bode Plot — Penguatan Amplifier (Gain vs Frekuensi)",
                      xaxis_title="Frekuensi (Hz)", yaxis_title="Gain (dB)",
                      xaxis=dict(**_LAYOUT_BASE["xaxis"], type="log"))
    return fig


# ── 6. Dioda I-V ──────────────────────────────────────────────────────────────
def plot_diode_iv(V_source, V_diode, I_diode):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=V_diode, y=np.array(I_diode) * 1000, mode="lines+markers",
        line=dict(color=DANGER, width=2.5),
        marker=dict(size=4), name="I-V Dioda"))
    fig = _apply_base(fig, title="Karakteristik I-V Dioda Maju (Forward Bias)",
                      xaxis_title="V_D (V)", yaxis_title="I_D (mA)")
    return fig


# ── 7. Transistor BJT (IC vs VBE) ─────────────────────────────────────────────
def plot_bjt_ic_vbe(V_be, Ic_measured, Ic_fitted=None, V_bias=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=V_be, y=np.array(Ic_measured) * 1000, mode="markers", name="Data IC (Terukur)",
        marker=dict(color="#d97706", size=5, opacity=0.8)))
    if Ic_fitted is not None:
        fig.add_trace(go.Scatter(
            x=V_be, y=np.array(Ic_fitted) * 1000, mode="lines", name="Model Shockley Fitted",
            line=dict(color=PRIMARY, width=2.5)))
    if V_bias:
        fig.add_vline(x=V_bias, line_dash="dot", line_color=SUCCESS, line_width=1.5,
                      annotation_text=f"V_bias = {V_bias:.3f} V", annotation_font_size=11)
    fig = _apply_base(fig, title="Karakteristik Transfer BJT — Arus Kolektor vs V_BE",
                      xaxis_title="Tegangan Base-Emitter V_BE (V)", yaxis_title="Arus Kolektor I_C (mA)")
    return fig


# ── Algoritma & Evaluasi Plots ────────────────────────────────────────────────
def plot_convergence(history, label="Cost"):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Konvergensi Cost Function (MSE)", "Norm Gradien |∇f|"],
                        horizontal_spacing=0.12)
    iters = history.get("iteration", list(range(len(history["cost"]))))
    fig.add_trace(go.Scatter(x=iters, y=history["cost"], mode="lines",
                             name="Cost", line=dict(color=PRIMARY, width=2)),
                  row=1, col=1)
    if "gradient_norm" in history and len(history["gradient_norm"]) == len(iters):
        fig.add_trace(go.Scatter(x=iters, y=history["gradient_norm"],
                                 mode="lines", name="|∇f|",
                                 line=dict(color=PURPLE, width=2)),
                      row=1, col=2)
    fig.update_xaxes(title_text="Iterasi", gridcolor="#e2e8f0", linecolor="#cbd5e1")
    fig.update_yaxes(gridcolor="#e2e8f0", linecolor="#cbd5e1")
    fig.update_layout(template="plotly_white", height=360, showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="#f8fafc",
                      font=dict(family="Inter, sans-serif", size=12))
    return fig


def plot_newton_raphson_convergence(history):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Nilai Parameter per Iterasi", "|f(x)| — Skala Log"],
                        horizontal_spacing=0.12)
    iters = history["iteration"]
    fig.add_trace(go.Scatter(x=iters, y=history["x"], mode="lines+markers",
                             name="x", line=dict(color=PRIMARY, width=2),
                             marker=dict(size=5)),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=iters, y=history["error"], mode="lines+markers",
                             name="|f(x)|", line=dict(color=DANGER, width=2),
                             marker=dict(size=5)),
                  row=1, col=2)
    fig.update_xaxes(title_text="Iterasi", gridcolor="#e2e8f0", linecolor="#cbd5e1")
    fig.update_yaxes(row=1, col=2, type="log", gridcolor="#e2e8f0")
    fig.update_layout(template="plotly_white", height=360, showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="#f8fafc",
                      font=dict(family="Inter, sans-serif", size=12))
    return fig


def plot_residuals(residuals, y_true=None):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Residual vs Indeks Data", "Distribusi Residual"],
                        horizontal_spacing=0.12)
    idx = list(range(len(residuals)))
    fig.add_trace(go.Scatter(x=idx, y=residuals, mode="markers",
                             marker=dict(color=PRIMARY, size=4, opacity=0.7),
                             name="Residual"),
                  row=1, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="#64748b", line_width=1.2, row=1, col=1)
    fig.add_trace(go.Histogram(x=residuals, nbinsx=24,
                               marker_color=SECONDARY, opacity=0.8, name="Distribusi"),
                  row=1, col=2)
    fig.update_xaxes(gridcolor="#e2e8f0", linecolor="#cbd5e1")
    fig.update_yaxes(gridcolor="#e2e8f0", linecolor="#cbd5e1")
    fig.update_layout(template="plotly_white", height=340, showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="#f8fafc",
                      font=dict(family="Inter, sans-serif", size=12))
    return fig


def plot_sensitivity(sensitivity_df):
    fig = px.bar(sensitivity_df, x="Parameter", y="Sensitivity Index",
                 color="Sensitivity Index",
                 color_continuous_scale=["#1a7f37", "#f59e0b", "#cf222e"],
                 title="Analisis Sensitivitas Parameter (±5%)")
    fig.update_traces(marker_line_width=0)
    fig = _apply_base(fig, height=340)
    return fig
