import openseespy.opensees as ops
import numpy as np

def build_model(H, E, W_kN, gamma, section_data, n_ele=30):
    ops.wipe()
    ops.model('basic', '-ndm', 2, '-ndf', 3)
    dz = H / n_ele
    for i in range(n_ele + 1):
        ops.node(i + 1, 0.0, i * dz)
        
    ops.fix(1, 1, 1, 1)
    
    ops.mass(n_ele + 1, W_kN / 9.81, 1e-9, 1e-9) 
    ops.geomTransf('Linear', 1)
    
    areas = []
    
    for i in range(n_ele):
        node_i = i + 1
        node_j = i + 2
        z_mid = (i + 0.5) * dz
        
        if section_data['type'] == 'costante':
            A_el, I_el = section_data['A'], section_data['I']
        elif section_data['type'] == 'tratti':
            A_el, I_el = 0.0, 0.0
            for row in section_data['segments']:
                if z_mid <= row['z_end']:
                    A_el, I_el = row['A'], row['I']
                    break
        elif section_data['type'] == 'variabile':
            A_el = section_data['A_base'] + (section_data['A_top'] - section_data['A_base']) * (z_mid / H)
            I_el = section_data['I_base'] + (section_data['I_top'] - section_data['I_base']) * (z_mid / H)
            
        areas.append(A_el) 
        
        mass_dens = A_el * (gamma / 9.81) 
        ops.element('elasticBeamColumn', i + 1, node_i, node_j, A_el, E, I_el, 1, '-mass', mass_dens)
        
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    
    ops.load(n_ele + 1, 0.0, -W_kN, 0.0)
    for i in range(n_ele):
        ops.eleLoad('-ele', i + 1, '-type', '-beamUniform', 0.0, -areas[i] * gamma)
            
    ops.system('BandSPD')
    ops.numberer('RCM')
    ops.constraints('Plain')
    ops.integrator('LoadControl', 1.0)
    ops.algorithm('Linear')
    ops.analysis('Static')
    ops.analyze(1)
    
    ops.loadConst('-time', 0.0)
    ops.wipeAnalysis() 
    
    return n_ele

def run_modal_analysis():
    lambdas = ops.eigen('-fullGenLapack', 1)
    if not lambdas:
        return 1.0 
    omega = np.sqrt(lambdas[0])
    return 2 * np.pi / omega

def run_static_analysis(F_orizzontale, H, n_ele=30):
    ops.wipeAnalysis() 
    
    ops.timeSeries('Linear', 2)
    ops.pattern('Plain', 2, 2)
    ops.load(n_ele + 1, F_orizzontale, 0.0, 0.0) 
    
    ops.system('BandSPD')
    ops.numberer('RCM')
    ops.constraints('Plain')
    ops.integrator('LoadControl', 1.0)
    ops.algorithm('Linear')
    ops.analysis('Static')
    ops.analyze(1)
    
    z_nodes = np.linspace(0, H, n_ele + 1)
    N, V, M, Disp, Rot, Acc = np.zeros(n_ele+1), np.zeros(n_ele+1), np.zeros(n_ele+1), np.zeros(n_ele+1), np.zeros(n_ele+1), np.zeros(n_ele+1)
    
    for i in range(n_ele + 1):
        Disp[i] = ops.nodeDisp(i + 1, 1) * 1000  
        Rot[i] = ops.nodeDisp(i + 1, 3)
        Acc[i] = 0.0 
    
    # Nodo I dell'elemento alla base: segni normali
    forces_base = ops.eleForce(1)
    N[0], V[0], M[0] = forces_base[0], forces_base[1], forces_base[2]
    
    # Nodi J di tutti gli elementi: SEGNI INVERTITI per sollecitazione interna corretta
    for i in range(n_ele):
        forces = ops.eleForce(i + 1) 
        N[i+1], V[i+1], M[i+1] = -forces[3], -forces[4], -forces[5]
            
    return z_nodes, N, V, M, Disp, Rot, Acc

