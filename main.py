import streamlit as st
import random
import math
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
import names 

st.set_page_config(
    page_title="Cupido: Par de Pontos Mais Próximos",
    page_icon="💘",
)

# ----- Classe Pessoa -----
class Pessoa:
    def __init__(self, id, x, y):
        self.id = id
        self.nome = names.get_full_name()
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.ativo = True

    def mover(self, largura, altura):
        if not self.ativo:
            return
        self.x += self.vx
        self.y += self.vy

        # Rebater nas bordas
        if self.x <= 0 or self.x >= largura:
            self.vx *= -1
        if self.y <= 0 or self.y >= altura:
            self.vy *= -1

    def distancia(self, outra):
        return math.hypot(self.x - outra.x, self.y - outra.y)

# ----- Algoritmo do par mais próximo  -----
def encontrar_par_mais_proximo(pessoas):
    pessoas_ativas = [p for p in pessoas if p.ativo]
    if len(pessoas_ativas) < 2:
        return (None, None)
    return _par_mais_proximo(sorted(pessoas_ativas, key=lambda p: p.x))

def _forca_bruta(pessoas):
    min_dist = float('inf')
    par = (None, None)
    for i in range(len(pessoas)):
        for j in range(i + 1, len(pessoas)):
            d = pessoas[i].distancia(pessoas[j])
            if d < min_dist:
                min_dist = d
                par = (pessoas[i], pessoas[j])
    return par

def _par_mais_proximo(pessoas_ordenadas_x):
    n = len(pessoas_ordenadas_x)
    if n <= 4:
        return _forca_bruta(pessoas_ordenadas_x)
    
    mid = n // 2
    midpoint = pessoas_ordenadas_x[mid]
    
    par_esq = _par_mais_proximo(pessoas_ordenadas_x[:mid])
    par_dir = _par_mais_proximo(pessoas_ordenadas_x[mid:])
    
    dist_esq = par_esq[0].distancia(par_esq[1]) if par_esq[0] else float('inf')
    dist_dir = par_dir[0].distancia(par_dir[1]) if par_dir[0] else float('inf')
    
    if dist_esq <= dist_dir:
        melhor_par = par_esq
        min_dist = dist_esq
    else:
        melhor_par = par_dir
        min_dist = dist_dir
        
    strip = [p for p in pessoas_ordenadas_x if abs(p.x - midpoint.x) < min_dist]
    strip.sort(key=lambda p: p.y)
    
    par_strip = _strip_closest(strip, min_dist)
    
    if par_strip and par_strip[0]:
        dist_strip = par_strip[0].distancia(par_strip[1])
        if dist_strip < min_dist:
            return par_strip
            
    return melhor_par

def _strip_closest(strip, d):
    min_dist = d
    par = (None, None)
    for i in range(len(strip)):
        j = i + 1
        while j < len(strip) and (strip[j].y - strip[i].y) < min_dist:
            dist = strip[i].distancia(strip[j])
            if dist < min_dist:
                min_dist = dist
                par = (strip[i], strip[j])
            j += 1
    return par


# ----- Inicialização do estado -----
if 'pessoas' not in st.session_state:
    largura, altura = 100, 100
    st.session_state.largura = largura
    st.session_state.altura = altura
    st.session_state.pessoas = [
        Pessoa(i, random.uniform(0, largura), random.uniform(0, altura))
        for i in range(20)
    ]
    st.session_state.casais = 0

# Atualização automática
st_autorefresh(interval=200, key="auto_refresh")

# ----- Título e Controles -----
st.title("💘 Cupido: Par de Pontos Mais Próximos")
st.caption('Você é o Cupido observando uma praça vista de cima. Várias pessoas (pontos) andam aleatoriamente. Com suas flexas, você pode usar o algoritmo do par de pontos mais próximos para unir dois corações. Eles "saem do gráfico" como se estivessem indo namorar. O jogo continua até todos os pontos serem pareados ou o usuário decidir trocar de cidade (novo mapa).')


col2, col3 = st.columns(2)

with col2:
    if st.button("💘 Flexar casal mais próximo"):
        p1, p2 = encontrar_par_mais_proximo(st.session_state.pessoas)
        if p1 and p2:
            p1.ativo = False
            p2.ativo = False
            st.session_state.casais += 1
            # 3. MENSAGEM DE SUCESSO ATUALIZADA COM NOMES
            st.success(f"Casal formado! **{p1.nome}** e **{p2.nome}** encontraram o amor!")
        else:
            st.info("Todos já formaram um par! ❤️")

with col3:
    if st.button("🏙️ Nova cidade (Resetar)"):
        st.session_state.pessoas = [
            Pessoa(i, random.uniform(0, st.session_state.largura), random.uniform(0, st.session_state.altura))
            for i in range(20)
        ]
        st.session_state.casais = 0
        st.rerun() 

# ----- Movimentação -----
for p in st.session_state.pessoas:
    p.mover(st.session_state.largura, st.session_state.altura)

# ----- Mostrar gráfico -----
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, st.session_state.largura)
ax.set_ylim(0, st.session_state.altura)

for p in st.session_state.pessoas:
    if p.ativo:
        ax.plot(p.x, p.y, 'o', color='#0066cc', markersize=8)  # Ponto azul mais forte
    else:
        # 4. GRÁFICO ATUALIZADO PARA MOSTRAR O NOME
        ax.plot(p.x, p.y, 'o', color='#ff4d4d', markersize=8)  # Ponto vermelho para casal
        # Escreve o primeiro nome ao lado do ponto do casal
        ax.text(p.x + 1, p.y, p.nome.split()[0], fontsize=9, color='#333333')

ax.set_title("Pessoas na Praça Virtual")
ax.set_xticks([])
ax.set_yticks([])
st.pyplot(fig)

# ----- Estatísticas -----
st.markdown("---")
col_stats1, col_stats2 = st.columns(2)
with col_stats1:
    st.metric(label="Casais Formados", value=f"❤️ {st.session_state.casais}")
with col_stats2:
    ativos = sum(1 for p in st.session_state.pessoas if p.ativo)
    st.metric(label="Pessoas Restantes", value=f"🚶 {ativos}")