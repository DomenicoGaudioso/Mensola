import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import src_core as sc

st.set_page_config(page_title="Analisi Pila Ponte", layout="wide")
st.title("Pila da Ponte: Modello Semplificato 2D")

# --- SIDEBAR ---
st.sidebar.header("1. Geometria e Materiale")
H = st.sidebar.number_input("Altezza Pila, H (m)", value=10.0, step=1.0)
E_MPa = st.sidebar.number_input("Modulo Elastico, E (MPa)", value=30000.0, step=1000.0)
E = E_MPa * 1000
gamma = st.sidebar.number_input("Peso Specifico γ (kN/m³)", value=25.0, step=1.0)

tipo_sezione = st.sidebar.selectbox("Profilo della sezione", ("1 - Sezione Costante", "2 - A tratti", "3 - Sezione Variabile"))
if tipo_sezione == "1 - Sezione Costante":
    A = st.sidebar.number_input("Area, A (m²)", value=4.0, step=0.1)
    I = st.sidebar.number_input("Inerzia, I (m⁴)", value=1.33, step=0.1)
    section_data = {'type': 'costante', 'A': A, 'I': I}
elif tipo_sezione == "2 - A tratti":
    df_edited = st.sidebar.data_editor(pd.DataFrame({"z_end": [H/2, H], "A": [6.0, 3.0], "I": [2.5, 0.8]}), num_rows="dynamic", hide_index=True)
    section_data = {'type': 'tratti', 'segments': sorted(df_edited.to_dict('records'), key=lambda x: x['z_end'])}
elif tipo_sezione == "3 - Sezione Variabile":
    section_data = {'type': 'variabile', 
                    'A_base': st.sidebar.number_input("Area Base", value=6.0, step=0.1), 'I_base': st.sidebar.number_input("Inerzia Base", value=2.5, step=0.1), 
                    'A_top': st.sidebar.number_input("Area Testa", value=3.0, step=0.1), 'I_top': st.sidebar.number_input("Inerzia Testa", value=0.8, step=0.1)}

st.sidebar.header("2. Pesi e Input Sismici")
W_kN = st.sidebar.number_input("Peso in testa (Impalcato), W (kN)", value=5000.0, step=500.0)
ag_g = st.sidebar.number_input("Accelerazione al suolo (ag/g)", value=0.15, step=0.01, format="%.2f")

num_modi = st.sidebar.number_input("Numero max di Modi da calcolare (SRSS)", min_value=1, max_value=15, value=3, step=1)

st.sidebar.markdown("---")
spettro_file = st.sidebar.file_uploader("Carica Spettro (.txt: T, Se[g])", type=['txt', 'csv'])
acc_files = st.sidebar.file_uploader("Carica Accelerogrammi (.txt)", accept_multiple_files=True)
dt = st.sidebar.number_input("Passo dt accelerogrammi (s)", value=0.01, step=0.005, format="%.3f")

N_ELEM = 30 

