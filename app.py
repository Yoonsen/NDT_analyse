import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(page_title="Dependenstrebank", layout="wide", initial_sidebar_state="auto", menu_items=None)

@st.cache()
def get_ndt():
    df = pd.read_csv('NDT/ndt_nob.csv', index_col = 0)
    sent = pd.read_csv('NDT/setninger.csv', index_col = 0)
    return df, sent




def make_sentence_graph(indx):
    edges = ndt[ndt.sent_id == indx]["token_order head deprel".split()]
    nodes = ndt[ndt.sent_id == indx]["token_order form".split()]

    edgelist = [(int(e[1].token_order), int(e[1]['head']), {'name':e[1].deprel}) for e in edges.iterrows()]
    nodelist = [(int(e[1].token_order), {'name':e[1]['form']}) for e in nodes.iterrows()] 

    G = nx.DiGraph()

    G.add_edges_from(edgelist)
    G.add_nodes_from(nodelist)
    
    # add name for root element
    G.nodes[0]['name'] = 'root'
    return G


def draw_graph(G):
    edgelabels = {(x[0], x[1]):x[2]['name'] for x in G.edges(data=True)}
    nodelabels = {x[0]:x[1]['name'] for x in G.nodes(data=True)}
    pos =  nx.nx_agraph.graphviz_layout(G, prog="dot")
    fig = plt.figure(figsize=(16,8))
    # nodes
    options = {"edgecolors": "tab:gray", "node_size": 0, "alpha": 0.9}
    # n1 = list(G.nodes)[:int(len(list(G.nodes))/2)]
    # n2 = list(G.nodes)[int(len(list(G.nodes))/2):]
    # nx.draw_networkx_nodes(G, pos,nodelist = n1, node_color="tab:red", **options)
    # nx.draw_networkx_nodes(G, pos,nodelist = n2, node_color="tab:blue", **options)

    # edges
    
    nx.draw_networkx_edges(G, pos, width=1.2, alpha=0.2, arrows=True) #, connectionstyle="arc3,rad=0.3");
    nx.draw_networkx_edge_labels(G, pos, edge_labels = edgelabels, font_size=10,font_color='red');
    nx.draw_networkx_labels(G, pos, labels = nodelabels, font_color='blue', font_size=12);
    st.pyplot(fig)


ndt, sent = get_ndt()

s = st.text_input("Velg et ord fra en setning eller skriv inn et nummer mellom 1 og 4310", "", help="Om input ikke gjenkjennes velges en tilfeldig trestruktur")
try:
    ix = int(s)
    if not 1 <= ix <= 4310:
        ix = list(sent.sample(1).index)[0]
except:
    try:
        ix = list(sent[sent['form'].str.contains(s)].sample(1).index)[0]
    except:
        ix = list(sent.sample(1).index)[0]
try:   
    G = make_sentence_graph(ix)
    draw_graph(G)
    st.write(sent.loc[ix])
except:
    st.write('...gulp... noe gikk galt... prøv igjen!')