def run_response_spectrum(H, E, W_kN, gamma, section_data, T_spettro, Se_spettro, num_modes_req=3, n_ele=30):
    build_model(H, E, W_kN, gamma, section_data, n_ele)
    ops.wipeAnalysis() 
    
    num_modes = min(num_modes_req, n_ele * 3)
    lambdas = ops.eigen('-fullGenLapack', num_modes)
    ops.modalProperties('-unorm')
    
    num_modes_extracted = len(lambdas) if lambdas else 0
    
    z_nodes = np.linspace(0, H, n_ele + 1)
    N_srss, V_srss, M_srss = np.zeros(n_ele+1), np.zeros(n_ele+1), np.zeros(n_ele+1)
    Disp_srss, Rot_srss, Acc_srss = np.zeros(n_ele+1), np.zeros(n_ele+1), np.zeros(n_ele+1)
    
    T_modes = {}
    mode_shapes = {}
    
    if num_modes_extracted == 0:
        return z_nodes, N_srss, V_srss, M_srss, Disp_srss, Rot_srss, Acc_srss, T_modes, mode_shapes
    
    for m in range(1, num_modes_extracted + 1):
        omega = np.sqrt(lambdas[m-1])
        T_m = 2 * np.pi / omega
        
        phi_x = np.array([ops.nodeEigenvector(i + 1, m, 1) for i in range(n_ele + 1)])
        phi_y = np.array([ops.nodeEigenvector(i + 1, m, 2) for i in range(n_ele + 1)])
        
        norm_factor = np.max([np.max(np.abs(phi_x)), np.max(np.abs(phi_y))])
        
        if norm_factor > 1e-12:
            phi_x_norm = phi_x / norm_factor
            
            if np.max(np.abs(phi_x_norm)) > 0.01:
                T_modes[f"Modo {m}"] = T_m
                mode_shapes[f"Modo {m}"] = phi_x_norm
    
    T_safe = np.where(T_spettro <= 0.0, 1e-6, T_spettro)
    Tn_vals = T_safe.tolist()
    Sa_vals = (Se_spettro * 9.81).tolist()
    
    for mode in range(1, num_modes_extracted + 1):
        ops.responseSpectrumAnalysis(1, '-Tn', *Tn_vals, '-Sa', *Sa_vals, '-mode', mode)
        
        cur_N, cur_V, cur_M = np.zeros(n_ele+1), np.zeros(n_ele+1), np.zeros(n_ele+1)
        cur_Disp, cur_Rot = np.zeros(n_ele+1), np.zeros(n_ele+1)
        
        for i in range(n_ele + 1):
            cur_Disp[i] = ops.nodeDisp(i + 1, 1) * 1000  
            cur_Rot[i] = ops.nodeDisp(i + 1, 3)
            
        # Nodo I (Base) normale
        forces_base = ops.eleForce(1)
        cur_N[0], cur_V[0], cur_M[0] = forces_base[0], forces_base[1], forces_base[2]
        
        # Nodo J (Testa elemento) invertito
        for i in range(n_ele):
            forces = ops.eleForce(i + 1) 
            cur_N[i+1], cur_V[i+1], cur_M[i+1] = -forces[3], -forces[4], -forces[5]
            
        N_srss += cur_N**2
        V_srss += cur_V**2
        M_srss += cur_M**2
        Disp_srss += cur_Disp**2
        Rot_srss += cur_Rot**2
        
    return z_nodes, np.sqrt(N_srss), np.sqrt(V_srss), np.sqrt(M_srss), np.sqrt(Disp_srss), np.sqrt(Rot_srss), Acc_srss, T_modes, mode_shapes