# --- FUNZIONI GRAFICHE ---
def plot_schema_petrangeli(H, W_kN):
    fig = go.Figure()
    M_ton = W_kN / 9.81
    offset_quota, ampiezza_base = H * 0.2, H * 0.3
    marker_size = max(25, 25 + 15 * np.log10(max(1, M_ton / 10)))

    fig.add_trace(go.Scatter(x=[-ampiezza_base, ampiezza_base], y=[0, 0], mode='lines', line=dict(color='black', width=3), hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=[0, 0], y=[0, H], mode='lines', line=dict(color='black', width=1.5), hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=[0], y=[H], mode='markers+text', 
                             marker=dict(size=marker_size, color='#333333', symbol='circle', line=dict(color='black', width=2)),
                             text=["<b>me</b>"], textposition="top center", textfont=dict(size=20, color='black'), hoverinfo='skip'))
    
    fig.add_trace(go.Scatter(x=[offset_quota, offset_quota], y=[0, H], mode='lines', line=dict(color='black', width=1.2), hoverinfo='skip'))
    fig.add_annotation(x=offset_quota, y=H, ax=offset_quota, ay=H*0.8, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2)
    fig.add_annotation(x=offset_quota, y=0, ax=offset_quota, ay=H*0.2, xref="x", yref="y", axref="x", ayref="y", showarrow=True, arrowhead=2)
    fig.add_annotation(x=offset_quota*1.2, y=H/2, text=f"<b>He = {H} m</b>", showarrow=False, font=dict(size=18, color='black'), xanchor='left')

    fig.update_layout(xaxis=dict(visible=False, range=[-H*0.5, H*0.6]), yaxis=dict(visible=False, range=[-H*0.1, H*1.25]), 
                      plot_bgcolor='white', width=350, height=600, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    return fig

col_img, col_grafici = st.columns([1, 1.5])

with col_img:
    st.markdown("### Schema Grafico (Dinamico)")
    st.plotly_chart(plot_schema_petrangeli(H, W_kN), use_container_width=True)

with col_grafici:
    st.markdown("### Segnali Sismici in Input")
    
    if spettro_file is not None:
        spettro_file.seek(0)
        spettro_data = np.loadtxt(spettro_file)
        fig_sp = go.Figure()
        fig_sp.add_trace(go.Scatter(x=spettro_data[:, 0], y=spettro_data[:, 1], mode='lines', line=dict(color='black', width=2)))
        fig_sp.update_layout(title="Spettro di Risposta", xaxis_title="Periodo T (s)", yaxis_title="Accelerazione Se (g)", 
                             height=280, margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor='white')
        fig_sp.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig_sp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        st.plotly_chart(fig_sp, use_container_width=True)
        spettro_file.seek(0) 
    else:
        st.info("Carica un file di Spettro dalla sidebar per visualizzarlo qui.")
        
    if len(acc_files) > 0:
        fig_acc = go.Figure()
        for file in acc_files:
            file.seek(0)
            acc_data = np.loadtxt(file)
            t_array = np.arange(len(acc_data)) * dt
            fig_acc.add_trace(go.Scatter(x=t_array, y=acc_data, mode='lines', opacity=0.6, name=file.name))
            file.seek(0) 
            
        fig_acc.update_layout(title=f"Accelerogrammi ({len(acc_files)} file)", xaxis_title="Tempo (s)", yaxis_title="Accelerazione (m/s²)", 
                              height=280, margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor='white', showlegend=False)
        fig_acc.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig_acc.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        st.plotly_chart(fig_acc, use_container_width=True)
    else:
        st.info("Carica i file Accelerogrammi dalla sidebar per visualizzarli qui.")

st.markdown("---")

def plot_envelopes(z, env_max, env_min=None, title_suffix=""):
    fig = make_subplots(rows=1, cols=6, subplot_titles=(
        f"Normale {title_suffix}<br>(kN)", f"Taglio {title_suffix}<br>(kN)", f"Momento {title_suffix}<br>(kNm)",
        f"Spostamento {title_suffix}<br>(mm)", f"Rotazione {title_suffix}<br>(rad)", f"Acc. {title_suffix}<br>(m/s²)"
    ))
    
    colors = ['green', 'blue', 'red', 'purple', 'orange', 'brown']
    keys = ['N', 'V', 'M', 'Disp', 'Rot', 'Acc']
    
    for i, (key, color) in enumerate(zip(keys, colors)):
        fig.add_trace(go.Scatter(x=env_max[key], y=z, mode='lines', line=dict(color=color, width=2), name=f'Max {key}'), row=1, col=i+1)
        if env_min is not None:
            fig.add_trace(go.Scatter(x=env_min[key], y=z, mode='lines', line=dict(color=color, width=2), 
                                     fill='tonextx', fillcolor=f'rgba({",".join(str(c) for c in tuple(int(color.lstrip("#")[j:j+2], 16) if color.startswith("#") else (128,128,128)))}, 0.2)', name=f'Min {key}'), row=1, col=i+1)

    fig.update_yaxes(title_text="Altezza Z (m)", row=1, col=1)
    fig.update_xaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black')
    fig.update_layout(height=450, showlegend=False, plot_bgcolor='rgba(250, 250, 250, 0.8)', margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)

def plot_time_series(all_ts, filenames, dt):
    fig = make_subplots(rows=2, cols=3, subplot_titles=(
        "Spostamento Top (mm)", "Rotazione Top (rad)", "Accelerazione Top (m/s²)",
        "Sforzo Normale Base (kN)", "Taglio Base (kN)", "Momento Base (kNm)"
    ))
    
    keys = ['Disp_Top', 'Rot_Top', 'Acc_Top', 'N_Base', 'V_Base', 'M_Base']
    positions = [(1,1), (1,2), (1,3), (2,1), (2,2), (2,3)]
    
    for idx_file, ts_data in enumerate(all_ts):
        cur_time_array = np.arange(0, len(ts_data['Disp_Top']) * dt, dt)
        for idx_plot, (key, (r, c)) in enumerate(zip(keys, positions)):
            fig.add_trace(go.Scatter(x=cur_time_array, y=ts_data[key], mode='lines', opacity=0.7, 
                                     name=filenames[idx_file] if idx_plot == 0 else "", showlegend=(idx_plot == 0)), row=r, col=c)

    fig.update_xaxes(title_text="Tempo (s)", row=2)
    fig.update_layout(height=700, hovermode='x unified', plot_bgcolor='white', legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

def build_animation(z_nodes, profile_history, acc_data, dt, H):
    skip = max(1, int(0.05 / dt))
    max_disp_m = np.max(np.abs(profile_history)) / 1000.0
    scale_factor = (H * 0.15) / max_disp_m if max_disp_m > 0 else 1.0
    
    fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3], vertical_spacing=0.1,
                        subplot_titles=(f"Oscillazione Pila (Spostamenti amplificati x{scale_factor:.0f})", "Accelerogramma al Suolo"))
    
    t_array = np.arange(len(acc_data)) * dt
    
    fig.add_trace(go.Scatter(x=profile_history[0]/1000*scale_factor, y=z_nodes, mode='lines', line=dict(color='black', width=5), name='Pila'), row=1, col=1)
    fig.add_trace(go.Scatter(x=[profile_history[0][-1]/1000*scale_factor], y=[H], mode='markers', marker=dict(size=25, color='#1f77b4', line=dict(color='black', width=2)), name='Massa'), row=1, col=1)
    fig.add_trace(go.Scatter(x=t_array, y=acc_data, mode='lines', line=dict(color='lightgray', width=1.5), name='Sisma'), row=2, col=1)
    fig.add_trace(go.Scatter(x=[t_array[0]], y=[acc_data[0]], mode='markers', marker=dict(color='red', size=12), name='Istante T'), row=2, col=1)

    frames = []
    for i in range(0, len(acc_data), skip):
        frames.append(go.Frame(
            data=[
                go.Scatter(x=profile_history[i]/1000*scale_factor, y=z_nodes), 
                go.Scatter(x=[profile_history[i][-1]/1000*scale_factor], y=[H]), 
                go.Scatter(x=[t_array[i]], y=[acc_data[i]]) 
            ],
            traces=[0, 1, 3],
            name=f'frame_{i}'
        ))
    
    fig.frames = frames

    fig.update_layout(
        height=800, plot_bgcolor='white', showlegend=False,
        updatemenus=[dict(type="buttons", showactive=False, x=0.1, y=1.1, xanchor="right", yanchor="top",
                          buttons=[dict(label="▶️ Riproduci", method="animate", args=[None, {"frame": {"duration": 50, "redraw": False}, "fromcurrent": True, "transition": {"duration": 0}}]),
                                   dict(label="⏸️ Pausa", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}])])]
    )
    
    fig.update_xaxes(range=[-H*0.3, H*0.3], row=1, col=1)
    fig.update_yaxes(range=[0, H*1.1], row=1, col=1)
    fig.update_xaxes(title_text="Tempo (s)", range=[0, t_array[-1]], row=2, col=1)
    
    return fig

