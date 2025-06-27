import streamlit as st
import random
import math
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# ----- Classe Pessoa -----
class Pessoa:
    def __init__(self, id, x, y):
        self.id = id
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


# ----- Algoritmo do par mais próximo otimizado -----
def encontrar_par_mais_proximo(pessoas):
    """
    Encontra o par mais próximo usando divisão e conquista O(n log n)
    Fallback para força bruta O(n²) quando há poucos pontos
    """
    pessoas_ativas = [p for p in pessoas if p.ativo]
    
    if len(pessoas_ativas) < 2:
        return (None, None)
    
    # Para muitos pontos, usa divisão e conquista
    return _par_mais_proximo(pessoas_ativas)

def _forca_bruta(pessoas):
    """Algoritmo força bruta O(n²) para poucos pontos"""
    min_dist = float('inf')
    par = (None, None)
    for i in range(len(pessoas)):
        for j in range(i + 1, len(pessoas)):
            d = pessoas[i].distancia(pessoas[j])
            if d < min_dist:
                min_dist = d
                par = (pessoas[i], pessoas[j])
    return par

def _par_mais_proximo(pessoas):
    # Ordena por coordenada x
    px = sorted(pessoas, key=lambda p: p.x)
    py = sorted(pessoas, key=lambda p: p.y)
    
    return _par_mais_proximo_rec(px, py)

def _par_mais_proximo_rec(px, py):
    """Função recursiva do algoritmo de divisão e conquista"""
    n = len(px)
    
    # Caso base: poucos pontos
    if n <= 3:
        return _forca_bruta(px)
    
    # Divide no meio
    mid = n // 2
    midpoint = px[mid]
    
    pyl = [p for p in py if p.x <= midpoint.x]
    pyr = [p for p in py if p.x > midpoint.x]
    
    # Conquista: encontra o par mais próximo em cada metade
    par_esq = _par_mais_proximo_rec(px[:mid], pyl)
    par_dir = _par_mais_proximo_rec(px[mid:], pyr)
    
    # Encontra a menor distância entre as duas metades
    dist_esq = par_esq[0].distancia(par_esq[1]) if par_esq[0] else float('inf')
    dist_dir = par_dir[0].distancia(par_dir[1]) if par_dir[0] else float('inf')
    
    if dist_esq <= dist_dir:
        melhor_par = par_esq
        min_dist = dist_esq
    else:
        melhor_par = par_dir
        min_dist = dist_dir
    
    # Verifica pontos próximos à linha divisória
    strip = [p for p in py if abs(p.x - midpoint.x) < min_dist]
    par_strip = _strip_closest(strip, min_dist)
    
    if par_strip and par_strip[0]:
        dist_strip = par_strip[0].distancia(par_strip[1])
        if dist_strip < min_dist:
            return par_strip
    
    return melhor_par

def _strip_closest(strip, d):
    """Encontra o par mais próximo na faixa central"""
    min_dist = d
    par = (None, None)
    
    # Ordena por coordenada y
    strip.sort(key=lambda p: p.y)
    
    for i in range(len(strip)):
        j = i + 1
        # Verifica apenas pontos próximos em y (otimização crucial)
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
    st.session_state.pausado = False

# 🔄 Atualização automática a cada 200ms
st_autorefresh(interval=200, key="auto_refresh")

# ----- Título e Controles -----
st.title("💘 Cupido: Par de Pontos Mais Próximos")

col2, col3 = st.columns(2)

with col2:
    if st.button("💘 Flexar casal"):
        p1, p2 = encontrar_par_mais_proximo(st.session_state.pessoas)
        if p1 and p2:
            p1.ativo = False
            p2.ativo = False
            st.session_state.casais += 1
            st.success(f"Casal formado: {p1.id} + {p2.id}")
        else:
            st.info("Nenhum par restante!")

with col3:
    if st.button("🔁 Nova cidade"):
        st.session_state.pessoas = [
            Pessoa(i, random.uniform(0, st.session_state.largura), random.uniform(0, st.session_state.altura))
            for i in range(20)
        ]
        st.session_state.casais = 0

for p in st.session_state.pessoas:
    p.mover(st.session_state.largura, st.session_state.altura)

# ----- Mostrar gráfico -----
fig, ax = plt.subplots()
ax.set_xlim(0, st.session_state.largura)
ax.set_ylim(0, st.session_state.altura)

for p in st.session_state.pessoas:
    if p.ativo:
        ax.plot(p.x, p.y, 'bo')  # ponto azul
    else:
        ax.plot(p.x, p.y, 'ro')  # ponto vermelho (casal removido)
        ax.text(p.x, p.y, str(p.id), fontsize=8, ha='right', va='bottom')

ax.set_title("Pessoas na praça")

st.pyplot(fig)

# ----- Estatísticas -----
st.markdown(f"**Casais formados:** {st.session_state.casais}")
ativos = sum(1 for p in st.session_state.pessoas if p.ativo)
st.markdown(f"**Pessoas restantes:** {ativos}")
