# -*- coding: utf-8 -*-
"""
Created on Thu Apr 10 16:57:58 2025

@author: javie
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import csv

class TimeSeriesPlotter:
    def __init__(self, csv_path, delimiter=","):
        #delimiter = self.detect_delimiter(csv_path)
        self.df = pd.read_csv(csv_path, delimiter=delimiter)
        self.df = self._add_time_from_zero(self.df)

    def _convert_time_to_seconds(self, time_str):
        try:
            days, hours, minutes, seconds = map(float, time_str.split(":"))
            return days * 86400 + hours * 3600 + minutes * 60 + seconds
        except:
            return None

    def detect_delimiter(self,uploaded_file):
        """
        Detects the delimiter of a CSV file from a Streamlit UploadedFile object.
        """
        uploaded_file.seek(0)  # Reset file pointer to beginning
        sample = uploaded_file.read(2048).decode('utf-8')  # Read and decode
        uploaded_file.seek(0)  # Reset again for actual reading later
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)
        return dialect.delimiter 
        
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

    def timeplot_data(self, variables, time_type=0, tini=0, tfin=None):
        if isinstance(variables, str):
            variables = [variables]
    
        time_col = "time_seconds" if time_type == 0 else "time_from_zero"
        tini_sec = self._convert_time_to_seconds(tini) if time_type == 0 else tini
        if time_type == 0:
            tfin_sec = self._convert_time_to_seconds(tfin) if tfin else self.df["time_seconds"].max()
        else:
            tfin_sec = tfin if tfin is not None else self.df["time_from_zero"].max()
    
        if tini_sec < self.df[time_col].min() or tfin_sec > self.df[time_col].max():
            print("Error: Specified time range is outside the available data.")
            return None
    
        df_plot = self.df[(self.df[time_col] >= tini_sec) & (self.df[time_col] <= tfin_sec)]
    
        return [
            {"x": df_plot[time_col], "y": df_plot[var], "name": var}
            for var in variables if var in df_plot.columns
        ]

    def testplot_data(self, variables, test, active_value=1, time_type=0):
        if isinstance(variables, str):
            variables = [variables]
    
        if test not in self.df["test_point"].unique():
            print(f"Error: Test point {test} not found.")
            return None
    
        time_col = "time_seconds" if time_type == 0 else "time_from_zero"
        df_plot = self.df[
            (self.df["test_point"] == test) &
            (self.df["active"] == active_value)
        ]
    
        return [
            {"x": df_plot[time_col], "y": df_plot[var], "name": var}
            for var in variables if var in df_plot.columns
        ]

    def vartimeplot_data(self, variable_x, variables_y, time_type=0, tini=0, tfin=None):
        if isinstance(variables_y, str):
            variables_y = [variables_y]
    
        time_col = "time_seconds" if time_type == 0 else "time_from_zero"
        tini_sec = self._convert_time_to_seconds(tini) if time_type == 0 else tini
        if time_type == 0:
            tfin_sec = self._convert_time_to_seconds(tfin) if tfin else self.df["time_seconds"].max()
        else:
            tfin_sec = tfin if tfin is not None else self.df["time_from_zero"].max()
    
        df_plot = self.df[(self.df[time_col] >= tini_sec) & (self.df[time_col] <= tfin_sec)]
    
        return [
            {"x": df_plot[variable_x], "y": df_plot[var], "name": var}
            for var in variables_y if var in df_plot.columns
        ]

    
    def vartestplot_data(self, variable_x, variables_y, test, active_value=1):
        if isinstance(variables_y, str):
            variables_y = [variables_y]
    
        if test not in self.df["test_point"].unique():
            print(f"Error: Test point {test} not found.")
            return None
    
        df_plot = self.df[
            (self.df["test_point"] == test) &
            (self.df["active"] == active_value)
        ]
    
        return [
            {"x": df_plot[variable_x], "y": df_plot[var], "name": var}
            for var in variables_y if var in df_plot.columns
        ]
    
