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
uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type="csv",
    help="Upload a CSV file containing time-series flight test data. Columns like 'Time', 'test_point', 'active' should be present."
)

# Step 2: If file uploaded, initialize plotter and show options
if uploaded_file:
    plotter = TimeSeriesPlotter(uploaded_file)
    all_vars = [col for col in plotter.df.columns if col not in ["Time", "time_seconds", "time_from_zero"]]

    # Step 3: Select plot type
    plot_type = st.selectbox(
        "Choose plot type",
        ["Timeplot", "Testplot", "VarTimeplot", "VarTestplot"],
        help="Choose how you want to visualize your data: \n- Timeplot: Y variables vs time \n- Testplot: Filter by test point \n- VarTimeplot: Y vs custom X over time \n- VarTestplot: Y vs custom X for a test point"
    )

    # Step 4: Logic for each plot type
    if plot_type == "Timeplot":
        variables = st.multiselect(
            "Select variable(s) to plot",
            all_vars,
            help="Select one or more variables to plot against time."
        )
        grouping = 1 if st.checkbox(
            "Group parameters in same plot",
            help="If selected, variables will be shown in one plot with separate Y axes. Otherwise, each variable will get its own subplot."
        ) else 0

        st.markdown("### Time Range Filter")
        tini = st.text_input(
            "Start time (in seconds)",
            value="0",
            help="Start time for filtering the data (relative to time_from_zero = 0)."
        )
        tfin = st.text_input(
            "End time (in seconds)",
            value="",
            help="End time for filtering the data. Leave blank to use the full time range."
        )

        if st.button("📊 Generate Timeplot") and variables:
            fig = plotter.timeplot(
                variables=variables,
                time_type=1,
                tini=float(tini),
                tfin=float(tfin) if tfin else None,
                grouping=grouping
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    elif plot_type == "Testplot":
        variables = st.multiselect(
            "Select variable(s) to plot",
            all_vars,
            help="Select one or more variables to plot against time, filtered by test point and active value."
        )
        test_points = sorted(plotter.df["test_point"].dropna().unique().astype(int))
        test = st.selectbox(
            "Select Test Point",
            options=test_points,
            help="Choose one of the available test points found in the 'test_point' column of the dataset."
        )
        active_value = st.radio(
            "Active State",
            [0, 1],
            horizontal=True,
            help="Use rows where the 'active' column equals this value."
        )
        grouping = 1 if st.checkbox(
            "Group parameters in same plot",
            help="If selected, variables will be shown in one plot with separate Y axes. Otherwise, each variable will get its own subplot."
        ) else 0

        if st.button("📊 Generate Testplot") and variables:
            fig = plotter.testplot(
                variables=variables,
                test=int(test),
                active_value=int(active_value),
                time_type=1,
                grouping=grouping
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    elif plot_type == "VarTimeplot":
        variable_x = st.selectbox(
            "Select variable for X-axis",
            all_vars,
            help="This variable will be used for the X-axis in the plot."
        )
        variables_y = st.multiselect(
            "Select variable(s) for Y-axis",
            all_vars,
            help="These variables will be plotted on the Y-axis against the selected X variable."
        )
        grouping = 1 if st.checkbox(
            "Group parameters in same plot",
            help="If selected, all variables will be shown in a single chart. Otherwise, separate subplots will be created."
        ) else 0

        st.markdown("### Time Range Filter")
        tini = st.text_input(
            "Start time (in seconds)",
            value="0",
            help="Start time for filtering the data (relative to time_from_zero = 0)."
        )
        tfin = st.text_input(
            "End time (in seconds)",
            value="",
            help="End time for filtering the data. Leave blank to use the full time range."
        )

        if st.button("📊 Generate VarTimeplot") and variable_x and variables_y:
            fig = plotter.vartimeplot(
                variable_x=variable_x,
                variables_y=variables_y,
                time_type=1,
                tini=float(tini),
                tfin=float(tfin) if tfin else None,
                grouping=grouping
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    elif plot_type == "VarTestplot":
        variable_x = st.selectbox(
            "Select variable for X-axis",
            all_vars,
            key="var_x_vartest",
            help="This variable will be used for the X-axis in the plot."
        )
        variables_y = st.multiselect(
            "Select variable(s) for Y-axis",
            all_vars,
            key="var_y_vartest",
            help="These variables will be plotted on the Y-axis against the selected X variable."
        )
        test_points = sorted(plotter.df["test_point"].dropna().unique().astype(int))
        test = st.selectbox(
            "Select Test Point",
            options=test_points,
            help="Choose one of the available test points found in the 'test_point' column of the dataset."
        )
        active_value = st.radio(
            "Active State",
            [0, 1],
            horizontal=True,
            help="Only rows where the 'active' column matches this value will be used."
        )
        grouping = 1 if st.checkbox(
            "Group parameters in same plot",
            help="If selected, all variables will be shown in a single chart. Otherwise, separate subplots will be created."
        ) else 0

        if st.button("📊 Generate VarTestplot") and variable_x and variables_y:
            fig = plotter.vartestplot(
                variable_x=variable_x,
                variables_y=variables_y,
                test=int(test),
                active_value=int(active_value),
                grouping=grouping
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)
