# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 16:57:58 2025

@author: javie
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class TimeSeriesPlotter:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.df = self._add_time_from_zero(self.df)

    def _convert_time_to_seconds(self, time_str):
        try:
            days, hours, minutes, seconds = map(float, time_str.split(":"))
            return days * 86400 + hours * 3600 + minutes * 60 + seconds
        except:
            return None

    def _seconds_to_time_str(self, total_seconds):
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60
        return f"{days:03}:{hours:02}:{minutes:02}:{seconds:06.3f}"

    def _add_time_from_zero(self, df):
        df["time_seconds"] = df["Time"].apply(self._convert_time_to_seconds)
        df["time_from_zero"] = df["time_seconds"] - df["time_seconds"].iloc[0]
        return df

    def _compute_aligned_yaxes(self, df, variables):
        layout_yaxes = {}
        tick_count = 5

        for i, var in enumerate(variables):
            series = df[var].dropna()
            y_min = series.min()
            y_max = series.max()
            y_range = y_max - y_min
            dtick = y_range / tick_count

            axis_key = "yaxis" if i == 0 else f"yaxis{i+1}"

            layout_yaxes[axis_key] = dict(
                title=var,
                range=[y_min, y_max] if i > 0 else None,
                side="left",
                overlaying="y" if i > 0 else None,
                tickmode="sync" if i > 0 else None,
                anchor="free" if i > 0 else None,
                autoshift=True
            )

        return layout_yaxes

    def timeplot(self, variables, time_type=0, tini=0, tfin=None, grouping=0):
        if isinstance(variables, str):
            variables = [variables]

        time_col = "time_seconds" if time_type == 0 else "time_from_zero"
        tini_sec = self._convert_time_to_seconds(tini) if time_type == 0 else tini
        tfin_sec = self._convert_time_to_seconds(tfin) if time_type == 0 and tfin else self.df[time_col].max()

        if tini_sec < self.df[time_col].min() or tfin_sec > self.df[time_col].max():
            print("Error: Specified time range is outside the available data.")
            return None

        df_plot = self.df[(self.df[time_col] >= tini_sec) & (self.df[time_col] <= tfin_sec)]

        if df_plot.empty:
            print("No data found in the specified time range.")
            return None

        if len(variables) == 1:
            var = variables[0]
            series = df_plot.dropna(subset=[var])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=series[time_col], y=series[var], mode='lines', name=var))
            fig.update_layout(
                title=f"{var} vs {'Time from Zero' if time_type else 'Absolute Time'}",
                xaxis_title="Time (s)" if time_type else "Absolute Time",
                yaxis_title=var,
                hovermode="x unified"
            )
            return fig

        if grouping == 0:
            fig = make_subplots(rows=len(variables), cols=1, shared_xaxes=True, subplot_titles=variables)
            for i, var in enumerate(variables):
                series = df_plot.dropna(subset=[var])
                fig.add_trace(go.Scatter(x=series[time_col], y=series[var], mode='lines', name=var), row=i+1, col=1)
                fig.update_yaxes(title_text=var, row=i+1, col=1)
            fig.update_layout(
                height=300 * len(variables),
                title="Timeplot (Multiple Subplots)",
                xaxis_title="Time (s)" if time_type else "Absolute Time",
                hovermode="x unified"
            )
        else:
            fig = go.Figure()
            for i, var in enumerate(variables):
                series = df_plot.dropna(subset=[var])
                axis_name = "y" if i == 0 else f"y{i+1}"
                fig.add_trace(go.Scatter(x=series[time_col], y=series[var], mode='lines', name=var, yaxis=axis_name))
            aligned_axes = self._compute_aligned_yaxes(df_plot, variables)
            fig.update_layout(
                title="Timeplot (Grouped)",
                xaxis_title="Time (s)" if time_type else "Absolute Time",
                hovermode="x unified",
                **aligned_axes
            )
        return fig

    def testplot(self, variables, test, active_value=1, time_type=0, grouping=0):
        if isinstance(variables, str):
            variables = [variables]

        if test not in self.df["test_point"].unique():
            print(f"Error: Test point {test} not found in the dataset.")
            return None

        time_col = "time_seconds" if time_type == 0 else "time_from_zero"
        df_plot = self.df[
            (self.df["test_point"] == test) &
            (self.df["active"] == active_value)
        ]

        if df_plot.empty:
            print(f"No data found for test point {test} with active = {active_value}.")
            return None

        if len(variables) == 1:
            var = variables[0]
            series = df_plot.dropna(subset=[var])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=series[time_col], y=series[var], mode='lines', name=var))
            fig.update_layout(
                title=f"{var} — Test {test}, Active = {active_value}",
                xaxis_title="Time (s)" if time_type else "Absolute Time",
                yaxis_title=var,
                hovermode="x unified"
            )
            return fig

        if grouping == 0:
            fig = make_subplots(rows=len(variables), cols=1, shared_xaxes=True, subplot_titles=variables)
            for i, var in enumerate(variables):
                series = df_plot.dropna(subset=[var])
                fig.add_trace(go.Scatter(x=series[time_col], y=series[var], mode='lines', name=var), row=i+1, col=1)
                fig.update_yaxes(title_text=var, row=i+1, col=1)
            fig.update_layout(
                height=300 * len(variables),
                title=f"Testplot — Test {test}, Active = {active_value}",
                xaxis_title="Time (s)" if time_type else "Absolute Time",
                hovermode="x unified"
            )
        else:
            fig = go.Figure()
            for i, var in enumerate(variables):
                series = df_plot.dropna(subset=[var])
                axis_name = "y" if i == 0 else f"y{i+1}"
                fig.add_trace(go.Scatter(x=series[time_col], y=series[var], mode='lines', name=var, yaxis=axis_name))
            aligned_axes = self._compute_aligned_yaxes(df_plot, variables)
            fig.update_layout(
                title=f"Testplot (Grouped) — Test {test}, Active = {active_value}",
                xaxis_title="Time (s)" if time_type else "Absolute Time",
                hovermode="x unified",
                **aligned_axes
            )
        return fig


'''
plotter = TimeSeriesPlotter("230505_2_Guy2.csv")

plotter.timeplot("COLLECTVE", time_type=1, tini=0, tfin=10)
plotter.timeplot("COLLECTVE", time_type=0, tini="001:01:03:42.400", tfin="001:01:03:52.400")

plotter.testplot("COLLECTVE", test=20, time_type=0)
plotter.testplot("COLLECTVE", test=20, time_type=1)

plotter.timeplot(["COLLECTVE", "gnss_alt_ft", "Yaw_Pedals"], time_type=1, tini=0, tfin=50, grouping=0)
plotter.testplot(["COLLECTVE", "gnss_alt_ft", "Yaw_Pedals"], test=35, time_type=1, grouping=1)

'''