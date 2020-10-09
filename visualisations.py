import utilities
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
import plotly.graph_objects as go

ge_colour_map = {
    "con": "blue",
    "lab": "red",
    "ld": "orange",
    "brexit": "lightblue",
    "ukip": "purple",
    "green": "green",
    "snp": "yellow",
    "pc": "lightgreen",
    "sf": "darkgreen",
    "spk": "lightgray",
    "dup": "#ad494a",
    "sdlp": "#dcc451",
    "uup": "darkblue",
    "alliance": "gold",
    "ind": "gray",
    "other": "gray",
    "invalid": "black",
    "na": "white"
}

# ToDo: error handling

def create_discrete_constit_map(
    constit_data_df,
    col_to_visualise,
    ax = None,
    title = None,
    title_params = {"fontsize": 20, "fontweight": 5},
    default_colour = "white",
    constit_colour_map = ge_colour_map):
    
        # Merge data
        constit_hex_coords_df = pd.read_csv("csvs/constit_hex_coords.csv")
        constit_data_df = pd.merge(constit_hex_coords_df, constit_data_df, on="ons_id")
        # Could do some checking here and a filter
        
        # Do something with this
        y_min = 1000
        y_max = -1000
        
        # Create visualisation
        # Using regular hexagons to keep a nice format
        # Going to keep the regular hexagon with a width of 1 exactly, from this we can
        # then use then use sine to calculate the correct radius of the circle used to draw 
        # the hexagon
        radius = 0.5 / np.sin(np.pi / 3)
        # Then use the radius and some more gemoetry to work out what the spacing on the y-axis will be
        y_spacing = radius + (radius - 0.5/np.tan(np.pi/3))
        
        constit_hexagons = []
        legend_recorder = {}
        
        for index, row in constit_data_df.iterrows():
            constit_x = row["q"]
            constit_y = row["r"]
            # Might have to do a speaker thing here
            constit_value = row[col_to_visualise]
            
            if (constit_y % 2 == 1):
                constit_x = constit_x + 0.5
            constit_y = y_spacing * constit_y
            
            constit_colour = constit_colour_map.get(constit_value, default_colour)
            constit_hexagon = RegularPolygon(
                (constit_x, constit_y),
                numVertices = 6,
                radius = radius,
                edgecolor = "k",
                facecolor = constit_colour)
            
            constit_hexagons.append(constit_hexagon)
            
            if (legend_recorder.get(constit_value) == None):
                legend_recorder[constit_value] = constit_hexagon
        
        collection = PatchCollection(constit_hexagons, match_original=True, alpha=1.0)
        ax.add_collection(collection)
        
        # Clean up and polish
        if title is not None:
            ax.set_title(title, fontdict=title_params)
        ax.set_xlim([constit_data_df["q"].min() - 1, constit_data_df["q"].max() + 1])
        ax.set_ylim([(constit_data_df["r"]*y_spacing).min() - 1, (constit_data_df["r"]*y_spacing).max() + 1])
        ax.legend(legend_recorder.values(), legend_recorder.keys())
        ax.axis("off")
        
        if (len(constit_hexagons) < 649):
            print("Only " + str(len(constit_hexagons)) + " constituencies were animated")

