import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import visualisations as vis
import plotly.graph_objects as go

def get_election_parties(df, year):
    parties = []
    for col in df.columns:
        if (year in col and "elect" not in col and "id" not in col and "cons" not in col and "region" not in col and "country" not in col and "valid" not in col and "party" not in col and "share" not in col and "bound" not in col and "result" not in col):
            parties.append(col.replace(str(year + "_"), ""))
    return parties

def print_summary_election_result(df, year, compare_df=None, compare_year=None, additional_title=None):
    year = str(year)
    
    if ((compare_df is not None) and (compare_year != None)):
        print("====================================================================================================")
        print("=== " + year + " general election summary (compared with " + str(compare_year) + ")")
        if (additional_title != None):
            print("=== " + additional_title)
        print("===================================================================================================")
    
        if (df.shape[0] != compare_df.shape[0]):
            print("(constituency changes occured, difference of " + '{0:+}'.format(df.shape[0] - compare_df.shape[0]) + ")")
        print("\nSEATS WON: ")
        seats_won_this_election = df[year + "_first_party"].value_counts()
        seats_won_compare_election = compare_df[compare_year + "_first_party"].value_counts()
        for party, seats in seats_won_this_election.iteritems():
            if (party in seats_won_compare_election.index):
                print('{:10s}'.format(party) + str(seats) + " (" + '{0:+}'.format(seats - seats_won_compare_election.at[party]) + ")")
            else:
                print('{:10s}'.format(party) + str(seats))
        print("\nVOTE SHARE:")
        # TODO: to_numeric here deals with the fact that some of the election dfs haven't had their vote columns put into pure numeric form
        total_votes_this_election = pd.to_numeric(df[year + "_valid_votes"]).sum(skipna=True)
        total_votes_last_election = pd.to_numeric(compare_df[compare_year + "_valid_votes"]).sum(skipna=True)
        parties_this_election = get_election_parties(df, year)
        parties_last_election = get_election_parties(compare_df, compare_year)
        for party in parties_this_election:
            party_votes_this_election = pd.to_numeric(df[year + "_" + party]).sum(skipna=True)
            party_share_this_election = 100*party_votes_this_election/total_votes_this_election
            if (party in  parties_last_election):
                party_votes_last_election = pd.to_numeric(compare_df[compare_year + "_" + party]).sum(skipna=True)
                party_share_last_election = 100*party_votes_last_election/total_votes_last_election
                print('{:10s}'.format(party) + str(round(party_share_this_election, 1)) + "% (" + '{0:+}'.format(round(party_share_this_election - party_share_last_election, 1)) + "%)")
            else:
                print('{:10s}'.format(party) + str(round(party_share_this_election, 1)) + "%")
    else:
        print("====================================================================================================")
        print("=== " + year + " general election summary")
        print("===================================================================================================")
        print("\nSEATS WON: ")
        print(df[year + "_first_party"].value_counts().to_string())
        print("\nVOTE SHARE:")
        # TODO: to_numeric here deals with the fact that some of the election dfs haven't had their vote columns put into pure numeric form
        total_votes = pd.to_numeric(df[year + "_valid_votes"]).sum(skipna=True)
        parties = get_election_parties(df, year)
        for party in parties:
            party_votes = pd.to_numeric(df[year + "_" + party]).sum(skipna=True)
            print('{:10s}'.format(party) + str(round(100*party_votes/total_votes, 1)) + "%")
    
    print()
            
def calculate_constit_winners(row, year, parties):
    winning_party = "invalid"
    winning_votes = -1
    for party in parties:
        col_name = year + "_" + party
        party_votes = row[col_name]
        if (party_votes != np.nan):
            party_votes = float(party_votes)
            if (party_votes > winning_votes):
                winning_votes = party_votes
                winning_party = party
    return winning_party.lower()

def calculate_constit_runnerup(row, year, parties):
    party_1_votes = row[year + "_" + parties[0]]
    party_2_votes = row[year + "_" + parties[1]]
    if (party_1_votes > party_2_votes):
        winning_party = parties[0]
        winning_votes = party_1_votes
        runner_up_party = parties[1]
        runner_up_votes = party_2_votes
    else:
        winning_party = parties[1]
        winning_votes = party_2_votes
        runner_up_party = parties[0]
        runner_up_votes = party_1_votes
        
    for party in parties[2:]:
        col_name = year + "_" + party
        party_votes = row[col_name]
        if (party_votes != np.nan):
            if (party_votes > winning_votes):
                runner_up_party = winning_party
                runner_up_votes = winning_votes
                winning_party = party
                winning_votes = party_votes
            elif (party_votes > runner_up_votes):
                    runner_up_party = party
                    runner_up_votes = party_votes
    
    return runner_up_party