# --- TABELLE ANALISI ---
tab1, tab2, tab3 = st.tabs(["1. Analisi Statica Lineare Equivalente", "2. Dinamica Lineare (Spettro)", "3. Time-History"])

with tab1:
    st.subheader("Analisi Statica Equivalente NTC")
    st.markdown("In accordo alla normativa, la forza orizzontale in testa viene calcolata leggendo l'accelerazione spettrale $S_e(T_1)$ dallo spettro di risposta caricato, garantendo il pieno confronto col metodo dinamico.")
    
    if st.button("Esegui Statica"):
        sc.build_model(H, E, W_kN, gamma, section_data, n_ele=N_ELEM)
        T1 = sc.run_modal_analysis()
        
        # FIX FONDAMENTALE SULLA FORZA STATICA (Equivalenza tra Statica e Modale)
        if spettro_file is not None:
            spettro_file.seek(0)
            spettro_data = np.loadtxt(spettro_file)
            Se_T1 = np.interp(T1, spettro_data[:, 0], spettro_data[:, 1])
            F_stat = W_kN * Se_T1  # Forza calcolata tramite spettro amplificato
            msg_risultato = f"**T1:** {T1:.3f} s | **Se(T1) applicata:** {Se_T1:.3f} g | **Taglio Base:** {F_stat:.1f} kN"
        else:
            F_stat = W_kN * ag_g # Fallback semplice se non c'è lo spettro
            msg_risultato = f"**T1:** {T1:.3f} s | **ag applicata:** {ag_g:.3f} g | **Taglio Base:** {F_stat:.1f} kN"
            
        z, N, V, M, Disp, Rot, Acc = sc.run_static_analysis(F_stat, H, n_ele=N_ELEM)
        
        env_stat = {'N': N, 'V': V, 'M': M, 'Disp': Disp, 'Rot': Rot, 'Acc': Acc}
        st.success(msg_risultato)
        plot_envelopes(z, env_stat, title_suffix="Statico")

