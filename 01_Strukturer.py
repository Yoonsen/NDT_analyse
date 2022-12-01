import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(page_title="Dependenstrebank", layout="wide", initial_sidebar_state="auto", menu_items=None)
st.session_state.update(st.session_state)

@st.cache()
def get_ndt():
    df = pd.read_csv('NDT/ndt_all_reduce.csv', index_col = 0)
    sent = pd.read_csv('NDT/setninger.csv', index_col = 0)
    return df, sent




def make_sentence_graph(indx):
    edges = ndt[ndt.sent_id == indx]["token_order head deprel".split()]
    nodes = ndt[ndt.sent_id == indx]["token_order form".split()]

    #edgelist = [(int(e[1].token_order), int(e[1]['head']), {'name':e[1].deprel}) for e in edges.iterrows()]
    edgelist = [(int(e[1]['head']), int(e[1].token_order), {'name':e[1].deprel}) for e in edges.iterrows()]
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
    G.graph.setdefault('graph', {})['rankdir'] = 'BT'
    n = nx.dag_longest_path(G)
    fig = plt.figure(figsize=(16,1.4*len(n)))
    # nodes
    options = {"edgecolors": "tab:gray", "node_size": 0, "alpha": 0.9}
    # n1 = list(G.nodes)[:int(len(list(G.nodes))/2)]
    # n2 = list(G.nodes)[int(len(list(G.nodes))/2):]
    # nx.draw_networkx_nodes(G, pos,nodelist = n1, node_color="tab:red", **options)
    # nx.draw_networkx_nodes(G, pos,nodelist = n2, node_color="tab:blue", **options)

    # edges
    
    nx.draw_networkx_edges(G, pos, width=1.2, alpha=0.3, arrows=True, edge_color='gray') #, connectionstyle="arc3,rad=0.3");
    nx.draw_networkx_edge_labels(G, pos, edge_labels = edgelabels, font_size=8,font_color='orange');
    nx.draw_networkx_labels(G, pos, labels = nodelabels, font_color='darkblue', font_size=12);
    st.pyplot(fig)

st.write("#### Inspiser [Norsk Dependenstrebank](https://www.nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-10/)")
st.write("En trebank over norsk (bokmål og nynorsk). Visualisering med [graphviz](https://graphviz.org/) og [networkx](https://networkx.org)")


if not 'ndt' in st.session_state:
    ndt, sent = get_ndt()
    st.session_state['ndt'] = ndt
    st.session_state['sentences'] = sent
else:
    ndt = st.session_state['ndt']
    sent = st.session_state['sentences']
    
if not 'current' in st.session_state:
    st.session_state['current'] = 1

col1, col2, col3, col4 = st.columns([2,1,2,1])
with col1:
    s = st.text_input("Ord eller nummer", "", help="Søk i setninger eller angi et setningsnummer, de ligger mellom 1 og 4309")

with col4:
    st.write('Utvalg')
    if st.button(f'klikk for tilfeldig', help="Velger en vilkårlig setning"):
        s = list(sent.sample(1).index)[0]
        
with col2:
    #crnt = st.session_state['current']
    antall = st.number_input('antall setninger', min_value = 1, max_value=20, value=4, help="Antall setninger etter første setning, for å se litt diskursting")
with col4:
    pass

#st.write(s)        
try:
    ix = int(s)
    if not 1 <= ix <= 4309:
        ix = list(sent.sample(1).index)[0]
except:
    try:
        ix = list(sent[sent['form'].str.contains(s)].sample(1).index)[0]
    except:
        ix = list(sent.sample(1).index)[0]

#st.write(ix)
st.session_state['current'] = ix

#st.write(st.session_state)
for inx in range(ix, ix+antall):
    try:   
        G = make_sentence_graph(inx)
        draw_graph(G)
        for x in sent.loc[inx]:
            st.write(f"```{x}```")
    except:
        pass
# except:
#     st.write('...gulp... noe gikk galt... prøv igjen!')
  