def calculate_share_change(row, recent_year, distant_year, party):
    recent_election_party_votes_col = recent_year + "_" + party
    recent_election_valid_votes_col = recent_year + "_valid_votes"
    distant_election_party_votes_col = distant_year + "_" + party
    distant_election_valid_votes_col = distant_year + "_valid_votes"
    return 100*(row[recent_election_party_votes_col]/row[recent_election_valid_votes_col] - row[distant_election_party_votes_col]/row[distant_election_valid_votes_col])

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

# Won't work perfectly for comparing using 2010 or earlier as the base year
def calculate_net_volatility(df, compare_year, year):
    total_votes_this_election = pd.to_numeric(df[year + "_valid_votes"]).sum(skipna=True)
    total_votes_last_election = pd.to_numeric(df[compare_year + "_valid_votes"]).sum(skipna=True)
    parties_this_election = get_election_parties(df, year)
    
    pederson_sum = 0
    for party in parties_this_election:
        party_votes_this_election = pd.to_numeric(df[year + "_" + party]).sum(skipna=True)
        party_share_this_election = 100*party_votes_this_election/total_votes_this_election
        party_votes_last_election = pd.to_numeric(df[compare_year + "_" + party]).sum(skipna=True)
        party_share_last_election = 100*party_votes_last_election/total_votes_last_election
        pederson_sum = pederson_sum + abs(party_share_this_election-party_share_last_election)
        
    return pederson_sum/2

# Won't work perfectly for comparing using 2010 or earlier as the base year
def estimate_individual_volatility(df, past_election_column, current_election_column, weight_column):
    df = df[~df[past_election_column].isin(["Didn't vote", "Don't know", " "])]
    df = df[~df[current_election_column].isin(["Didn't vote", "Don't know", " "])]
    total_weight = df[weight_column].sum()
    total_weight_of_changers = 0
    for index, row in df.iterrows():
        if ((row[past_election_column] != row[current_election_column]) and (float(row[weight_column] > 0))):
            total_weight_of_changers = total_weight_of_changers + row[weight_column]
    return 100*total_weight_of_changers/total_weight

# ToDo: handling shape correctly
def create_vote_share_change_maps_and_columns(df, year, compare_year, party_cols_to_map, fig, axes):
    min_share_changes = []
    max_share_changes = []
    
    for party in party_cols_to_map:
        new_col_name = year + "_" + party + "_share_change"
        df[new_col_name] = df.apply(calculate_share_change, args=(year, compare_year, party), axis=1)
        min_share_changes.append(np.min(df[new_col_name]))
        max_share_changes.append(np.max(df[new_col_name]))
    
    no_speaker_df = df[df[year + "_first_party"] != "spk"]
    
    v_min = np.min(min_share_changes)
    v_max = np.max(max_share_changes)
    
    if (np.absolute(v_min) > v_max):
        v_max = -v_min
    else:
        v_min = 0 - v_max
    
    for party_no in range(0, len(party_cols_to_map)):
        party = party_cols_to_map[party_no]
        if (len(np.array(axes.shape)) > 1):
            ax = axes[int(party_no/3), party_no%3]
        else:
            ax = axes[party_no]
        vis.create_continous_constit_map(no_speaker_df, 
                                               col_to_visualise = (year + "_" + party + "_share_change"),
                                               colour_bar_limits = (v_min, v_max),
                                               title = party,
                                               fig = fig,
                                               ax = ax,
                                               colour_map = "PiYG")
    
    plt.tight_layout()
    
    return df

def print_descriptive_summary_statistics(column):
    print("Min:    " + str(column.min()))
    print("Q1:     " + str(column.quantile([0.25]).values[0]))
    print("Median: " + str(column.median()))
    print("Q3:     " + str(column.quantile([0.75]).values[0]))
    print("Max:    " + str(column.max()))
    print("Mean:   " + str(column.mean()))
    print("Mode:   " + str(column.mode().values[0]))
    print("SD:     " + str(column.std()))
    print("Skew:   " + str(column.skew()))
    print("Kurto:  " + str(column.kurtosis()))

def get_ge_colour_map():
    return {
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

def get_regions_colour_map():
    return {
    "scotland": "blue",
    "wales": "red",
    "northern ireland": "lightgreen",
    "north east": "green",
    "north west": "pink",
    "london": "cyan",
    "south east": "orange",
    "west midlands": "yellow",
    "south west": "purple",
    "east": "white",
    "east midlands": "lightblue",
    "yorkshire and the humber": "lightgray"
}