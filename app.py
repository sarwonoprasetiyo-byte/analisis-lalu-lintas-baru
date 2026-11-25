"""Traffic Analysis Dashboard | PJBL Teknik Sipil.
Jalankan: streamlit run app.py
"""
from datetime import date
from html import escape

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

LABEL = 'Interval pengamatan'
DURATION = 'Durasi (menit)'
VEHICLES = ['Sepeda Motor', 'Kendaraan Ringan', 'Kendaraan Berat']
TOTAL = 'Total (kend)'
FLOW = 'Arus (kend/jam)'
EQ_TOTAL = 'Total (smp)'
EQ_FLOW = 'Arus (smp/jam)'
COLORS = dict(zip(VEHICLES, ['#0E7490', '#2563EB', '#F59E0B']))
DEFAULT = pd.DataFrame({LABEL: ['Interval 1'], DURATION: [60],
                        VEHICLES[0]: [204], VEHICLES[1]: [82], VEHICLES[2]: [41]})


def fmt(value, digits=0):
    """Format angka Indonesia."""
    return f'{value:,.{digits}f}'.replace(',', '_').replace('.', ',').replace('_', '.')


def analyze(raw, factors=None):
    """Validasi input, hitung hasil per interval, komposisi, dan ringkasan.

    Asumsi: interval tidak tumpang tindih dan seluruh baris berasal dari
    cakupan survei yang sama. Durasi adalah waktu pengamatan efektif.
    """
    if raw.empty:
        raise ValueError('Tambahkan minimal satu interval pengamatan.')
    df = raw[[LABEL, DURATION, *VEHICLES]].copy().reset_index(drop=True)
    df[LABEL] = df[LABEL].fillna('').astype(str).str.strip()
    if (df[LABEL] == '').any() or df[LABEL].duplicated().any():
        raise ValueError('Nama interval wajib diisi dan tidak boleh sama.')
    for column in [DURATION, *VEHICLES]:
        df[column] = pd.to_numeric(df[column], errors='coerce')
        if df[column].isna().any() or df[column].isin([float('inf'), -float('inf')]).any():
            raise ValueError(f'Isi angka yang valid pada kolom {column}.')
    if (df[DURATION] <= 0).any():
        raise ValueError('Durasi pengamatan harus lebih besar dari nol.')
    for column in VEHICLES:
        if (df[column] < 0).any() or (df[column] % 1 != 0).any():
            raise ValueError(f'{column} harus berupa bilangan bulat nonnegatif.')
        df[column] = df[column].astype('int64')
    df[TOTAL] = df[VEHICLES].sum(axis=1)
    df[FLOW] = df[TOTAL] * 60 / df[DURATION]
    if factors is not None:
        if len(factors) != len(VEHICLES) or not all(0 < x < float('inf') for x in factors):
            raise ValueError('Faktor ekuivalensi harus lebih besar dari nol dan berhingga.')
        df[EQ_TOTAL] = sum(df[v] * f for v, f in zip(VEHICLES, factors))
        df[EQ_FLOW] = df[EQ_TOTAL] * 60 / df[DURATION]
    counts = df[VEHICLES].sum()
    total = int(counts.sum())
    minutes = float(df[DURATION].sum())
    composition = pd.DataFrame({'Jenis Kendaraan': VEHICLES, 'Jumlah (kend)': counts.values,
                                'Persentase (%)': counts.values * 100 / total if total else [0., 0., 0.]})
    peak = float(df[FLOW].max())
    peaks = df.loc[(df[FLOW] - peak).abs() < 1e-9, LABEL].tolist()
    summary = {'total': total, 'minutes': minutes, 'avg': total * 60 / minutes,
               'peak': peak, 'peaks': peaks,
               'dominant': counts[counts == counts.max()].index.tolist() if total else [],
               'eq_avg': float(df[EQ_TOTAL].sum() * 60 / minutes) if factors is not None else None}
    return df, composition, summary


def csv_bytes(df):
    # Pemisah titik koma, desimal koma, BOM: praktis untuk Excel regional Indonesia.
    return df.to_csv(index=False, sep=';', decimal=',', float_format='%.4f').encode('utf-8-sig')