with tab2:
    st.subheader("Analisi Modale Equivalente (Comando Nativo OpenSees)")
    st.markdown(f"*Nota: Vengono calcolati i primi **{num_modi} modi di vibrare** e combinati con regola SRSS.*")
    if st.button("Esegui Dinamica Lineare"):
        if spettro_file is None:
            st.error("Carica lo spettro (.txt) per eseguire l'analisi.")
        else:
            spettro_file.seek(0)
            spettro_data = np.loadtxt(spettro_file)
            
            z, N, V, M, Disp, Rot, Acc, T_modes, mode_shapes = sc.run_response_spectrum(
                H, E, W_kN, gamma, section_data, spettro_data[:, 0], spettro_data[:, 1], num_modes_req=num_modi, n_ele=N_ELEM)
            
            env_mod = {'N': N, 'V': V, 'M': M, 'Disp': Disp, 'Rot': Rot, 'Acc': Acc}
            
            if len(T_modes) > 0:
                T1_val = list(T_modes.values())[0]
                st.success(f"Estrazione completata. Mostrati solo i modi con partecipazione orizzontale rilevante. **T1 Principale:** {T1_val:.3f} s | **Taglio Base (COMB SRSS):** {V[0]:.1f} kN")
                
                col_spettro, col_modi = st.columns(2)
                
                with col_spettro:
                    fig_spettro = go.Figure()
                    fig_spettro.add_trace(go.Scatter(x=spettro_data[:, 0], y=spettro_data[:, 1], mode='lines', name='Spettro NTC', line=dict(color='black')))
                    
                    colors_modi = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'brown', 'pink']
                    for m_idx, (nome_modo, T_val) in enumerate(T_modes.items()):
                        Se_val = np.interp(T_val, spettro_data[:, 0], spettro_data[:, 1])
                        fig_spettro.add_trace(go.Scatter(x=[T_val], y=[Se_val], mode='markers', marker=dict(size=10, color=colors_modi[m_idx%10]), 
                                                         name=f'{nome_modo}: T={T_val:.3f}s'))
                    
                    fig_spettro.update_layout(title="Punti di Lavoro Modali sullo Spettro", xaxis_title="Periodo T (s)", yaxis_title="Se (g)", 
                                              height=350, plot_bgcolor='white', legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99))
                    fig_spettro.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                    fig_spettro.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                    st.plotly_chart(fig_spettro, use_container_width=True)

                with col_modi:
                    fig_modi = go.Figure()
                    for m_idx, (nome_modo, phi) in enumerate(mode_shapes.items()):
                        fig_modi.add_trace(go.Scatter(x=phi, y=z, mode='lines+markers', name=nome_modo, line=dict(width=2, color=colors_modi[m_idx%10])))
                        
                    fig_modi.add_trace(go.Scatter(x=[0, 0], y=[0, H], mode='lines', line=dict(color='gray', width=1, dash='dash'), showlegend=False))
                    fig_modi.update_layout(title="Forme Modali (Proporzioni Fisiche Reali)", xaxis_title="Spostamento Relativo Orizzontale", yaxis_title="Altezza Z (m)", 
                                           height=350, plot_bgcolor='white')
                    fig_modi.update_xaxes(zeroline=True, zerolinewidth=1, zerolinecolor='black', showgrid=True, gridcolor='LightGray')
                    fig_modi.update_yaxes(showgrid=True, gridcolor='LightGray')
                    st.plotly_chart(fig_modi, use_container_width=True)
            else:
                st.warning("Nessun modo estratto valido o periodi fuori range.")

            st.markdown("#### Inviluppi SRSS Combinati")
            plot_envelopes(z, env_mod, title_suffix="Modale RSA")

