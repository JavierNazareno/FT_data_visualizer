# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 19:42:50 2025

@author: javie
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from time_series_plotter import TimeSeriesPlotter
import plotly.io as pio
import io

st.set_page_config(layout="wide")
st.title("📈 Flight Test Data Visualizer")

# File upload
uploaded_file = st.file_uploader(
    "Upload your CSV file", type="csv",
    help="Upload a CSV file containing flight test time series data."
)

# Default Plotly colors
DEFAULT_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
    "#bcbd22", "#17becf"
]

# Plot style controls
with st.sidebar:
    st.markdown("## ⚙️ Plot Settings")
    show_xgrid = st.checkbox("Show X-axis gridlines", value=True)
    show_ygrid = st.checkbox("Show Y-axis gridlines", value=True)
    subdivisions = st.selectbox(
        "Number of subdivisions (minor gridlines)",
        options=[0, 2, 5, 10],
        index=2,
        help="Number of minor gridlines between major ticks"
    )
    plot_style = st.radio(
        "Plot style",
        ["Lines", "Markers only", "Lines + markers"],
        index=0
    )
    marker_size = st.slider(
        "Marker size", 2, 12, value=6,
        help="Size of data point markers"
    )
    show_hover = st.checkbox("Show tooltips (hover info)", value=True)

    st.markdown("## 💾 Export Options")
    export_format = st.radio("Export format", ["PNG", "HTML"], horizontal=True)
    export_button = st.button("📤 Export plot")


# Centralized plot builder
def create_plotly_figure(data, grouping, x_title, y_titles, style_map):
    if not data:
        return None

    if grouping == 0 and len(data) > 1:
        fig = make_subplots(rows=len(data), cols=1, shared_xaxes=True, subplot_titles=y_titles)
        for i, trace in enumerate(data):
            name = trace["name"]
            fig.add_trace(go.Scatter(
                x=trace["x"], y=trace["y"], name=name,
                mode=style_map[name]["mode"],
                marker=dict(size=style_map[name]["marker_size"],
                            color=style_map[name]["color"],
                            symbol=style_map[name]["marker"]),
                line=dict(color=style_map[name]["color"],
                          dash=style_map[name]["line"]),
                hoverinfo="x+y+name" if style_map[name]["hover"] else "skip"
            ), row=i+1, col=1)
            fig.update_yaxes(title_text=name, row=i+1, col=1,
                             showgrid=style_map[name]["ygrid"],
                             gridcolor="#444",
                             minor=dict(showgrid=style_map[name]["subdiv"] > 0,
                                        gridcolor="#888", nticks=style_map[name]["subdiv"] + 1))
            fig.update_xaxes(title_text=x_title, row=i+1, col=1,
                             showgrid=style_map[name]["xgrid"],
                             gridcolor="#444",
                             minor=dict(showgrid=style_map[name]["subdiv"] > 0,
                                        gridcolor="#888", nticks=style_map[name]["subdiv"] + 1))
        fig.update_layout(height=300 * len(data), hovermode="x unified")

    else:
        fig = go.Figure()
        layout_yaxes = {}
        for i, trace in enumerate(data):
            name = trace["name"]
            axis_name = "yaxis" if i == 0 else f"yaxis{i+1}"
            yref = "y" if i == 0 else f"y{i+1}"

            fig.add_trace(go.Scatter(
                x=trace["x"], y=trace["y"], name=name,
                mode=style_map[name]["mode"],
                yaxis=yref,
                marker=dict(size=style_map[name]["marker_size"],
                            color=style_map[name]["color"],
                            symbol=style_map[name]["marker"]),
                line=dict(color=style_map[name]["color"],
                          dash=style_map[name]["line"]),
                hoverinfo="x+y+name" if style_map[name]["hover"] else "skip"
            ))

            layout_yaxes[axis_name] = dict(
                title=name,
                side="left",
                overlaying="y" if i > 0 else None,
                anchor="free" if i > 0 else None,
                autoshift=True,
                tickmode="sync" if i > 0 else "auto",
                showgrid=(i == 0 and style_map[name]["ygrid"]),
                gridcolor="#444",
                minor=dict(showgrid=style_map[name]["subdiv"] > 0,
                           gridcolor="#888", nticks=style_map[name]["subdiv"] + 1)
            )

        fig.update_layout(
            xaxis=dict(
                title=x_title,
                showgrid=show_xgrid,
                gridcolor="#444",
                minor=dict(showgrid=subdivisions > 0, gridcolor="#888", nticks=subdivisions + 1)
            ),
            hovermode="x unified",
            **layout_yaxes
        )
    return fig

