"""
Módulo para controlar o zoom das páginas Streamlit
Permite definir zoom personalizado com fallbacks para diferentes navegadores
"""

import streamlit as st

def set_page_zoom(zoom_percentage=80, enable_user_control=False, persistent=True):
    """
    Define o zoom da página usando JavaScript e CSS.
    
    Args:
        zoom_percentage (int): Porcentagem do zoom (padrão: 80%)
        enable_user_control (bool): Se True, adiciona controle manual de zoom
        persistent (bool): Se True, salva a preferência no localStorage
    
    Returns:
        None
    """
    zoom_decimal = zoom_percentage / 100
    
    # JavaScript simplificado e funcional
    zoom_js = f"""
    <script>
    // Prevenir múltiplas execuções
    if (typeof window.zoomApplied === 'undefined') {{
        window.zoomApplied = true;
        
        function applyZoom(zoomPercent = {zoom_percentage}) {{
            const zoomDecimal = zoomPercent / 100;
            
            // Aguardar DOM estar pronto
            function waitForApp() {{
                const app = document.querySelector('.stApp') || document.querySelector('[data-testid="stApp"]') || document.body;
                
                if (app) {{
                    // Aplicar zoom usando transform
                    app.style.transform = `scale(${{zoomDecimal}})`;
                    app.style.transformOrigin = 'top left';
                    app.style.width = `${{Math.round(100/zoomDecimal)}}%`;
                    app.style.height = `${{Math.round(100/zoomDecimal)}}%`;
                    app.style.overflow = 'visible';
                    
                    // Salvar no localStorage se habilitado
                    {f"localStorage.setItem('streamlit_page_zoom', zoomPercent);" if persistent else ""}
                    
                    console.log(`✅ Zoom aplicado: ${{zoomPercent}}%`);
                    
                    // Trigger evento customizado
                    window.dispatchEvent(new CustomEvent('zoomChanged', {{ 
                        detail: {{ zoom: zoomPercent }} 
                    }}));
                }} else {{
                    setTimeout(waitForApp, 100);
                }}
            }}
            
            waitForApp();
        }}
        
        // Função para carregar zoom salvo
        function loadSavedZoom() {{
            {f"""
            const saved = localStorage.getItem('streamlit_page_zoom');
            if (saved && !isNaN(saved)) {{
                const zoom = parseInt(saved);
                return (zoom >= 50 && zoom <= 200) ? zoom : {zoom_percentage};
            }}
            """ if persistent else ""}
            return {zoom_percentage};
        }}
        
        // Aplicar zoom inicial
        const initialZoom = loadSavedZoom();
        applyZoom(initialZoom);
        
        // Reaplicar quando DOM mudar (para navegação entre páginas)
        let reapplyTimeout;
        const observer = new MutationObserver(() => {{
            clearTimeout(reapplyTimeout);
            reapplyTimeout = setTimeout(() => {{
                const currentZoom = loadSavedZoom();
                applyZoom(currentZoom);
            }}, 300);
        }});
        
        observer.observe(document.body, {{ childList: true, subtree: true }});
      }}
    </script>
    """
      # CSS para suporte adicional ao zoom - VERSÃO OTIMIZADA
    zoom_css = f"""
    <style>
    /* Variáveis CSS para zoom */
    :root {{
        --page-zoom: {zoom_decimal};
        --page-zoom-percent: {zoom_percentage}%;
        --page-zoom-inverse: {1/zoom_decimal:.4f};
    }}
    
    /* Remover conflitos de CSS - aplicar zoom apenas via JavaScript */
    .stApp {{
        /* transform aplicado via JavaScript */
        overflow-x: auto;
        transition: transform 0.3s ease;
    }}
    
    /* Ajustar container principal - valores fixos para evitar conflitos */
    .main .block-container {{
        max-width: 1200px;
        padding-top: 1rem;
    }}
    
    /* Z-index otimizado para Streamlit */
    #zoom-control {{
        z-index: 999999 !important;
    }}
    
    /* Responsive: desativar zoom em telas pequenas */
    @media screen and (max-width: 768px) {{
        .stApp {{
            transform: none !important;
            width: 100% !important;
            height: auto !important;
        }}
    }}
    
    /* Melhorar scrollbars quando zoom está ativo */
    body:has(.stApp[style*="scale"]) {{
        overflow-x: auto;
        overflow-y: auto;
    }}
    
    /* Manter proporções de elementos importantes */
    @media screen and (min-width: 769px) {{
        .metric-card {{
            min-height: 100px;
        }}
        
        .section-header h4 {{
            font-size: 1.2rem;
        }}
    }}
    </style>
    """
    
    # Combinar JavaScript e CSS
    combined_code = zoom_js + zoom_css
    
    # Adicionar controle de usuário se habilitado
    if enable_user_control:
        combined_code += get_zoom_control_ui()
    
    st.markdown(combined_code, unsafe_allow_html=True)

