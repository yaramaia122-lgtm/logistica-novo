import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import requests

# Configuração formal e ocultação forçada da barra lateral antes do login
st.set_page_config(page_title="AURA APOENA LOGISTICS", layout="wide", initial_sidebar_state="collapsed")

# CSS Modernizado para a Interface de Login
st.markdown("""
<style>
    /* Fundo da aplicação */
    .stApp { 
        background: linear-gradient(135deg, #001F42 0%, #002D5E 100%) !important; 
    }
    
    /* Centralização e container do formulário */
    div[data-testid="stForm"] { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 30px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Estilização dos Labels (Títulos dos campos) */
    label { 
        color: #FFFFFF !important; 
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px;
        margin-bottom: 5px !important;
    }
    
    /* Inputs brancos e limpos com texto escuro */
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important; 
        color: #002D5E !important; 
        border: none !important;
        border-radius: 8px !important;
        height: 42px !important;
        font-size: 15px !important;
    }
    
    /* Botão de Acesso Principal (Destaque em Laranja Coral) */
    .stButton>button {
        background-color: #FF7F50 !important; 
        color: #FFFFFF !important;
        font-weight: 700 !important; 
        border: none !important;
        border-radius: 8px !important; 
        height: 46px !important;
        width: 100% !important;
        font-size: 16px !important;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255, 127, 80, 0.3) !important;
    }
    
    .stButton>button:hover {
        background-color: #FF6A33 !important;
        box-shadow: 0 6px 16px rgba(255, 127, 80, 0.5) !important;
        transform: translateY(-1px);
    }
    
    /* Botão secundário de cache */
    div.element-container