# Main plotting logic
if uploaded_file:
    plotter = TimeSeriesPlotter(uploaded_file)
    all_vars = [col for col in plotter.df.columns if col not in ["Time", "time_seconds", "time_from_zero"]]
    plot_type = st.selectbox("Choose plot type", ["Timeplot", "Testplot", "VarTimeplot", "VarTestplot"])

    if plot_type == "Timeplot":
        variables = st.multiselect("Select variable(s) to plot", all_vars)
        grouping = 1 if st.checkbox("Group parameters in same plot") else 0
        tini = st.text_input("Start time (in seconds)", value="0")
        tfin = st.text_input("End time (in seconds)", value="")

        if variables:
            st.markdown("### 🎨 Customize styles per variable")
            style_map = {}
            for i, var in enumerate(variables):
                with st.sidebar.expander(f"Style for {var}", expanded=True):
                    color = st.color_picker("Color", value=DEFAULT_COLORS[i % len(DEFAULT_COLORS)], key=f"{var}_color")
                    line = st.selectbox("Line style", ["solid", "dash", "dot", "dashdot"], key=f"{var}_line")
                    marker = st.selectbox("Marker shape", ["circle", "square", "diamond", "cross", "x"], key=f"{var}_marker")
                style_map[var] = {
                    "color": color,
                    "line": line,
                    "marker": marker,
                    "mode": {
                        "Lines": "lines",
                        "Markers only": "markers",
                        "Lines + markers": "lines+markers"
                    }[plot_style],
                    "marker_size": marker_size,
                    "hover": show_hover,
                    "xgrid": show_xgrid,
                    "ygrid": show_ygrid,
                    "subdiv": subdivisions
                }

            data = plotter.timeplot_data(variables, time_type=1, tini=float(tini), tfin=float(tfin) if tfin else None)
            fig = create_plotly_figure(data, grouping, "Time (s)", [d["name"] for d in data], style_map)

            if fig:
                st.plotly_chart(fig, use_container_width=True)

                # Export options
                if export_button:
                    if export_format == "PNG":
                        buf = io.BytesIO()
                        fig.write_image(buf, format="png")
                        st.download_button("Download PNG", buf.getvalue(), file_name="plot.png", mime="image/png")
                    elif export_format == "HTML":
                        html = pio.to_html(fig, full_html=False)
                        st.download_button("Download HTML", html, file_name="plot.html", mime="text/html")


    elif plot_type == "Testplot":
        variables = st.multiselect("Select variable(s) to plot", all_vars)
        test_points = sorted(plotter.df["test_point"].dropna().unique().astype(int))
        test = st.selectbox("Select Test Point", options=test_points)
        active_value = st.radio("Active State", [0, 1], horizontal=True)
        grouping = 1 if st.checkbox("Group parameters in same plot") else 0

        if variables:
            st.markdown("### 🎨 Customize styles per variable")
            style_map = {}
            for i, var in enumerate(variables):
                with st.sidebar.expander(f"Style for {var}", expanded=True):
                    color = st.color_picker("Color", value=DEFAULT_COLORS[i % len(DEFAULT_COLORS)], key=f"{var}_color_test")
                    line = st.selectbox("Line style", ["solid", "dash", "dot", "dashdot"], key=f"{var}_line_test")
                    marker = st.selectbox("Marker shape", ["circle", "square", "diamond", "cross", "x"], key=f"{var}_marker_test")
                style_map[var] = {
                    "color": color,
                    "line": line,
                    "marker": marker,
                    "mode": {
                        "Lines": "lines",
                        "Markers only": "markers",
                        "Lines + markers": "lines+markers"
                    }[plot_style],
                    "marker_size": marker_size,
                    "hover": show_hover,
                    "xgrid": show_xgrid,
                    "ygrid": show_ygrid,
                    "subdiv": subdivisions
                }

            data = plotter.testplot_data(variables, test=test, active_value=active_value, time_type=1)
            fig = create_plotly_figure(data, grouping, "Time (s)", [d["name"] for d in data], style_map)

            if fig:
                st.plotly_chart(fig, use_container_width=True)

                if export_button:
                    if export_format == "PNG":
                        buf = io.BytesIO()
                        fig.write_image(buf, format="png")
                        st.download_button("Download PNG", buf.getvalue(), file_name="plot.png", mime="image/png")
                    elif export_format == "HTML":
                        html = pio.to_html(fig, full_html=False)
                        st.download_button("Download HTML", html, file_name="plot.html", mime="text/html")


    elif plot_type == "VarTimeplot":
        variable_x = st.selectbox("Select variable for X-axis", all_vars)
        variables_y = st.multiselect("Select variable(s) for Y-axis", all_vars)
        grouping = 1 if st.checkbox("Group parameters in same plot") else 0
        tini = st.text_input("Start time (in seconds)", value="0")
        tfin = st.text_input("End time (in seconds)", value="")

        if variable_x and variables_y:
            st.markdown("### 🎨 Customize styles per variable")
            style_map = {}
            for i, var in enumerate(variables_y):
                with st.sidebar.expander(f"Style for {var}", expanded=True):
                    color = st.color_picker("Color", value=DEFAULT_COLORS[i % len(DEFAULT_COLORS)], key=f"{var}_color_vartime")
                    line = st.selectbox("Line style", ["solid", "dash", "dot", "dashdot"], key=f"{var}_line_vartime")
                    marker = st.selectbox("Marker shape", ["circle", "square", "diamond", "cross", "x"], key=f"{var}_marker_vartime")
                style_map[var] = {
                    "color": color,
                    "line": line,
                    "marker": marker,
                    "mode": {
                        "Lines": "lines",
                        "Markers only": "markers",
                        "Lines + markers": "lines+markers"
                    }[plot_style],
                    "marker_size": marker_size,
                    "hover": show_hover,
                    "xgrid": show_xgrid,
                    "ygrid": show_ygrid,
                    "subdiv": subdivisions
                }

            data = plotter.vartimeplot_data(variable_x, variables_y, time_type=1, tini=float(tini), tfin=float(tfin) if tfin else None)
            fig = create_plotly_figure(data, grouping, variable_x, [d["name"] for d in data], style_map)

            if fig:
                st.plotly_chart(fig, use_container_width=True)

                if export_button:
                    if export_format == "PNG":
                        buf = io.BytesIO()
                        fig.write_image(buf, format="png")
                        st.download_button("Download PNG", buf.getvalue(), file_name="plot.png", mime="image/png")
                    elif export_format == "HTML":
                        html = pio.to_html(fig, full_html=False)
                        st.download_button("Download HTML", html, file_name="plot.html", mime="text/html")


    elif plot_type == "VarTestplot":
        variable_x = st.selectbox("Select variable for X-axis", all_vars, key="var_x_vartest")
        variables_y = st.multiselect("Select variable(s) for Y-axis", all_vars, key="var_y_vartest")
        test_points = sorted(plotter.df["test_point"].dropna().unique().astype(int))
        test = st.selectbox("Select Test Point", options=test_points)
        active_value = st.radio("Active State", [0, 1], horizontal=True)
        grouping = 1 if st.checkbox("Group parameters in same plot") else 0

        if variable_x and variables_y:
            st.markdown("### 🎨 Customize styles per variable")
            style_map = {}
            for i, var in enumerate(variables_y):
                with st.sidebar.expander(f"Style for {var}", expanded=True):
                    color = st.color_picker("Color", value=DEFAULT_COLORS[i % len(DEFAULT_COLORS)], key=f"{var}_color_vartest")
                    line = st.selectbox("Line style", ["solid", "dash", "dot", "dashdot"], key=f"{var}_line_vartest")
                    marker = st.selectbox("Marker shape", ["circle", "square", "diamond", "cross", "x"], key=f"{var}_marker_vartest")
                style_map[var] = {
                    "color": color,
                    "line": line,
                    "marker": marker,
                    "mode": {
                        "Lines": "lines",
                        "Markers only": "markers",
                        "Lines + markers": "lines+markers"
                    }[plot_style],
                    "marker_size": marker_size,
                    "hover": show_hover,
                    "xgrid": show_xgrid,
                    "ygrid": show_ygrid,
                    "subdiv": subdivisions
                }

            data = plotter.vartestplot_data(variable_x, variables_y, test=test, active_value=active_value)
            fig = create_plotly_figure(data, grouping, variable_x, [d["name"] for d in data], style_map)

            if fig:
                st.plotly_chart(fig, use_container_width=True)

                if export_button:
                    if export_format == "PNG":
                        buf = io.BytesIO()
                        fig.write_image(buf, format="png")
                        st.download_button("Download PNG", buf.getvalue(), file_name="plot.png", mime="image/png")
                    elif export_format == "HTML":
                        html = pio.to_html(fig, full_html=False)
                        st.download_button("Download HTML", html, file_name="plot.html", mime="text/html")

