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

# Default Plotly colors
DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf"
]

if uploaded_file:
    plotter = TimeSeriesPlotter(uploaded_file, delimiter=delimiter)
    all_vars = [col for col in plotter.df.columns if col not in ["Time", "time_seconds", "time_from_zero"]]

    plot_type = st.selectbox(
        "Choose plot type",
        ["Timeplot", "Testplot"],
        help="Choose how to select the signal range: \n- Timeplot: filter by time range \n- Testplot: filter by test point and active flag"
    )
    
    def plot_signal(t, y, y_fit, y_filtered, styles, variable_name):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t, y=y, name="Original",
            mode=styles["Original"]["mode"],
            marker=dict(color=styles["Original"]["color"], size=styles["Original"]["size"], symbol=styles["Original"]["marker"]),
            line=dict(color=styles["Original"]["color"], dash=styles["Original"]["line"]),
            yaxis="y1"
        ))
        if y_filtered is not None:
            fig.add_trace(go.Scatter(
                x=t, y=y_filtered, name="Filtered",
                mode=styles["Filtered"]["mode"],
                marker=dict(color=styles["Filtered"]["color"], size=styles["Filtered"]["size"], symbol=styles["Filtered"]["marker"]),
                line=dict(color=styles["Filtered"]["color"], dash=styles["Filtered"]["line"]),
                yaxis="y2"
            ))
        fig.add_trace(go.Scatter(
            x=t, y=y_fit, name="Fitted",
            mode=styles["Fitted"]["mode"],
            marker=dict(color=styles["Fitted"]["color"], size=styles["Fitted"]["size"], symbol=styles["Fitted"]["marker"]),
            line=dict(color=styles["Fitted"]["color"], dash=styles["Fitted"]["line"]),
            yaxis="y2"
        ))
        '''

        fig.update_layout(
            yaxis=dict(title="Original", side="left"),
            yaxis2=dict(title="Filtered/Fitted", overlaying="y", side="right", anchor="free", position=1.0),
            xaxis_title="Time (s)",
            title=f"Oscillatory Signal Fit: {variable_name}",
            hovermode="x unified"
        )
        '''
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
            legend=dict(x=0.8, y=1.3),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    def get_style_controls(var_name, default_color):
        with st.sidebar.expander(f"Style for {var_name}", expanded=True):
            color = st.color_picker("Color", value=default_color, key=f"{var_name}_color")
            line = st.selectbox("Line style", ["solid", "dash", "dot", "dashdot"], key=f"{var_name}_line")
            marker = st.selectbox("Marker", ["circle", "square", "diamond", "cross", "x"], key=f"{var_name}_marker")
            style = st.radio("Display mode", ["Lines", "Markers only", "Lines + markers"], key=f"{var_name}_mode")
            size = st.slider("Marker size", 4, 12, value=6, key=f"{var_name}_size")
        return {
            "color": color,
            "line": line,
            "marker": marker,
            "mode": {
                "Lines": "lines",
                "Markers only": "markers",
                "Lines + markers": "lines+markers"
            }[style],
            "size": size
        }
    
    if plot_type == "Timeplot":
        variables = st.multiselect("Select variable(s) to analyze", all_vars)
        remove_static = st.checkbox("Remove static offset using high-pass filter")

        st.markdown("### Time Range Filter")
        tini = st.text_input("Start time (in seconds)", value="0")
        tfin = st.text_input("End time (in seconds)", value="")

        try:
            for var in variables:
                data = plotter.timeplot_data([var], time_type=1, tini=float(tini), tfin=float(tfin) if tfin else None)
                if not data:
                    st.warning(f"No data found for variable '{var}' in specified time range.")
                    continue

                t = np.array(data[0]["x"])
                x = np.array(data[0]["y"])

                sa = signal_analysis(t, x)
                approx, filtered, results = sa.fit(remove_static=remove_static)

                styles = {
                    "Original": get_style_controls("Original", DEFAULT_COLORS[0]),
                    "Filtered": get_style_controls("Filtered", DEFAULT_COLORS[1]),
                    "Fitted": get_style_controls("Fitted", DEFAULT_COLORS[2])
                }

                st.markdown(f"#### 📉 Signal: {var}")
                plot_signal(t, x, approx, filtered, styles, var)
                
                

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
                export_df = pd.DataFrame({
                    "time_seconds": t,
                    "Original": x,
                    "Fitted": approx                    
                })
                if filtered is not None:
                    export_df["Filtered"] = filtered
                
                # Add time_from_zero column
                export_df["time_from_zero"] = export_df["time_seconds"] - export_df["time_seconds"].iloc[0]

                csv = export_df.to_csv(index=False, sep=";").encode("utf-8")
                st.download_button(
                    label="📤 Export data as CSV",
                    data=csv,
                    file_name="signal_analysis_output.csv",
                    mime="text/csv"
                )
                
                # Export fitted param button
                results_df = pd.DataFrame.from_dict(results, orient="index").transpose()
                try:
                    results_df["test_point"]=plotter.df["test_point"].unique()
                except:
                    pass
                param_csv = results_df.to_csv(index=False, sep=";").encode("utf-8")
                
                st.download_button(
                    label="📥 Export fitted parameters as CSV",
                    data=param_csv,
                    file_name="fitted_parameters.csv",
                    mime="text/csv"
                    )

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
    
    elif plot_type == "Testplot":
        variables = st.multiselect("Select variable(s) to analyze", all_vars)
        remove_static = st.checkbox("Remove static offset using high-pass filter")
        test_points = sorted(plotter.df["test_point"].dropna().unique().astype(int))
        test = st.selectbox("Select Test Point", options=test_points)
        active_value = st.radio("Active State", [0, 1], horizontal=True)

        try:
            for var in variables:
                data = plotter.testplot_data([var], test=test, active_value=active_value, time_type=1)
                if not data:
                    st.warning(f"No data found for variable '{var}' with test point {test}.")
                    continue

                t = np.array(data[0]["x"])
                x = np.array(data[0]["y"])

                sa = signal_analysis(t, x)
                approx, filtered, results = sa.fit(remove_static=remove_static)


                styles = {
                    "Original": get_style_controls("Original", DEFAULT_COLORS[0]),
                    "Filtered": get_style_controls("Filtered", DEFAULT_COLORS[1]),
                    "Fitted": get_style_controls("Fitted", DEFAULT_COLORS[2])
                }

                st.markdown(f"#### 📉 Signal: {var}")
                plot_signal(t, x, approx, filtered, styles, var)

                
                
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
                
                export_df = pd.DataFrame({
                    "Time": t,
                    "Original": x,
                    "Fitted": approx,
                    "test_point": plotter.df["test_point"]
                })
                if filtered is not None:
                    export_df["Filtered"] = filtered

                csv = export_df.to_csv(index=False, sep=";").encode("utf-8")
                st.download_button(
                    label="📤 Export data as CSV",
                    data=csv,
                    file_name="signal_analysis_output.csv",
                    mime="text/csv"
                )
                # Export fitted param button
                results_df = pd.DataFrame.from_dict(results, orient="index").transpose()
                param_csv = results_df.to_csv(index=False, sep=";").encode("utf-8")
                st.download_button(
                    label="📥 Export fitted parameters as CSV",
                    data=param_csv,
                    file_name="fitted_parameters.csv",
                    mime="text/csv"
                    )
        except Exception as e:
            st.error(f"⚠️ Error: {e}")

