# -*- coding: utf-8 -*-
from r2a.ir2a import IR2A
from player.parser import *
from player.player import Player
import time
from time import sleep
from statistics import mean
import json


class R2A_SARA(IR2A):


    def __init__(self, id):
        IR2A.__init__(self, id)

        # segmentos ja baixados
        self.segmentos_baixados = 0
        # Tresholds
        self.I = 12
        self.b_alfa = 32
        self.b_beta = 50
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
        with open('D:\\developer\\projetos\\redes\\redes\\pydash\\lista_tamanhos.json', 'r', encoding='utf-8') as json_file:
            data_json = json_file.read()
            self.lista_tamanhos = json.loads(data_json)
           # print(self.lista_tamanhos)
        self.buffer_ocupancy = 0
        

    def handle_xml_request(self, msg):
        self.request_time = 0
        self.request_time = time.perf_counter()
        self.send_down(msg)


    def handle_xml_response(self, msg):
        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()

        t = time.perf_counter() - self.request_time
        self.bitrate.append(msg.get_bit_length() / t)
        self.tamanhos_baixados.append(msg.get_bit_length())
        self.buffer_ocupancy = self.whiteboard.get_amount_video_to_play()
        self.segmentos_baixados += 1 if self.segmentos_baixados <= 97 else 0

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # media com peso do SARA
        self.media_com_peso = (sum(self.tamanhos_baixados)/sum(self.bitrate))

        # tamanho do proximo segmento
        tamanho_proximo_segmento = int(self.lista_tamanhos[str(self.qualidade_atual_indice)][self.segmentos_baixados + 1])
        aux = self.qualidade_atual_indice + 1 if self.qualidade_atual_indice < 19 else 0
        tamanho_proximo_segmento_proxima_qualidade = int(self.lista_tamanhos[str(aux)][self.segmentos_baixados + 1])

## Inicio do algoritmo do SARA
        # Se o buffer estiver vazio, baixa a qualidade mais baixa (Quick Start)
        if self.buffer_ocupancy <= self.I:
            self.qualidade_atual_indice = 0

        else:
            # fast start
                    #tamanho estimado de dowload do proximo segmento menor que buffer - primeiro trashold(I)
            if self.buffer_ocupancy - self.I < ((tamanho_proximo_segmento/self.qi[self.qualidade_atual_indice])/self.media_com_peso):
                    #loop para achar a maxima qualidade que tem tempo de dowload menor que o buffer - primeiro trashold(I)
                for j in reversed(range(len(self.qi))):
                    self.qualidade_atual_indice = j
                    proximo_segmento = self.lista_tamanhos[str(j)][self.segmentos_baixados]
                    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                    print((proximo_segmento/self.qi[self.qualidade_atual_indice])/self.media_com_peso)
                    print(self.qualidade_atual_indice)
                    print(self.buffer_ocupancy - self.I)
                    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                    if (proximo_segmento/self.qi[self.qualidade_atual_indice])/self.media_com_peso < self.buffer_ocupancy - self.I:
                        self.qualidade_atual_indice = j
                        break

                    else:
                        continue

            # Additive Increase //aumenta a qualidade do video gradativamente
            elif self.buffer_ocupancy <= self.b_alfa:
                if (tamanho_proximo_segmento/self.qi[self.qualidade_atual_indice])/self.media_com_peso < self.buffer_ocupancy - self.I:
                    self.qualidade_atual_indice += 1 if self.qualidade_atual_indice < 19 else 0

                else:
                    self.qualidade_atual_indice = self.qualidade_atual_indice

            # Agressive Switching
                    #loop para achar a maxima qualidade que tem tempo de dowload menor que o buffer - primeiro trashold(I)
            elif self.buffer_ocupancy <= self.b_beta:
                for j in range(self.qi):
                    self.qualidade_atual_indice = j
                    proximo_segmento = self.lista_tamanhos[j][self.segmentos_baixados]

                    if (proximo_segmento/self.qi[self.qualidade_atual_indice])/self.media_com_peso < self.buffer_ocupancy - self.I:
                        self.qualidade_atual_indice = j

                    else:
                        self.qualidade_atual_indice = j
                        break

            # Delayed Download
                    #loop para achar a maxima qualidade que tem tempo de dowload menor que o buffer - segundo trashold(b_alfa)
            elif self.buffer_ocupancy > self.b_beta:
                for j in range(self.qi):
                    self.qualidade_atual_indice = j
                    proximo_segmento = self.lista_tamanhos[j][self.segmentos_baixados]

                    if (proximo_segmento/self.qi[self.qualidade_atual_indice])/self.media_com_peso < self.buffer_ocupancy - self.b_alfa:
                        self.qualidade_atual_indice = j

                    else:
                        self.qualidade_atual_indice = j
                        break
                # tempo de espera para o download do proximo segmento
                sleep(self.buffer_ocupancy - self.b_alfa)

            else:
                self.qualidade_atual_indice = self.qualidade_atual_indice // 2
## Fim do algoritmo do SARA

        msg.add_quality_id(self.qi[self.qualidade_atual_indice])
        self.send_down(msg)
        self.request_time = time.perf_counter()
        #print(self.tamanhos_baixados,self.bitrate, sep='>>>>>>>>>>>>>>>>')
        #print()
        #print(sum(self.tamanhos_baixados)/sum(self.bitrate))


    def handle_segment_size_response(self, msg):
        t = time.perf_counter() - self.request_time
        print(t)

        self.bitrate.append(msg.get_bit_length() / t)
        self.tamanhos_baixados.append(msg.get_bit_length())
        self.buffer_ocupancy = self.whiteboard.get_amount_video_to_play()
        self.segmentos_baixados += 1 if self.segmentos_baixados <= 97 else 0

        self.send_up(msg)
        

    def initialize(self):
        pass
        

    def finalization(self):
        pass