def chart_style(fig, height=335):
    fig.update_layout(height=height, margin=dict(l=12, r=12, t=18, b=12),
                      legend=dict(orientation='h', y=1.12),
                      font=dict(family='Arial, sans-serif'),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig


def main():
    st.set_page_config(page_title='Traffic Analysis | PJBL', page_icon='🚦', layout='wide')
    st.markdown('''<style>
    .block-container {max-width: 1440px; padding-top: 2rem; padding-bottom: 2rem;}
    .traffic-hero {background: linear-gradient(115deg,#0B2138,#123D5A 65%,#0E7490);
       border-radius: 18px; padding: 28px 32px; color: #fff; margin-bottom: 22px;}
    .traffic-hero h1 {font-size: clamp(1.7rem,4vw,2.7rem); color: #fff; margin: 3px 0; padding: 0;}
    .traffic-hero p {color: #D9EAF3; margin: 8px 0 0; font-size: .95rem;}
    .traffic-kicker {letter-spacing: .14em; font-size: .72rem; color: #A5F3FC; font-weight: 700;}
    [data-testid="stMetric"] {border: 1px solid rgba(125,145,165,.30); padding: 14px 16px;
       border-radius: 13px; min-height: 105px;}
    [data-testid="stMetricValue"] {font-size: clamp(1.25rem,3vw,2rem); font-weight: 700;}
    .traffic-meta {opacity:.75; font-size:.9rem; margin: 0 0 15px; overflow-wrap:anywhere;}
    </style>
    <div class="traffic-hero"><div class="traffic-kicker">PROJECT BASED LEARNING · TEKNIK SIPIL</div>
    <h1>Traffic Analysis Dashboard</h1><p>Program Analisis Lalu Lintas • Pencatatan, visualisasi, dan evaluasi data survei kendaraan.</p></div>''', unsafe_allow_html=True)

    with st.sidebar:
        st.header('Pengaturan survei')
        location = st.text_input('Lokasi / ruas jalan', placeholder='Nama jalan atau lokasi survei')
        survey_date = st.date_input('Tanggal survei', value=date.today())
        surveyor = st.text_input('Nama surveyor / kelompok', placeholder='Nama atau kelompok PJBL')
        direction = st.selectbox('Cakupan arah', ['Belum ditentukan', 'Satu arah', 'Dua arah'])
        st.divider()
        st.subheader('Analisis tambahan')
        use_eq = st.checkbox('Aktifkan ekuivalensi (smp)', value=False,
                            help='Gunakan hanya jika faktor yang sesuai dengan metode dan kondisi ruas tersedia.')
        factors = None
        if use_eq:
            st.caption('Nilai awal 1,00 hanya placeholder, bukan faktor standar. Ganti sesuai acuan dan kondisi survei.')
            factors = [st.number_input(f'Faktor {v}', min_value=0.01, max_value=100.0,
                                        value=1.0, step=0.05, format='%.2f', key=f'f_{i}')
                       for i, v in enumerate(VEHICLES)]
            reference = st.text_input('Acuan faktor / catatan', placeholder='Pedoman, tipe jalan, kondisi arus')
            if not reference.strip():
                st.warning('Acuan faktor belum diisi. Hasil smp masih bersifat simulasi.')
        else:
            reference = ''
        st.divider()
        st.caption('PJBL · Analisis lalu lintas\n\nData kendaraan per interval pengamatan.')

    st.markdown(f'<div class="traffic-meta">{escape(location.strip() or "Lokasi belum diisi")} &nbsp;·&nbsp; '
                f'{survey_date.strftime("%d/%m/%Y")} &nbsp;·&nbsp; {escape(direction)}</div>', unsafe_allow_html=True)

    if 'editor_version' not in st.session_state:
        st.session_state.editor_version = 0
    with st.container(border=True):
        h, reset = st.columns([4, 1])
        h.subheader('01 / Data pengamatan')
        if reset.button('Reset data contoh', use_container_width=True):
            st.session_state.editor_version += 1
            st.rerun()
        st.caption('Edit angka langsung pada tabel. Tambah baris untuk interval berikutnya atau hapus baris yang tidak diperlukan. '
                   'Durasi awal 60 menit adalah asumsi contoh; ubah sesuai survei. Gunakan interval tidak tumpang tindih dengan cakupan arah yang sama.')
        raw = st.data_editor(DEFAULT.copy(), num_rows='dynamic', hide_index=True,
                             use_container_width=True, key=f'editor_{st.session_state.editor_version}',
                             column_config={LABEL: st.column_config.TextColumn('Interval / waktu', required=True),
                                 DURATION: st.column_config.NumberColumn('Durasi (menit)', min_value=0.01, step=1, required=True, format='%.2f'),
                                 **{v: st.column_config.NumberColumn(v, min_value=0, step=1, required=True, format='%d') for v in VEHICLES}})
    try:
        df, comp, result = analyze(raw, factors)
    except ValueError as err:
        st.error(str(err))
        st.stop()
        return

    st.subheader('02 / Ringkasan survei')
    a, b, c, d = st.columns(4)
    a.metric('Total kendaraan', f'{fmt(result["total"])} kend')
    b.metric('Durasi pengamatan', f'{fmt(result["minutes"], 2)} mnt')
    c.metric('Arus rata-rata', f'{fmt(result["avg"], 2)}', help='Total kendaraan dibagi total jam pengamatan (rata-rata berbobot durasi).')
    d.metric('Arus interval tertinggi', f'{fmt(result["peak"], 2)}', help='Arus per jam tertinggi dari interval yang dimasukkan; bukan volume jam puncak terukur jika interval kurang dari 60 menit.')
    st.caption('Satuan arus: kendaraan/jam. Arus interval merupakan jumlah kendaraan yang dinormalisasi terhadap durasi.')
    if use_eq:
        st.metric('Arus ekuivalen rata-rata (smp/jam)', fmt(result['eq_avg'], 2))
        st.caption('Hasil ekuivalensi dihitung dari faktor masukan pengguna; bukan penetapan kapasitas atau tingkat pelayanan jalan.')

    tab1, tab2, tab3, tab4 = st.tabs(['Dashboard', 'Tabel hasil', 'Metode & kesimpulan', 'Ekspor data'])
    with tab1:
        left, right = st.columns([3, 2])
        with left:
            with st.container(border=True):
                st.markdown('**Jumlah kendaraan berdasarkan jenis**')
                bar = px.bar(comp, x='Jenis Kendaraan', y='Jumlah (kend)', color='Jenis Kendaraan',
                             color_discrete_map=COLORS, text='Jumlah (kend)')
                bar.update_traces(textposition='outside', cliponaxis=False, marker_line_width=0)
                bar.update_layout(showlegend=False, xaxis_title=None, yaxis_title='Kendaraan',
                                  yaxis_range=[0, max(1, result['total'] * 1.12)])
                st.plotly_chart(chart_style(bar), use_container_width=True, config={'displaylogo': False})
        with right:
            with st.container(border=True):
                st.markdown('**Komposisi lalu lintas**')
                if result['total']:
                    pie = px.pie(comp, names='Jenis Kendaraan', values='Jumlah (kend)', color='Jenis Kendaraan',
                                 color_discrete_map=COLORS, hole=.67)
                    pie.update_traces(textposition='inside', textinfo='percent', sort=False)
                    pie.add_annotation(text=f'<b>{fmt(result["total"])}</b><br>kendaraan', x=.5, y=.5,
                                       showarrow=False, font_size=17)
                    st.plotly_chart(chart_style(pie), use_container_width=True, config={'displaylogo': False})
                else:
                    st.info('Komposisi belum dapat ditampilkan karena tidak ada kendaraan tercatat.')
        with st.container(border=True):
            st.markdown('**Arus lalu lintas per interval**')
            line = go.Figure(go.Scatter(x=df[LABEL], y=df[FLOW], mode='lines+markers' if len(df) > 1 else 'markers',
                                        name='Arus', line=dict(color='#0E7490', width=3), marker=dict(size=10)))
            line.add_hline(y=result['avg'], line_dash='dash', line_color='#F59E0B',
                           annotation_text='Rata-rata', annotation_position='top left')
            line.update_layout(xaxis_title='Interval (urutan input)', yaxis_title='kend/jam', yaxis_rangemode='tozero')
            st.plotly_chart(chart_style(line, 300), use_container_width=True, config={'displaylogo': False})
            if len(df) > 1:
                st.caption('Grafik menggunakan urutan baris pengamatan, bukan skala waktu kontinu.')
    with tab2:
        st.subheader('Rekapitulasi per interval')
        st.dataframe(df, hide_index=True, use_container_width=True,
                     column_config={FLOW: st.column_config.NumberColumn(format='%.2f'),
                                    EQ_TOTAL: st.column_config.NumberColumn(format='%.2f'),
                                    EQ_FLOW: st.column_config.NumberColumn(format='%.2f')})
        st.subheader('Komposisi kendaraan')
        st.dataframe(comp, hide_index=True, use_container_width=True,
                     column_config={'Persentase (%)': st.column_config.NumberColumn(format='%.2f %%')})
        st.caption('Untuk total nol, persentase ditampilkan 0 sebagai penanda tidak ada kendaraan (komposisi tidak terdefinisi).')
    if result['total']:
        dominant = ', '.join(result['dominant'])
        share = float(comp['Persentase (%)'].max())
        conclusion = (f'Pengamatan pada {location.strip() or "lokasi yang belum diisi"} selama {fmt(result["minutes"], 2)} menit '
                      f'mencatat {fmt(result["total"])} kendaraan. Jenis kendaraan dengan jumlah tertinggi adalah {dominant} '
                      f'({fmt(share, 2)}% per jenis tersebut). Arus rata-rata sebesar {fmt(result["avg"], 2)} kendaraan/jam. '
                      f'Arus interval tertinggi sebesar {fmt(result["peak"], 2)} kendaraan/jam tercatat pada '
                      f'{", ".join(result["peaks"])}.')
    else:
        conclusion = 'Seluruh interval mencatat nol kendaraan. Komposisi dominan dan interval arus puncak tidak dapat ditetapkan dari data ini.'
    with tab3:
        st.subheader('Dasar perhitungan')
        st.markdown('**1. Jumlah kendaraan**')
        st.latex(r'N = N_{SM} + N_{KR} + N_{KB}')
        st.markdown('**2. Persentase jenis kendaraan** (jika total lebih dari nol)')
        st.latex(r'P_i = \frac{N_i}{N}\times 100\%')
        st.markdown('**3. Arus lalu lintas per interval** (T dalam menit)')
        st.latex(r'Q = \frac{60N}{T}\quad (\mathrm{kend/jam})')
        st.markdown('**4. Arus rata-rata selama survei**')
        st.latex(r'\bar{Q}=\frac{60\sum N_i}{\sum T_i}')
        st.markdown('**5. Arus ekuivalen** (opsional, faktor e dari pengguna)')
        st.latex(r'Q_{smp}=\frac{60}{T}(e_{SM}N_{SM}+e_{KR}N_{KR}+e_{KB}N_{KB})')
        st.subheader('Kesimpulan otomatis')
        st.write(conclusion)
        st.info('Kesimpulan bersifat deskriptif. Penilaian kemacetan, kapasitas, derajat kejenuhan, dan tingkat pelayanan memerlukan data tambahan serta metode yang sesuai.')
    with tab4:
        st.subheader('Unduh hasil survei')
        st.caption('CSV dapat dibuka di Microsoft Excel. Format menggunakan pemisah titik koma dan desimal koma.')
        detail = df.copy()
        for col, val in reversed(list({'Lokasi': location, 'Tanggal': survey_date.isoformat(),
                                      'Surveyor': surveyor, 'Cakupan arah': direction}.items())):
            detail.insert(0, col, val)
        if use_eq:
            for v, f in zip(VEHICLES, factors):
                detail[f'Faktor {v}'] = f
            detail['Acuan faktor'] = reference
        summary_df = pd.DataFrame([{'Lokasi': location, 'Tanggal': survey_date.isoformat(), 'Surveyor': surveyor,
                                    'Cakupan arah': direction, 'Total (kend)': result['total'],
                                    'Durasi (menit)': result['minutes'], 'Arus rata-rata (kend/jam)': result['avg'],
                                    'Arus tertinggi (kend/jam)': result['peak'],
                                    'Interval tertinggi': ', '.join(result['peaks']) if result['total'] else '',
                                    'Arus rata-rata (smp/jam)': result['eq_avg'], 'Kesimpulan': conclusion}])
        if use_eq:
            for v, f in zip(VEHICLES, factors):
                summary_df[f'Faktor {v}'] = f
            summary_df['Acuan faktor'] = reference
        x, y, z = st.columns(3)
        x.download_button('Data per interval (.csv)', csv_bytes(detail), 'data_lalu_lintas.csv', 'text/csv', use_container_width=True)
        y.download_button('Komposisi (.csv)', csv_bytes(comp), 'komposisi_kendaraan.csv', 'text/csv', use_container_width=True)
        z.download_button('Ringkasan (.csv)', csv_bytes(summary_df), 'ringkasan_survei.csv', 'text/csv', use_container_width=True)
        st.caption('Simpan data sebelum menutup atau memuat ulang halaman; versi ini belum menggunakan database permanen.')
    st.divider()
    st.caption('Traffic Analysis Dashboard · Project Based Learning · Teknik Sipil')


if __name__ == '__main__':
    main()
