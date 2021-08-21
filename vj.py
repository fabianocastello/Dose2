import pandas as pd
import numpy as np
pd.options.display.max_columns = None
import warnings
warnings.simplefilter(action='ignore')
import socket
import os
import os.path

import time
from PIL import Image
from datetime import datetime
import requests
from random import randrange
from glob import glob
import zipfile
from unidecode import unidecode
from dateutil import tz

from datetime import time
from datetime import date
from datetime import timedelta

update_from_net = True

runningOn =  socket.gethostname()
is_local = socket.gethostname() in 'LENOVO18 MAC18'

if is_local:
    horario_atual = datetime.now()
else:
    horario_atual = datetime.now() - timedelta(hours=3)


 
global running_date
running_date = horario_atual.strftime("%d-%m-%Y %Hh%Mm")
print('*'*40)

def run():
############################# FRONT END STREAMLIT
    global df, cep, geo
    postos = df.shape[0]
    cep2seach = '01000'
    registro()
    st.markdown(f'''<body>
    <p style="padding-top:0px;font-size:30px;line-height: 32px"><b>💉CADÊ MINHA SEGUNDA DOSE?</b><br><span style="font-size: 10pt;line-height: 10px"><b><i>by</i> Fabiano Castello, cientista de dados @cDataLab</b><span style="font-size: 8pt;line-height: 8px"><br>(contato e outras informações no final da página)</span></span></p></body>''', unsafe_allow_html=True)
    
    with st.expander('Primeira vez por aqui? Leia-Me!', expanded=False):
        st.write('💉 A PMSP criou o site De Olho na Fila para que os paulistanos possam checar quais postos estão funcionando e quais vacinas estão disponíveis. **Porém**, para saber aonde você acha a segunda dose da sua vacina, é necessário verificar local por local, um por um! Uma trabalheira! Esta página ajuda os usuários a verificar qual vacina está disponível no local mais próximo do CEP informado. Vale apenas para CEPs da cidade de São Paulo.')
        st.write('💉 Este app é voluntário, totalmente gratuito e não é vinculado a PMSP de nenhuma forma. A ideia nasceu porque eu passei pela dor de ter que achar a minha segunda dose. Fui obrigado a ir a vários locais.')
        st.write(f'⚠️ Existem duas informações sobre atualização. Uma é o momento em que os dados foram coletados do site da prefeitura (que é {last}), a outra é, para cada local de vacinação, quando foi feita a última atualização (depende de cada local)') 
        st.write(f'⚠️ O site da PMSP não fornece horários de funcionamento de cada local, que podem variar. Sugiro verificar os horários de funcionamento antes de sair.') 
        st.write(f'⚠️ Finalmente, este aplicativo depende de informações públicas da PMSP. Se ela deixar de disponibilizar os dados o aplicativo sairá do ar. Vamos torcer para que não!') 
        
    ################################# Opções
    slot_form = st.empty()

    slot_erro = st.empty()
    
    sharing = st.empty()

    slot_expand5    = st.empty()
    slot_expandRest = st.empty()
    slot_mensagem    = st.empty()
    slot_dispair    = st.empty()
    
    image = Image.open('BannerVJ.jpg')
    st.image(image,use_column_width='always'  )  
    
    st.markdown(f'''<body>
    <p style="padding-top:0px;font-size:18px;line-height:18px"><span style="font-size:16px;line-height:16px">Desenvolvido por Fabiano Castello,<br>Cientista de Dados @cDataLab<br></span><span style="padding-top:0px;font-size:12px;line-height:12px"><span style="font-size:12px;line-height:12px">
    <a href="http://www.linkedin.com/in/fabianocastello"
    target="_blank">LinkedIn</a>, 
    <a href="http://www.fabianocastello.com.br"
    target="_blank">www.fabianocastello.com.br</a>, 
    <a href="http://www.cdatalab.com.br"
    target="_blank">www.cdatalab.com.br</a>, 
    </span></span></p></body>''', unsafe_allow_html=True)
    
    st.markdown(f'''<body>
    <p style="padding-top:0px;font-size:14px;line-height:14px"><span style="font-size:14px;line-height:14px">Agradecimentos ao meu amigo 
    <a href="http://www.linkedin.com/in/marciorf"
    target="_blank">Márcio Francisco</a>. 
    </span></span></p></body>''', unsafe_allow_html=True)

    st.markdown(f'''<body>
    <p style="padding-top:0px;font-size:8px;line-height:8px"><span style="font-size:8px;line-height:8px">{horario_atual.strftime('%d/%m %Hh%Mm')}&nbsp;{runningOn} 
    </span></span></p></body>''', unsafe_allow_html=True)
    
    with slot_form.form(key='inputs'):
        st.write('Informe seu CEP com 5 dígitos, há quanto tempo a informação dos locais foi atualizado e a vacina que você está procurando:')
        col1,col2,col3 = st.columns(3)

        with col1:
            cep2search = st.text_input(
                 label='', value='01000')
        with col2:
            opts    = []
            optsDF  = []
            choices = []
            for index, value in enumerate(sorted((df['slotF'].unique()))):
                if value=='ND':continue 
                optsDF.append(value)
                opts.append(value[2:])
                choices.append(index)
            choice = st.radio("", opts)
        with col3:
            coronavac   = st.checkbox('Coronavac'  , value=True)
            astrazeneca = st.checkbox('Astra-Zeneca'  , value=True)
            pfizer      = st.checkbox('Pfizer'  , value=True)
            selection = ('c' if coronavac   else '')+\
                        ('a' if astrazeneca else '')+\
                        ('p' if pfizer      else '')
                    
        submit_button = st.form_submit_button(
            label='Procurar locais')

    sharing.markdown(sharing_message, unsafe_allow_html=True)



    if submit_button:
        cep2search = cep2search[:5]
        try:
            tmp = cep.loc[cep2search]
        except:
            slot_erro.error(f'o CEP {cep2search} é inválido ou não é um CEP da cidade de São Paulo.')
            st.stop()
            
        if len(selection) == 0:
            slot_erro.error(f'Selecione ao menos uma vacina.')
            st.stop()
            
        c1 = df.coronavac.astype(int).sum()
        c = f'Coronavac: ({c1})' if c1>0 else ''
        a1 = df.astrazeneca.astype(int).sum()
        a = f'Astrazeneca: ({a1})' if a1>0 else ''
        p1 = df.pfizer.astype(int).sum()
        p = f'Pfizer: ({p1})' if p1>0 else ''
    
        df  = update_dist(df,cep2search)
        dsp = update_dsp(df)


        if choice != 'Todos os locais':
            df = df[df['slotF'].apply(
                 lambda x: True  if int(x[:1]) <= int(opts.index(choice))
                      else False)].reset_index(drop=True)

        df['keep'] = df['disp'].apply(lambda x: keep_data(x,selection))
        df = df[df.keep==True].reset_index(drop=True)
    else:
        st.stop()
        
        
    
    with slot_expand5.expander(
        f'5 locais mais próximos do CEP {cep2search}', expanded=True): 
        for index,row in df[:5].iterrows():
            st.markdown(f"""{show_local(df.loc[index])}""",
                        unsafe_allow_html=True)
                        
    with slot_expandRest.expander(
        f'Demais locais ordenados por proximidade do CEP {cep2search}', expanded=False): 
        for index,row in df[5:].iterrows():
            st.markdown(f"""{show_local(df.loc[index])}""",
                        unsafe_allow_html=True)
                        
    slot_mensagem.write(f'De acordo com as opções selecionadas foram  considerados {df.shape[0]} locais, com a seguinte disponibilidade: {c if c1>0 else ""} {a if a1>0 else ""} {p if p1>0 else ""}. Informações atualizadas em {last}.')

    with slot_dispair.expander(f'Desesperado? Veja todos os locais sem fila, com todas as vacinas, ordenados pela atualização mais recente.', expanded=False): 
        for index,row in dsp.iterrows():
            st.markdown(f"""{show_local(dsp.loc[index])}""",
                        unsafe_allow_html=True)
    return()