def get_zoom_control_ui():
    """
    Retorna HTML/JS para controle manual de zoom pelo usuário - VERSÃO OTIMIZADA.
    
    Returns:
        str: HTML com controle de zoom
    """
    return """
    <div id="zoom-control" style="position: fixed; top: 10px; right: 10px; z-index: 999999; 
                background: rgba(255,255,255,0.98); padding: 12px; border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.25); font-size: 12px; border: 1px solid #ddd;
                min-width: 160px; backdrop-filter: blur(5px);">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <label style="font-weight: bold; color: #333;">🔍 Zoom</label>
            <button onclick="toggleZoomControl()" style="background: none; border: none; font-size: 14px; cursor: pointer; color: #999;">✕</button>
        </div>
        <div style="text-align: center; margin-bottom: 8px;">
            <span id="zoom-value" style="font-weight: bold; color: #007bff;">80%</span>
        </div>
        <input type="range" id="zoom-slider" min="50" max="150" value="80" step="5"
               style="width: 100%; margin-bottom: 8px; accent-color: #007bff;">
        <div style="display: flex; gap: 5px;">
            <button onclick="resetZoom()" style="flex: 1; padding: 4px; font-size: 10px; border: 1px solid #ddd; background: #f8f9fa; cursor: pointer; border-radius: 4px; transition: all 0.2s;">Reset</button>
            <button onclick="saveZoom()" style="flex: 1; padding: 4px; font-size: 10px; border: 1px solid #007bff; background: #007bff; color: white; cursor: pointer; border-radius: 4px; transition: all 0.2s;">Salvar</button>
        </div>
    </div>
    
    <script>
    // Evitar múltiplas inicializações
    if (typeof window.zoomControlInitialized === 'undefined') {{
        window.zoomControlInitialized = true;
        
        // Configurar controle de zoom
        function initZoomControl() {{
            const zoomSlider = document.getElementById('zoom-slider');
            const zoomValue = document.getElementById('zoom-value');
            
            if (!zoomSlider || !zoomValue) {{
                console.warn('⚠️ Zoom control elements not found');
                return;
            }}
            
            // Carregar zoom salvo e sincronizar UI
            const savedZoom = localStorage.getItem('streamlit_page_zoom') || '80';
            const zoomInt = parseInt(savedZoom);
            
            // Validar valor
            if (zoomInt >= 50 && zoomInt <= 150) {{
                zoomSlider.value = zoomInt;
                zoomValue.textContent = zoomInt + '%';
            }} else {{
                zoomSlider.value = 80;
                zoomValue.textContent = '80%';
            }}
            
            // Event listener para mudanças no slider
            zoomSlider.addEventListener('input', function() {{
                const zoom = parseInt(this.value);
                zoomValue.textContent = zoom + '%';
                
                // Aplicar zoom usando a função global
                if (window.setPageZoom) {{
                    window.setPageZoom(zoom);
                }} else {{
                    console.error('❌ setPageZoom function not available');
                }}
            }});
            
            console.log('✅ Zoom control initialized');
        }}
        
        function resetZoom() {{
            const zoomSlider = document.getElementById('zoom-slider');
            const zoomValue = document.getElementById('zoom-value');
            
            if (zoomSlider && zoomValue) {{
                zoomSlider.value = 80;
                zoomValue.textContent = '80%';
                if (window.setPageZoom) {{
                    window.setPageZoom(80);
                }}
                
                // Feedback visual
                const resetBtn = event.target;
                const originalText = resetBtn.textContent;
                resetBtn.textContent = '✓';
                resetBtn.style.background = '#28a745';
                resetBtn.style.borderColor = '#28a745';
                setTimeout(() => {{
                    resetBtn.textContent = originalText;
                    resetBtn.style.background = '#f8f9fa';
                    resetBtn.style.borderColor = '#ddd';
                }}, 800);
            }}
        }}
        
        function saveZoom() {{
            const zoomSlider = document.getElementById('zoom-slider');
            if (zoomSlider) {{
                const zoomValue = parseInt(zoomSlider.value);
                localStorage.setItem('streamlit_page_zoom', zoomValue);
                
                // Feedback visual
                const saveBtn = event.target;
                const originalText = saveBtn.textContent;
                saveBtn.textContent = '✓ Salvo';
                saveBtn.style.background = '#28a745';
                saveBtn.style.borderColor = '#28a745';
                setTimeout(() => {{
                    saveBtn.textContent = originalText;
                    saveBtn.style.background = '#007bff';
                    saveBtn.style.borderColor = '#007bff';
                }}, 1000);
                
                console.log(`💾 Zoom ${zoomValue}% saved to localStorage`);
            }}
        }}
        
        // Inicializar quando DOM estiver pronto
        function attemptInit() {{
            if (document.getElementById('zoom-control')) {{
                initZoomControl();
            }} else {{
                setTimeout(attemptInit, 100);
            }}
        }}
        
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', attemptInit);
        }} else {{
            attemptInit();
        }}
        
        // Disponibilizar funções globalmente
        window.resetZoom = resetZoom;
        window.saveZoom = saveZoom;
        window.initZoomControl = initZoomControl;
        
        // Tecla de atalho para mostrar/ocultar controle (Ctrl+Shift+Z)
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey && e.shiftKey && e.key === 'Z') {{
                e.preventDefault();
                toggleZoomControl();
            }}
        }});
    }}
    </script>
    """