with tab3:
    st.subheader("Analisi Dinamica (Time-History)")
    if st.button("Esegui Time-History"):
        if len(acc_files) == 0:
            st.warning("Carica i file txt degli accelerogrammi.")
        else:
            list_env_max, list_env_min, list_ts = [], [], []
            file_names = []
            progress_bar = st.progress(0)
            
            for idx, file in enumerate(acc_files):
                file.seek(0) 
                acc_data = np.loadtxt(file)
                file_names.append(file.name)
                
                z, env_max, env_min, ts = sc.run_time_history(H, E, W_kN, gamma, section_data, acc_data, dt, n_ele=N_ELEM)
                
                if idx == 0:
                    anim_profile_history = ts['Profile']
                    anim_acc_data = acc_data
                
                list_env_max.append(env_max)
                list_env_min.append(env_min)
                list_ts.append(ts)
                progress_bar.progress((idx + 1) / len(acc_files))
            
            st.markdown("#### Storie Temporali (Punti Critici: Top e Base)")
            plot_time_series(list_ts, file_names, dt)
            
            with st.expander("🎬 Guarda il Video dell'Oscillazione (Primo Accelerogramma)", expanded=False):
                st.markdown("Premi **Riproduci** per avviare l'animazione sincrona tra la deformazione della pila e l'input sismico al suolo.")
                fig_anim = build_animation(z, anim_profile_history, anim_acc_data, dt, H)
                st.plotly_chart(fig_anim, use_container_width=True)

            if len(acc_files) >= 7:
                mean_env_max = {k: np.mean([e[k] for e in list_env_max], axis=0) for k in list_env_max[0].keys()}
                mean_env_min = {k: np.mean([e[k] for e in list_env_min], axis=0) for k in list_env_min[0].keys()}
                
                st.markdown("#### Inviluppi Medi NTC lungo l'altezza")
                plot_envelopes(z, mean_env_max, mean_env_min, "NTC")
            else:
                st.warning(f"Caricati solo {len(acc_files)}/7 segnali. Inviluppi medi NTC non mostrati.")