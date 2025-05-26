
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Analisador de Transformadores', layout='wide')

st.title('📊 Analisador de Carregamento de Transformadores')
st.markdown('Faça o upload de um arquivo Excel com as colunas: **Transformador, Horário, Carga (kW), Geração (kW), Capacidade (kVA)**')

uploaded_file = st.file_uploader('📁 Upload do arquivo .xlsx', type=['xlsx'])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        required_cols = {'Transformador', 'Horário', 'Carga (kW)', 'Geração (kW)', 'Capacidade (kVA)'}
        if not required_cols.issubset(df.columns):
            st.error(f'O arquivo deve conter as colunas: {required_cols}')
        else:
            fp = 0.92
            df['Capacidade (kW)'] = df['Capacidade (kVA)'] * fp
            df['Demanda Líquida (kW)'] = df['Carga (kW)'] - df['Geração (kW)']
            df['% da Capacidade'] = (df['Demanda Líquida (kW)'] / df['Capacidade (kW)']) * 100

            def classificar(valor):
                if valor < 10:
                    return 'Subutilização'
                elif valor < 80:
                    return 'Operação normal'
                elif valor < 100:
                    return 'Alerta - Crescimento de carga'
                elif valor < 120:
                    return 'Sobrecarga controlada (curto prazo)'
                elif valor <= 140:
                    return 'Risco alto - Planejar ampliação'
                else:
                    return 'Risco crítico - Obra imediata'

            df['Status'] = df['% da Capacidade'].apply(classificar)

            trafos = df['Transformador'].unique()
            st.success(f'Transformadores encontrados: {len(trafos)}')

            for trafo in trafos:
                st.subheader(f'Transformador: {trafo}')
                dados = df[df['Transformador'] == trafo]

                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(dados['Horário'], dados['% da Capacidade'], marker='o', label='Carregamento (%)')

                ax.axhspan(0, 10, facecolor='lightgray', alpha=0.5, label='Subutilização (<10%)')
                ax.axhspan(10, 80, facecolor='lightgreen', alpha=0.3, label='Operação normal (10-80%)')
                ax.axhspan(80, 100, facecolor='yellow', alpha=0.3, label='Alerta (80-100%)')
                ax.axhspan(100, 120, facecolor='orange', alpha=0.3, label='Sobrecarga (100-120%)')
                ax.axhspan(120, 140, facecolor='red', alpha=0.3, label='Risco alto (120-140%)')
                ax.axhspan(140, 200, facecolor='darkred', alpha=0.4, label='Crítico (>140%)')

                ax.set_title(f'Carregamento do Transformador {trafo}')
                ax.set_xlabel('Horário')
                ax.set_ylabel('% da Capacidade')
                ax.set_xticks(range(len(dados['Horário'])))
                ax.set_xticklabels(dados['Horário'], rotation=45)
                ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3)
                ax.grid(True)
                st.pyplot(fig)

            with st.expander('📥 Baixar dados analisados'):
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button('⬇️ Baixar CSV', csv, file_name='diagnostico_transformadores.csv')

    except Exception as e:
        st.error(f'Erro ao processar o arquivo: {e}')
