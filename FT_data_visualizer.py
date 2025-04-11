# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 19:42:50 2025

@author: javie
"""
import streamlit as st
from time_series_plotter import TimeSeriesPlotter

st.set_page_config(layout="wide")
st.title("📈 Flight Test Data Visualizer")

# Step 1: Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# Step 2: If file uploaded, initialize plotter and show options
if uploaded_file:
    plotter = TimeSeriesPlotter(uploaded_file)
    all_vars = [col for col in plotter.df.columns if col not in ["Time", "time_seconds", "time_from_zero"]]

    # Step 3: Select plot type
    plot_type = st.selectbox("Choose plot type", ["Timeplot", "Testplot"])

    # Step 4: Show variable selection and grouping option
    selected_vars = st.multiselect("Select variable(s) to plot", all_vars)
    grouping = 1 if st.checkbox("Group parameters in same plot") else 0

    # Step 5: Show inputs based on plot type
    if plot_type == "Timeplot":
        st.markdown("### Timeplot Options")
        tini = st.text_input("Start time (in seconds)", value="0")
        tfin = st.text_input("End time (in seconds)", value="")

        if st.button("📊 Generate Timeplot") and selected_vars:
            fig = plotter.timeplot(
                variables=selected_vars,
                time_type=1,  # Always use relative time
                tini=float(tini),
                tfin=float(tfin) if tfin else None,
                grouping=grouping
            )
            if fig:
                for i in range(len(selected_vars)):
                    xaxis_name = f"xaxis{i+1}" if i > 0 and grouping == 0 else "xaxis"
                    yaxis_name = f"yaxis{i+1}" if i > 0 or grouping == 0 else "yaxis"
                    fig.update_layout({
                        xaxis_name: dict(
                            showgrid=True,
                            gridcolor="#444444",
                            minor=dict(showgrid=True, gridcolor="#888888")
                        ),
                        yaxis_name: dict(
                            showgrid=True,
                            gridcolor="#444444",
                            minor=dict(showgrid=True, gridcolor="#888888")
                        )
                    })
                st.plotly_chart(fig, use_container_width=True)

    elif plot_type == "Testplot":
        st.markdown("### Testplot Options")
        test = st.number_input("Test Point", value=0, step=1)
        active_value = st.radio("Active State", [0, 1], horizontal=True)

        if st.button("📊 Generate Testplot") and selected_vars:
            fig = plotter.testplot(
                variables=selected_vars,
                test=int(test),
                active_value=int(active_value),
                time_type=1,
                grouping=grouping
            )
            if fig:
                for i in range(len(selected_vars)):
                    xaxis_name = f"xaxis{i+1}" if i > 0 and grouping == 0 else "xaxis"
                    yaxis_name = f"yaxis{i+1}" if i > 0 or grouping == 0 else "yaxis"
                    fig.update_layout({
                        xaxis_name: dict(
                            showgrid=True,
                            gridcolor="#444444",
                            minor=dict(showgrid=True, gridcolor="#888888")
                        ),
                        yaxis_name: dict(
                            showgrid=True,
                            gridcolor="#444444",
                            minor=dict(showgrid=True, gridcolor="#888888")
                        )
                    })
                st.plotly_chart(fig, use_container_width=True)