############################# END OF FRONT END STREAMLIT
def registro(remarks=None):
    form_data = { 'entry.2093722949'  : 'VacinaJá',
                  'entry.442023490' : 'IP',
                  'entry.225285568'   : runningOn,
                  'entry.1052496244'   : remarks}
    ret = requests.post(url_post+'/formResponse', data=form_data, headers=
             {'Referer':url_post+'/viewform',
              'User-Agent': UserAgents[randrange(len(UserAgents))]})
    return(True)
    
import streamlit as st 
try: st.set_page_config(
        page_title='Filômetro "Plus"',
        initial_sidebar_state="collapsed",
        layout="wide")
except: pass
from streamlit import caching
hide_streamlit_style = """<style>#MainMenu {visibility: hidden;}
                          footer {visibility: hidden;}
                          </style>"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

############################# CONFIG
with open("./UserAgents.cfg",encoding='utf-8') as f:
     UserAgents = f.readlines(); f.close()
UserAgents = [c.replace('\n','').strip() for c in UserAgents]
if not runningOn == 'localhost':
    import configparser
    config_parser = configparser.RawConfigParser()
    config_parser.read('./vj.ini')
    url_post  = config_parser.get('RUN', 'url_post')
    urlpkl    = config_parser.get('RUN', 'urlpkl')
    urltxt    = config_parser.get('RUN', 'urltxt')
    urlcep5   = config_parser.get('RUN', 'urlcep5')
    urlgeo    = config_parser.get('RUN', 'urlgeo')
else:
    url_post = st.secrets["url_post"]
    urlpkl   = st.secrets["urlpkl"]
    urltxt   = st.secrets["urltxt"]
    urlcep5  = st.secrets["urlcep5"]
    urlgeo   = st.secrets["urlgeo"]
    
############################# UPDATE DATA
def update_df():
    try:
        if not os.path.exists('./Data'):
            os.makedirs('./Data')
    
        if os.path.isfile('./Data/cep5spCompleto.pkl'):
            cep = pd.read_pickle(r'./Data/cep5spCompleto.pkl')
        else:
            r = requests.get(urlcep5)
            with open(f'./Data/cep5spCompleto.pkl', 'wb') as fout:
                fout.write(r.content)
                cep = pd.read_pickle(r'./Data/cep5spCompleto.pkl')
                
        if os.path.isfile('./Data/GeoEquip.pkl'):
            geo = pd.read_pickle(r'./Data/GeoEquip.pkl')
        else:
            r = requests.get(urlgeo)
            with open(f'./Data/GeoEquip.pkl', 'wb') as fout:
                fout.write(r.content)
                geo = pd.read_pickle(r'./Data/GeoEquip.pkl')

        if update_from_net:
            r = requests.get(urltxt)
            with open(f'./Data/last.txt', 'wb') as fout:
                fout.write(r.content)
        with open(f'./Data/last.txt', 'r') as fout:
            last = fout.read()
        update = datetime.strptime(last[:17],'%Y-%m-%d.%H%M%S')\
                            .replace(tzinfo=tz.tzutc())\
                            .astimezone(tz.gettz('America/Sao_Paulo'))
            
        if update_from_net:
            r = requests.get(urlpkl)
            with open(f'./Data/last.pkl', 'wb') as fout:
                fout.write(r.content)
        df = pd.read_pickle('./Data/last.pkl')
        df = df.merge(geo, on='equipamento', how='left')
        df['ativo'] = df['status_fila'].apply(
            lambda x: x not in
            ['NÃO FUNCIONANDO',
             'AGUARDANDO ABASTECIMENTO 1ª e 2ª DOSE',
             'AGUARDANDO ABASTECIMENTO 1ª DOSE'])
             
        df = df[df.ativo].reset_index(drop=True)
        df.drop(['ativo'], axis = 1, inplace = True)
        df['update'] = df['data_hora'].apply(lambda x: datetime.strptime(x[:19],'%Y-%m-%d %H:%M:%S'))

        df['slot']  = df['update'].apply(lambda x: horario_atual - x)
        df['slotM'] = df['slot'].apply(lambda x: int(x.total_seconds()/60))
        df['slotT'] = df['slotM'].apply(
            lambda x: f'{x}m'    if x <= 60    else
                      f'1h{x-60}m'  if x <= 60*2 else
                      f'2h{x-120}m'  if x <= 60*3 else
                      f'+3h'   if  x <= 60*13 else
                      f'+12h'  if  x <= 60*25 else
                      f'+24h'  if  x <= 60*49 else
                      f'+48h')
        df['slotT2'] = df['slotT']+' ('+df['update'].apply(lambda x: x.strftime('%d/%m %Hh%Mm'))+')'
        bins =   [-10000000, 30, 60, 120,10000000]
        labels = ['0 menos de 30 min',
                  '1 menos de 1 hora',
                  '2 menos de 2 horas',
                  '3 Todos os locais']
        df['slotF'] = pd.cut(df['slotM'], bins=bins, labels=labels)
        
        df['Vacs'] = df['coronavac'].apply(lambda x: int(x))+\
                     df['astrazeneca'].apply(lambda x: int(x))+\
                     df['pfizer'].apply(lambda x: int(x))
        df = df[df['Vacs']>0]
        df['disp'] = df['coronavac'   ].apply(lambda x: 'c' if x=='1' else '')+\
             df['astrazeneca' ].apply(lambda x: 'a' if x=='1' else '')+\
             df['pfizer'      ].apply(lambda x: 'p' if x=='1' else '')

        df.reset_index(drop=True, inplace=True)
        return(True, df,update, cep, geo)
    except Exception as e:
        print(str(e))
        registro(str(e))
        return(False, pd.DataFrame, 'N/A', cep, geo)

global df, cep, geo
with st.spinner('Atualizando dados. Aguarde menos de 1 minuto!'):
    status, df,update, cep, geo = update_df() 
    
print(status, update)
if not status:
    st.error("Erro carregando dados. Pressione F5 para tentar novamente")
    st.stop()

last = datetime.strptime(str(update)[:19], '%Y-%m-%d %H:%M:%S')\
               .strftime('%d/%m %H:%M')

def keep_data(disp, selection):
    for x in selection:
        if x in disp: return(True)
    return(False)

from math import radians, cos, sin, asin, sqrt
def haversine(lat1, lon1, lat2, lon2):
      R = 6372.8 # Earth radius in kilometers use 6372.8 km
      dLat = radians(lat2 - lat1)
      dLon = radians(lon2 - lon1)
      lat1 = radians(lat1)
      lat2 = radians(lat2)
      a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
      c = 2*asin(sqrt(a))
      return(R * c)
      
def update_dist(df,cepf):
    cepf = str(int(cepf)).zfill(5)
    for index, row in df.iterrows():
        try:
            latb = cep.loc[cepf]['lat']
            lonb = cep.loc[cepf]['lon']
            df.at[index,'base'] = cepf
            df.at[index,'latb'] = latb
            df.at[index,'lonb'] = lonb
            lat = cep.loc[row['cep']]['lat']
            lon = cep.loc[row['cep']]['lon']
            df.at[index,'lat' ] = lat
            df.at[index,'lon' ] = lon
            df.at[index,'dist'] = round(haversine(float(lat),float(lon),
                                            float(latb),float(lonb)),1)
        except Exception as e:
            print("type error: " + str(e))
            df.at[index,'dist'] = 100.0
    df.sort_values(by=['dist'], ascending=True, inplace = True)
    return(df)
    
def update_dsp(df):
    #Dispair :-)
    dsp = df #dsp = dispair :-)
    dsp['qt_vacs'] = dsp['coronavac'].astype(int)+dsp['astrazeneca'].astype(int)+dsp['pfizer'].astype(int)
    dsp = dsp[(dsp.indice_fila=='1') & (dsp.qt_vacs==3)]
    dsp.sort_values(by=['slotM'], ascending=True, inplace = True)
    dsp.reset_index(drop=True, inplace=True)
    return(dsp)

def trata_eq(x):
    x = ''.join(c for c in x if (c.isalpha() or c.isdigit() or c in ' ') )
    x = x.replace('  ',' ')
    return(x.strip())

def show_local(r):
    fila =   '🟢 sem Fila'     if r['indice_fila']=='1' else\
             '🟡 fila pequena' if r['indice_fila']=='2' else\
             '🟠 fila média'   if r['indice_fila']=='3' else\
             '🔴 fila grande'  if r['indice_fila']=='4' else\
             '😭 sem informação de fila'
    dist = '<1' if r['dist'] <1 else r['dist'] if r['dist']<=15 else '>15' 
    vacs = ['<span style="color:LimeGreen">💚<b>Coronavac</b></span>' if r['coronavac']=='1' else
            '<span style="color:#F03A17">❌Coronavac</span>',
            '<span style="color:LimeGreen">💚<b>Astrazeneca</b></span>' if r['astrazeneca']=='1' else
            '<span style="color:#F03A17">❌Astrazeneca</span>',
            '<span style="color:LimeGreen">💚<b>Pfizer</b></span>' if r['pfizer']=='1' else
            '<span style="color:#F03A17">❌Pfizer</span>']
    eq_maps = trata_eq(r['equipamento']).replace(' ','+')+'+São+Paulo+SP'
    eq_waze = trata_eq(r['equipamento']).replace(' ','%20')+'%20São%20Paulo%20SP'
    eq_goog = 'horário+'+trata_eq(r['equipamento']).replace(' ','+')
    string =f'''
        <body><p style="font-size:14px;line-height: 16px">
        <b>{r['equipamento']} - {r['tipo_posto']} ({dist}km)</b><br>
        <span style="font-size:12px;">
        &nbsp;&nbsp;&nbsp;{fila} - atualizado há {r['slotT2']})<br>
        &nbsp;&nbsp;&nbsp;vacinas: {' ; '.join(vacs)}</span><br>
        <span style="font-size:10px;">
        &nbsp;&nbsp;&nbsp;{r['endereco']} ({r['distrito']})</span><br></span>
        &nbsp;&nbsp;&nbsp;<a target="_blank"  href="https://www.google.com.br/maps/place/{eq_maps}"
        style="text-decoration:none"> <span style="font-size:10px;">Google Maps</a></span>
        &nbsp;&nbsp;&nbsp;<a target="_blank"  href="https://www.waze.com/ul?q={eq_maps}&navigate=yes"
        style="text-decoration:none"> <span style="font-size:10px;">Waze</a></span>
        &nbsp;&nbsp;&nbsp;<a target="_blank"  href="https://www.google.com/search?q={eq_goog}&sourceid=chrome&ie=UTF-8&tbs=qdr:w"
        style="text-decoration:none"> <span style="font-size:10px;">Verifique se o local está funcionando</a></span>
        </p></body>
                ''' 
    return(string)

            
sharing_message = """
<body><p style="font-size:14px;line-height:16px">Curtiu? Compartilhe!</span>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<a href="https://www.facebook.com/sharer/sharer.php?title=Cade+minha+segunda+dose&u=http://www.fabianocastello.com.br"
style="text-decoration:none" target="_blank"
class="fa fa-facebook"> </a>&nbsp;
<a href="https://twitter.com/intent/tweet?text=Cadê+minha+segunda+dose&url=http:www.fabianocastello.com.br" 
style="text-decoration:none" target="_blank"
class="fa fa-twitter"></a>&nbsp;
<a href="https://www.linkedin.com/shareArticle?title=Cade+minha+segunda+dose%3F&url=http:www.fabianocastello.com.br" 
style="text-decoration:none" target="_blank"
class="fa fa-linkedin"></a>&nbsp;
<a href="whatsapp://send?text=Cade+minha+segunda+dose%3F http:www.fabianocastello.com.br" 
style="text-decoration:none" target="_blank"
class="fa fa-whatsapp"></a>
</p></body>
"""

run()





