R = [rmin, ri, ..., rmax]  
I = Bmin = Bmax = 3  # Buffer constants (number of segments)
'''
total = 60 
# treshholds
0 > i > b_alfa > b_beta > bmax
i = 0 - 10
i - b_alfa = 10 - 25 
b_ alfa - b_beta = 25 - 50
b_beta - b_max = 50 - 60
b_curr = ocupação do buffer

## media harmonica
bitrate = tamanho do segmento / tempo de download

w1 = tamanho do segmento / birate
w2 = (tamanho do segmento / bitrate)/bitrate

w3 = w1 / w2

harmonic_mean = [  w3n, w3n2, ......  ]

n =  segmento mais atual
rcurr = bitrate do segmento mais atual
bcurr = ocupação do buffer


qualidades = [46980, 91917, 135410, 182366, 226106, 270316, 352546, 
424520, 537825, 620705, 808057, 1071529, 1312787, 1662809, 2234145, 2617284, 3305118, 3841983, 4242923, 4726737]

'''

def sara():

    qualidades_disponiveis = [46980, 91917, 135410, 182366, 226106, 270316, 352546, 
                        424520, 537825, 620705, 808057, 1071529, 1312787, 1662809, 
                        2234145, 2617284, 3305118, 3841983, 4242923, 4726737]

    # Tresholds
    self.I = 5
    self.b_alfa = 10
    self.b_beta = 30
    self.b_max = 60
    
    # Bitrate
    self.request_time = 0
    self.bitrate = []
    self.tamanhos_baixados = []

    # Harmonic mean
    self.media_com_peso = 0

    # Qualidades disponiveis
    self.qi = []
    self.qualidade_atual_indice = 0

    # Necessario para calcular corretamente o algoritmo do SARA
    with open('D:\developer\projetos\redes\redes\pydash\lista_tamanhos.json', 'r', encoding='utf-8') as json_file:
        self.lista_tamanhos = json.loads(json_file)
        self.buffer_ocupancy = 0

    if b_curr <= I:
        qualidade = self.qi[0]
         
    else:
        if (lista_w[-1]/Hn) > b_curr - I:
            # Fast Start, passa pela lista ate achar um mais proximo
            for j in qualidades_disponiveis:
                atual = qualidade_atual
                if j/Hn < (lista_w[-1]/Hn) and j > qualidades_disponiveis[qualidade_atual]:
                    atual = j
                else:
                    r_next = atual
                    break

        elif b_curr <= b_alfa:
            # Additive Increase
            if (qualidades_disponiveis[qualidade_atual + 1]/Hn) < b_curr - I:
                r_next = qualidade_atual + 1
                wait_time = 0

            else:
                r_next = qualidade_atual
                wait_time = 0

        elif b_curr <= b_beta:
            # Aggressive Switching
            for j in qualidades_disponiveis:
                atual = qualidade_atual
                if j/Hn < (lista_w[-1]/Hn) - I and j > qualidades_disponiveis[qualidade_atual]:
                    atual = j
                else:
                    r_next = atual
                    break
            wait_time = 0

        elif b_curr > b_beta:
            # Delayed Download
            for j in qualidades_disponiveis:
                atual = qualidade_atual
                if j/Hn < (lista_w[-1]/Hn) - b_alfa and j >= qualidades_disponiveis[qualidade_atual]:
                    atual = j
                else:
                    r_next = atual
                    break
            sleep(b_curr - b_beta)
        else:
            r_next = qualidade_atual 






def segment_aware_rate_adaptation(n, curr, Bcurr, Hn, sizes):
    """
    n: Segment number of the most recent download
    curr: Bitrate of the most recently downloaded segment
    Bcurr: Current buffer occupancy in seconds
    Hn: Weighted Harmonic mean download rate for the first n segments
    sizes: List of segment sizes for bitrates [rmin, ..., rm, ..., rmax]
    """
    if Bcurr <= I:
        In_next = rmin
        wait_time = 0
    elif (1/Hn) > Bcurr - I:
        # Fast Start
        In_next = max([r for r in R if (1/Hn) <= Bcurr - I and sizes[r] <= curr])
        wait_time = 0
    elif Bcurr <= Bmin:
        # Additive Increase
        if (1/Hn) < Bcurr - I:
            In_next = curr
            wait_time = 0
        else:
            In_next = curr - 1
            wait_time = 0
    elif Bcurr <= Bmax:
        # Aggressive Switching
        In_next = max([r for r in R if (1/Hn) <= Bcurr - I and sizes[r] >= curr])
        wait_time = 0
    elif Bcurr > Bmax:
        # Delayed Download
        In_next = max([r for r in R if (1/Hn) <= Bcurr - Bmin and sizes[r] >= curr])
        wait_time = Bcurr - Bmax
    else:
        In_next = curr - 1
        wait_time = 0
    return In_next, wait_time