def create_continous_constit_map(
    constit_data_df,
    col_to_visualise,
    fig = None, # necessary for colour bar
    ax = None,
    title = None,
    title_params = {"fontsize": 20, "fontweight": 5},
    colour_map = "PiYG",
    colour_bar_limits = None,
    suppress_con_warning=True):
        
        # Merge data
        constit_hex_coords_df = pd.read_csv("csvs/constit_hex_coords.csv")
        constit_data_df = pd.merge(constit_hex_coords_df, constit_data_df, on="ons_id")
        # Could do some checking here and a filter
        
        # Do something with this
        y_min = 1000
        y_max = -1000
        
        # Create visualisation
        # Using regular hexagons to keep a nice format
        # Going to keep the regular hexagon with a width of 1 exactly, from this we can
        # then use then use sine to calculate the correct radius of the circle used to draw 
        # the hexagon
        radius = 0.5 / np.sin(np.pi / 3)
        # Then use the radius and some more gemoetry to work out what the spacing on the y-axis will be
        y_spacing = radius + (radius - 0.5/np.tan(np.pi/3))
        
        constit_hexagons = []
        constit_colour_values = []
        
        for index, row in constit_data_df.iterrows():
            constit_x = row["q"]
            constit_y = row["r"]
            # Might have to do a speaker thing here
            constit_value = row[col_to_visualise]
            if (constit_value == None):
                constit_value = 0
            
            if (constit_y % 2 == 1):
                constit_x = constit_x + 0.5
            constit_y = y_spacing * constit_y
            
            constit_hexagon = RegularPolygon(
                (constit_x, constit_y),
                numVertices = 6,
                radius = radius,
                edgecolor = "k")
            
            constit_hexagons.append(constit_hexagon)
            constit_colour_values.append(constit_value)
        
        collection = PatchCollection(constit_hexagons, cmap=plt.get_cmap(colour_map), alpha=1.0)
        collection.set_array(np.array(constit_colour_values))
        
        # ToDo: something smarter with the colour bar and symmetrical colouring
        if (colour_bar_limits == None):
            collection.set_clim(np.min(constit_colour_values), np.max(constit_colour_values))
        else:
            collection.set_clim(colour_bar_limits[0], colour_bar_limits[1])
        
        fig.colorbar(collection, ax=ax, shrink=0.5)
        ax.add_collection(collection)
        
        # Clean up and polish
        if title is not None:
            ax.set_title(title, fontdict=title_params)
        ax.set_xlim([constit_data_df["q"].min() - 1, constit_data_df["q"].max() + 1])
        ax.set_ylim([(constit_data_df["r"]*y_spacing).min() - 1, (constit_data_df["r"]*y_spacing).max() + 1])
        ax.axis("off")
        
        if ((len(constit_hexagons) < 649) and (not suppress_con_warning)):
            print("Only " + str(len(constit_hexagons)) + " constituencies were animated")
        
def create_voter_flow_diagram(bes_df, past_election_column, current_election_column, weight_column, parties, party_colours, dont_include, title, other=True):
    bes_df = bes_df[~(bes_df[past_election_column].isin(dont_include)) | ~(bes_df[current_election_column].isin(dont_include))]
    
    if (not other):
        bes_df = bes_df[(bes_df[past_election_column].isin(parties)) & (bes_df[current_election_column].isin(parties))]
    
    sankey_total_weight = bes_df[weight_column].sum()
        
    total_no_parties = len(parties)
    
    source = []
    target = []
    value = []
    
    # parties
    for party_past_election_no in range(0, total_no_parties):
        for party_current_election_no in  range(0, total_no_parties):
            filtered_df = bes_df[
                (bes_df[past_election_column] == parties[party_past_election_no]) 
                & (bes_df[current_election_column] == parties[party_current_election_no])]
            source.append(party_past_election_no)
            target.append(total_no_parties + party_current_election_no)
            value.append(100*filtered_df[weight_column].sum()/sankey_total_weight)
    
    if (other):
        for party_current_election_no in range(0, total_no_parties):
            # other to party
            source.append(total_no_parties*2)
            target.append(total_no_parties + party_current_election_no)
            filtered_df = bes_df[
                    ~(bes_df[past_election_column].isin(parties)) 
                    & ~(bes_df[current_election_column] == parties[party_current_election_no])]
            value.append(100*filtered_df[weight_column].sum()/sankey_total_weight)
            # party to other
            source.append(party_current_election_no)
            target.append(total_no_parties*2 + 1)
            filtered_df = bes_df[
                    ~(bes_df[current_election_column].isin(parties)) 
                    & ~(bes_df[past_election_column] == parties[party_current_election_no])]
            value.append(100*filtered_df[weight_column].sum()/sankey_total_weight)
            
    sank_parties = parties + parties
    sank_colours = party_colours + party_colours
    
    if (other):
        sank_parties = sank_parties + ["Other parties", "Other parties"]
        sank_colours = sank_colours + ["grey", "grey"]
    
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 5,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = sank_parties,
          color = sank_colours
        ),
        link = dict(
          source = source,
          target = target,
          value = value
        ))])
    
    fig.update_layout(title_text=title, font_size=12, height=750)
    fig.show()