def run_time_history(H, E, W_kN, gamma, section_data, accelerogram_data, dt, n_ele=30):
    build_model(H, E, W_kN, gamma, section_data, n_ele)
    T1 = run_modal_analysis()
    
    ops.wipeAnalysis() 
    
    zeta = 0.05
    ops.rayleigh(2 * zeta * (2 * np.pi / T1), 0.0, 0.0, 0.0)
    
    ops.timeSeries('Path', 3, '-dt', dt, '-values', *accelerogram_data.tolist())
    ops.pattern('UniformExcitation', 3, 1, '-accel', 3)
    
    ops.system('BandGeneral')
    ops.numberer('Plain')
    ops.constraints('Plain')
    ops.integrator('Newmark', 0.5, 0.25)
    ops.algorithm('Newton')
    ops.analysis('Transient')
    
    n_pts = len(accelerogram_data)
    
    N_max, V_max, M_max = np.full(n_ele+1, -np.inf), np.full(n_ele+1, -np.inf), np.full(n_ele+1, -np.inf)
    N_min, V_min, M_min = np.full(n_ele+1, np.inf), np.full(n_ele+1, np.inf), np.full(n_ele+1, np.inf)
    Disp_max, Rot_max, Acc_max = np.full(n_ele+1, -np.inf), np.full(n_ele+1, -np.inf), np.full(n_ele+1, -np.inf)
    Disp_min, Rot_min, Acc_min = np.full(n_ele+1, np.inf), np.full(n_ele+1, np.inf), np.full(n_ele+1, np.inf)
    
    t_disp_top, t_rot_top, t_acc_top = [], [], []
    t_N_base, t_V_base, t_M_base = [], [], []
    t_profile = [] 
    
    for _ in range(n_pts):
        ops.analyze(1, dt)
        
        cur_N, cur_V, cur_M = np.zeros(n_ele+1), np.zeros(n_ele+1), np.zeros(n_ele+1)
        cur_Disp, cur_Rot, cur_Acc = np.zeros(n_ele+1), np.zeros(n_ele+1), np.zeros(n_ele+1)
        
        for i in range(n_ele + 1):
            cur_Disp[i] = ops.nodeDisp(i + 1, 1) * 1000 
            cur_Rot[i] = ops.nodeDisp(i + 1, 3)
            cur_Acc[i] = ops.nodeAccel(i + 1, 1)
            
        # Nodo I (Base) normale
        forces_b = ops.eleForce(1)
        cur_N[0], cur_V[0], cur_M[0] = forces_b[0], forces_b[1], forces_b[2]
        
        # Nodo J (Testa elemento) invertito
        for i in range(n_ele):
            forces = ops.eleForce(i + 1)
            cur_N[i+1], cur_V[i+1], cur_M[i+1] = -forces[3], -forces[4], -forces[5]
            
        N_max, N_min = np.maximum(N_max, cur_N), np.minimum(N_min, cur_N)
        V_max, V_min = np.maximum(V_max, cur_V), np.minimum(V_min, cur_V)
        M_max, M_min = np.maximum(M_max, cur_M), np.minimum(M_min, cur_M)
        Disp_max, Disp_min = np.maximum(Disp_max, cur_Disp), np.minimum(Disp_min, cur_Disp)
        Rot_max, Rot_min = np.maximum(Rot_max, cur_Rot), np.minimum(Rot_min, cur_Rot)
        Acc_max, Acc_min = np.maximum(Acc_max, cur_Acc), np.minimum(Acc_min, cur_Acc)
        
        t_disp_top.append(cur_Disp[-1])
        t_rot_top.append(cur_Rot[-1])
        t_acc_top.append(cur_Acc[-1])
        t_N_base.append(cur_N[0])
        t_V_base.append(cur_V[0])
        t_M_base.append(cur_M[0])
        t_profile.append(cur_Disp.copy()) 
                
    z_nodes = np.linspace(0, H, n_ele + 1)
    
    env_max = {'N': N_max, 'V': V_max, 'M': M_max, 'Disp': Disp_max, 'Rot': Rot_max, 'Acc': Acc_max}
    env_min = {'N': N_min, 'V': V_min, 'M': M_min, 'Disp': Disp_min, 'Rot': Rot_min, 'Acc': Acc_min}
    time_series = {'Disp_Top': t_disp_top, 'Rot_Top': t_rot_top, 'Acc_Top': t_acc_top, 
                   'N_Base': t_N_base, 'V_Base': t_V_base, 'M_Base': t_M_base, 'Profile': t_profile}
                   
    return z_nodes, env_max, env_min, time_series