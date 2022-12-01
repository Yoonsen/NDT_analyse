import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


@st.cache()
def get_rels():
    return list(set(list(ndt.deprel.values)))

@st.cache()
def get_pos():
    return list(set(list(ndt.pos.values)))

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
pos = get_pos()

def counts(header="POS", column = 'pos'):
    nob = pd.DataFrame(ndt[ndt.language_code=="nb-NO"].groupby([column]).count()['language_code']).reset_index().set_index(column)
    nno = pd.DataFrame(ndt[ndt.language_code=="nn-NO"].groupby([column]).count()['language_code']).reset_index().set_index(column)
    combo = pd.concat([nob, nno], axis = 1).fillna(0)
    combo.columns = ['bokmål', 'nynorsk']
    return combo.style.format(precision=0)


pos = counts("POS", "pos")
dep = counts("Dependensrelasjoner", 'deprel')

st.markdown("#### Statistikk over relasjoner og kategorier")

st.write("##### POS")
col1, col2 = st.columns([1,2])
with col1:
    st.write(pos)
with col2:
    st.bar_chart(pos)


st.write("##### Dependensrelasjoner")
colA, colB = st.columns([1,2])
with colA:
    st.write(dep)
with colB:
    st.bar_chart(dep)