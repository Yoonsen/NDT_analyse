import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


@st.cache()
def get_rels():
    return list(set(list(ndt.deprel.values)))

@st.cache()
def get_ndt():
    df = pd.read_csv('NDT/ndt_all_reduce.csv', index_col = 0)
    sent = pd.read_csv('NDT/setninger.csv', index_col = 0)
    return df, sent

st.session_state.update(st.session_state)


if not 'ndt' in st.session_state:
    ndt, sent = get_ndt()
    st.session_state['ndt'] = ndt
    st.session_state['sentences'] = sent
else:
    ndt = st.session_state['ndt']
    sent = st.session_state['sentences']


deprels = get_rels()

#with st.form('Velg målføre og relasjoner'):
    
col1, col2 = st.columns([1,3])

with col1:
    lang = st.selectbox('Målføre', ['nb-NO', 'nn-NO'])
with col2:
    rels = st.multiselect('Relasjoner', deprels, default = deprels[:4]) 

#    if st.form_submit_button('Analyser distanse'):    
df = ndt[ndt.language_code == lang] 
diffs = abs(df[['token_order', 'head']].diff(axis = 1)['head'])
df['diffs'] = diffs
if rels != []:
    df = df[['deprel','diffs']][df.deprel.isin(rels)]
else:
    df = df[['deprel', 'diffs']]
hist = df.hist(by = 'deprel', bins = 30, figsize = (8,8))
st.pyplot(plt.gcf())