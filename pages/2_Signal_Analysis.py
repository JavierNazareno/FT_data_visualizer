import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from time_series_plotter import TimeSeriesPlotter
from signal_analysis import signal_analysis

st.set_page_config(layout="wide")
st.title("🔍 Signal Analysis — Oscillatory Behavior")

uploaded_file = st.file_uploader(
    "Upload your CSV file", type="csv",
    help="Upload a CSV file containing flight test time series data."
)
delimiter = st.radio("Select CSV delimiter", [",", ";"], index=0, horizontal=True)

if uploaded_file:
    plotter = TimeSeriesPlotter(uploaded_file, delimiter=delimiter)
    all_vars = [col for col in plotter.df.columns if col not in ["Time", "time_seconds", "time_from_zero"]]

    plot_type = st.selectbox(
        "Choose plot type",
        ["Timeplot", "Testplot"],
        help="Choose how to select the signal range: \n- Timeplot: filter by time range \n- Testplot: filter by test point and active flag"
    )
    
    
    if plot_type == "Timeplot":
        variables = st.multiselect("Select variable(s) to analyze", all_vars)
        remove_static = st.checkbox("Remove static offset using high-pass filter")

        st.markdown("### Time Range Filter")
        tini = st.text_input("Start time (in seconds)", value="0")
        tfin = st.text_input("End time (in seconds)", value="")

        if st.button("📊 Generate Timeplot") and variables:
            for var in variables:
                data = plotter.timeplot_data([var], time_type=1, tini=float(tini), tfin=float(tfin) if tfin else None)
                if not data:
                    st.warning(f"No data found for variable '{var}' in specified time range.")
                    continue

                t = np.array(data[0]["x"])
                x = np.array(data[0]["y"])

                sa = signal_analysis(t, x)
                approx, filtered, results = sa.fit(remove_static=remove_static)

                
                st.markdown(f"#### 📉 Signal: {var}")
                
                fig = go.Figure()

                # Original signal on left axis
                fig.add_trace(go.Scatter(
                    x=t, y=x, name="Original",
                    yaxis="y", line=dict(color='gray', dash='dot')
                ))
                
                # Filtered signal on right axis
                fig.add_trace(go.Scatter(
                    x=t, y=filtered, name="Filtered",
                    yaxis="y2", line=dict(color='orange')
                ))
                
                # Fitted curve on right axis
                fig.add_trace(go.Scatter(
                    x=t, y=approx, name="Fitted",
                    yaxis="y2", line=dict(color='blue', dash='dash')
                ))
                
                fig.update_layout(
                    title=f"Signal Fit — {var}",
                    xaxis=dict(
                        title="Time (s)",
                        showgrid=True,
                        gridcolor="#444",
                        minor=dict(showgrid=True, gridcolor="#888", nticks=5)
                    ),
                    yaxis=dict(
                        title="Original Signal",
                        showgrid=True,
                        gridcolor="#444",
                        minor=dict(showgrid=True, gridcolor="#888", nticks=5)
                    ),
                    yaxis2=dict(
                        title="Filtered & Fitted",
                        overlaying="y",
                        anchor="free",
                        side="right",
                        position=1.0,
                        tickmode="sync",
                        showgrid=True,
                        gridcolor="#444",
                        minor=dict(showgrid=True, gridcolor="#888", nticks=5)
                    ),
                    legend=dict(x=0.01, y=0.99),
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 🧮 Fitted Parameters")

                st.markdown(f"""
                $$
                \\begin{{aligned}}
                A &= {results['A']:.3f} \\\\
                \\zeta &= {results['zeta']:.4f} \\quad \\text{{(damping ratio, unitless)}} \\\\
                \\omega_n &= {results['omega_n']:.3f} \\ \\text{{rad/s}} \\quad \\text{{(natural frequency)}} \\\\
                \\phi &= {results['phi']:.3f} \\ \\text{{rad}} \\quad \\text{{(phase shift)}} \\\\
                \\omega_d &= {results['omega_d']:.3f} \\ \\text{{rad/s}} \\quad \\text{{(damped frequency)}} \\\\
                \\delta &= {results['delta']:.3f} \\ \\text{{1/s}} \\quad \\text{{(damping coefficient)}} \\\\
                T &= {results['T']:.3f} \\ \\text{{s}} \\quad \\text{{(period)}} \\\\
                t_2 &= {results['t2 (half/double)']:.3f} \\ \\text{{s}} \\quad \\text{{(time to half/double)}}
                \\end{{aligned}}
                $$
                """, unsafe_allow_html=True)

    elif plot_type == "Testplot":
        variables = st.multiselect("Select variable(s) to analyze", all_vars)
        remove_static = st.checkbox("Remove static offset using high-pass filter")
        test_points = sorted(plotter.df["test_point"].dropna().unique().astype(int))
        test = st.selectbox("Select Test Point", options=test_points)
        active_value = st.radio("Active State", [0, 1], horizontal=True)

        if st.button("📊 Generate Testplot") and variables:
            for var in variables:
                data = plotter.testplot_data([var], test=test, active_value=active_value, time_type=1)
                if not data:
                    st.warning(f"No data found for variable '{var}' with test point {test}.")
                    continue

                t = np.array(data[0]["x"])
                x = np.array(data[0]["y"])

                sa = signal_analysis(t, x)
                approx, filtered, results = sa.fit(remove_static=remove_static)


                st.markdown(f"#### 📉 Signal: {var} (Test Point {test})")
                fig = go.Figure()

                # Original signal on left axis
                fig.add_trace(go.Scatter(
                    x=t, y=x, name="Original",
                    yaxis="y", line=dict(color='gray', dash='dot')
                ))
                
                # Filtered signal on right axis
                fig.add_trace(go.Scatter(
                    x=t, y=filtered, name="Filtered",
                    yaxis="y2", line=dict(color='orange')
                ))
                
                # Fitted curve on right axis
                fig.add_trace(go.Scatter(
                    x=t, y=approx, name="Fitted",
                    yaxis="y2", line=dict(color='blue', dash='dash')
                ))
                
                fig.update_layout(
                    title=f"Signal Fit — {var}",
                    xaxis=dict(
                        title="Time (s)",
                        showgrid=True,
                        gridcolor="#444",
                        minor=dict(showgrid=True, gridcolor="#888", nticks=5)
                    ),
                    yaxis=dict(
                        title="Original Signal",
                        showgrid=True,
                        gridcolor="#444",
                        minor=dict(showgrid=True, gridcolor="#888", nticks=5)
                    ),
                    yaxis2=dict(
                        title="Filtered & Fitted",
                        overlaying="y",
                        anchor="free",
                        side="right",
                        position=1.0,
                        tickmode="sync",
                        showgrid=True,
                        gridcolor="#444",
                        minor=dict(showgrid=True, gridcolor="#888", nticks=5)
                    ),
                    legend=dict(x=0.01, y=0.99),
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### 🧮 Fitted Parameters")

                st.markdown(f"""
                $$
                \\begin{{aligned}}
                A &= {results['A']:.3f} \\\\
                \\zeta &= {results['zeta']:.4f} \\quad \\text{{(damping ratio, unitless)}} \\\\
                \\omega_n &= {results['omega_n']:.3f} \\ \\text{{rad/s}} \\quad \\text{{(natural frequency)}} \\\\
                \\phi &= {results['phi']:.3f} \\ \\text{{rad}} \\quad \\text{{(phase shift)}} \\\\
                \\omega_d &= {results['omega_d']:.3f} \\ \\text{{rad/s}} \\quad \\text{{(damped frequency)}} \\\\
                \\delta &= {results['delta']:.3f} \\ \\text{{1/s}} \\quad \\text{{(damping coefficient)}} \\\\
                T &= {results['T']:.3f} \\ \\text{{s}} \\quad \\text{{(period)}} \\\\
                t_2 &= {results['t2 (half/double)']:.3f} \\ \\text{{s}} \\quad \\text{{(time to half/double)}}
                \\end{{aligned}}
                $$
                """, unsafe_allow_html=True)
