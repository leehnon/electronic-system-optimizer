import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Design token (GitHub-inspired palette) ───────────────────────────────────
PRIMARY   = "#1f6feb"   # blue
SECONDARY = "#fb8f44"   # orange
SUCCESS   = "#1a7f37"   # green
DANGER    = "#cf222e"   # red
PURPLE    = "#8250df"   # purple

# Plotly layout base — clean, minimal, matches app theme
_LAYOUT_BASE = dict(
    template="plotly_white",
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f6f8fa",
    font=dict(family="Inter, -apple-system, sans-serif", size=12, color="#1c2128"),
    title_font=dict(size=14, color="#1c2128", family="Inter, sans-serif"),
    legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#d0d7de",
                borderwidth=1, font=dict(size=11)),
    xaxis=dict(gridcolor="#eaeef2", linecolor="#d0d7de", tickcolor="#d0d7de",
               title_font=dict(size=12)),
    yaxis=dict(gridcolor="#eaeef2", linecolor="#d0d7de", tickcolor="#d0d7de",
               title_font=dict(size=12)),
    margin=dict(t=50, l=10, r=10, b=10),
)


def _apply_base(fig, title="", height=400, **kwargs):
    layout = {**_LAYOUT_BASE, "height": height}
    if title:
        layout["title"] = dict(text=title, font=dict(size=14, color="#1c2128"))
    layout.update(kwargs)
    fig.update_layout(**layout)
    return fig


def plot_rc_charging(time, V_measured, V_fitted=None, tau_true=None, tau_fitted=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time, y=V_measured, mode="markers", name="Data",
        marker=dict(color=PRIMARY, size=4, opacity=0.7)))
    if V_fitted is not None:
        fig.add_trace(go.Scatter(
            x=time, y=V_fitted, mode="lines",
            name=f"Model (τ = {tau_fitted:.4f} s)" if tau_fitted else "Model Fitted",
            line=dict(color=SECONDARY, width=2.5)))
    if tau_true:
        fig.add_vline(x=tau_true, line_dash="dot", line_color=SUCCESS, line_width=1.5,
                      annotation_text=f"τ_true = {tau_true:.4f} s",
                      annotation_font_size=11)
    fig = _apply_base(fig, title="RC Charging — Tegangan Kapasitor vs Waktu",
                      xaxis_title="Waktu (s)", yaxis_title="Tegangan (V)")
    return fig


def plot_rlc_impedance(freq, Z_measured, Z_fitted=None, f_resonance=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freq, y=Z_measured, mode="markers", name="Data",
        marker=dict(color=PRIMARY, size=4, opacity=0.7)))
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


def plot_amplifier_gain(freq, G_measured, G_fitted=None, f_cutoff=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=freq, y=20*np.log10(G_measured + 1e-14), mode="markers", name="Data",
        marker=dict(color=PRIMARY, size=4, opacity=0.7)))
    if G_fitted is not None:
        fig.add_trace(go.Scatter(
            x=freq, y=20*np.log10(G_fitted + 1e-14), mode="lines", name="Model Fitted",
            line=dict(color=SECONDARY, width=2.5)))
    if f_cutoff:
        fig.add_vline(x=f_cutoff, line_dash="dot", line_color=SUCCESS, line_width=1.5,
                      annotation_text=f"f_c = {f_cutoff:.1f} Hz",
                      annotation_font_size=11)
    fig = _apply_base(fig, title="Bode Plot — Gain Amplifier",
                      xaxis_title="Frekuensi (Hz)", yaxis_title="Gain (dB)",
                      xaxis=dict(**_LAYOUT_BASE["xaxis"], type="log"))
    return fig


def plot_convergence(history, label="Cost"):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Konvergensi Cost Function", "Norm Gradien |∇f|"],
                        horizontal_spacing=0.12)
    iters = history.get("iteration", list(range(len(history["cost"]))))
    fig.add_trace(go.Scatter(x=iters, y=history["cost"], mode="lines",
                             name="Cost", line=dict(color=PRIMARY, width=2)),
                  row=1, col=1)
    if "gradient_norm" in history:
        fig.add_trace(go.Scatter(x=iters, y=history["gradient_norm"],
                                 mode="lines", name="|∇f|",
                                 line=dict(color=PURPLE, width=2)),
                      row=1, col=2)
    fig.update_xaxes(title_text="Iterasi", gridcolor="#eaeef2", linecolor="#d0d7de")
    fig.update_yaxes(gridcolor="#eaeef2", linecolor="#d0d7de")
    fig.update_layout(template="plotly_white", height=360, showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="#f6f8fa",
                      font=dict(family="Inter, sans-serif", size=12))
    return fig


def plot_newton_raphson_convergence(history):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Nilai x per Iterasi", "|f(x)| — Skala Log"],
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
    fig.update_xaxes(title_text="Iterasi", gridcolor="#eaeef2", linecolor="#d0d7de")
    fig.update_yaxes(row=1, col=2, type="log", gridcolor="#eaeef2")
    fig.update_layout(template="plotly_white", height=360, showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="#f6f8fa",
                      font=dict(family="Inter, sans-serif", size=12))
    return fig


def plot_residuals(residuals, y_true=None):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Residual vs Index", "Distribusi Residual"],
                        horizontal_spacing=0.12)
    idx = list(range(len(residuals)))
    fig.add_trace(go.Scatter(x=idx, y=residuals, mode="markers",
                             marker=dict(color=PRIMARY, size=4, opacity=0.7),
                             name="Residual"),
                  row=1, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="#8c959f", line_width=1.2, row=1, col=1)
    fig.add_trace(go.Histogram(x=residuals, nbinsx=24,
                               marker_color=SECONDARY, opacity=0.8, name="Distribusi"),
                  row=1, col=2)
    fig.update_xaxes(gridcolor="#eaeef2", linecolor="#d0d7de")
    fig.update_yaxes(gridcolor="#eaeef2", linecolor="#d0d7de")
    fig.update_layout(template="plotly_white", height=340, showlegend=False,
                      paper_bgcolor="white", plot_bgcolor="#f6f8fa",
                      font=dict(family="Inter, sans-serif", size=12))
    return fig


def plot_sensitivity(sensitivity_df):
    fig = px.bar(sensitivity_df, x="Parameter", y="Sensitivity Index",
                 color="Sensitivity Index",
                 color_continuous_scale=["#1a7f37", "#d4a72c", "#cf222e"],
                 title="Analisis Sensitivitas Parameter (±5%)")
    fig.update_traces(marker_line_width=0)
    fig = _apply_base(fig, height=340)
    return fig


def plot_diode_iv(V_source, V_diode, I_diode):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=V_diode, y=I_diode * 1000, mode="lines",
        line=dict(color=DANGER, width=2.5), name="I-V Dioda"))
    fig = _apply_base(fig, title="Karakteristik I-V Dioda",
                      xaxis_title="V_D (V)", yaxis_title="I_D (mA)")
    return fig