def create_zoom_toggle_button():
    """
    Cria um botão otimizado para mostrar/ocultar o controle de zoom.
    
    Returns:
        None
    """
    toggle_button = """
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 999998;">
        <button onclick="toggleZoomControl()" 
                style="background: linear-gradient(135deg, #007bff, #0056b3); 
                       color: white; border: none; padding: 12px; 
                       border-radius: 50%; width: 55px; height: 55px; cursor: pointer;
                       box-shadow: 0 4px 15px rgba(0,123,255,0.3); font-size: 18px;
                       transition: all 0.3s ease; backdrop-filter: blur(5px);"
                title="Controle de Zoom (Ctrl+Shift+Z)"
                onmouseover="this.style.transform='scale(1.1)'; this.style.boxShadow='0 6px 20px rgba(0,123,255,0.4)';"
                onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 15px rgba(0,123,255,0.3)';">
            🔍
        </button>
    </div>
    
    <script>
    // Garantir que toggleZoomControl está sempre disponível
    if (typeof window.toggleZoomControl === 'undefined') {
        window.toggleZoomControl = function() {
            const control = document.getElementById('zoom-control');
            if (control) {
                const isVisible = control.style.display !== 'none';
                control.style.display = isVisible ? 'none' : 'block';
                
                // Feedback visual no botão
                const button = document.querySelector('[title*="Controle de Zoom"]');
                if (button) {
                    button.textContent = isVisible ? '🔍' : '✕';
                    setTimeout(() => {
                        if (!isVisible) button.textContent = '🔍';
                    }, 3000);
                }
            } else {
                console.warn('⚠️ Zoom control panel not found. Make sure to enable user control.');
            }
        };
    }
    </script>
    """
    
    st.markdown(toggle_button, unsafe_allow_html=True)

def get_current_zoom():
    """
    Retorna o zoom atual salvo no localStorage (para uso em callbacks).
    
    Returns:
        str: JavaScript que retorna o zoom atual
    """
    return """
    <script>
    function getCurrentZoom() {
        return localStorage.getItem('streamlit_page_zoom') || '80';
    }
    
    // Disponibilizar globalmente
    window.getCurrentZoom = getCurrentZoom;
    </script>
    """

# Função de conveniência para aplicar zoom padrão
def apply_default_zoom():
    """Aplica zoom padrão de 80% sem controles adicionais."""
    set_page_zoom(80, enable_user_control=False, persistent=True)

def apply_zoom_with_control():
    """Aplica zoom de 80% com controle de usuário."""
    set_page_zoom(80, enable_user_control=True, persistent=True)
    create_zoom_toggle_button()
