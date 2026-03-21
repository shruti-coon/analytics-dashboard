import pandas as pd
import plotly.express as px
import streamlit as st
import time

st.set_page_config(
    page_title='Consoleflare Analytics Portal',
    page_icon='📈'
)

st.sidebar.title("Navigation")
option = st.sidebar.radio("Go to", [
    "Upload Data",
    "Overview",
    "Cleaning",
    "Visualization",
    "Insights"
])

st.title(':rainbow[Data Analytics Portal]')
st.subheader(':gray[Explore Data with ease.]', divider='rainbow')

file = st.file_uploader('Drop csv or excel file', type=['csv', 'xlsx'])

if file is not None:
    with st.spinner('Loading data...'):
        time.sleep(1)

    # Load data
    if file.name.endswith('csv'):
        data = pd.read_csv(file)
    else:
        data = pd.read_excel(file)

    # ✅ SESSION STATE (important)
    if "data" not in st.session_state:
        st.session_state.data = data

    data = st.session_state.data

    st.dataframe(data)
    st.success('File uploaded successfully 🚀')

    # ================= OVERVIEW =================
    if option == "Overview":
        st.subheader(':rainbow[Basic information of the dataset]', divider='rainbow')

        tab1, tab2, tab3, tab4 = st.tabs(['Summary', 'Top/Bottom', 'Data Types', 'Columns'])

        with tab1:
            st.write(f'Rows: {data.shape[0]}, Columns: {data.shape[1]}')
            st.dataframe(data.describe())

        with tab2:
            rows = st.slider('Rows', 1, data.shape[0])
            st.dataframe(data.head(rows))

        with tab3:
            st.dataframe(data.dtypes)

        with tab4:
            st.write(list(data.columns))

    # ================= CLEANING =================
    numeric_cols = data.select_dtypes(include='number').columns

    col = st.selectbox('Select column', data.columns)
    method = st.selectbox('Method', ['Mean','Median','Mode'])

    if st.button('Apply'):
      if method in ['Mean', 'Median'] and col not in numeric_cols:
        st.error("❌ Mean/Median only works on numeric columns!")
      else:
        if method == 'Mean':
            st.session_state.data[col].fillna(data[col].mean(), inplace=True)
        elif method == 'Median':
            st.session_state.data[col].fillna(data[col].median(), inplace=True)
        else:
            st.session_state.data[col].fillna(data[col].mode()[0], inplace=True)

        st.success('Cleaning Applied ✅')
    # ================= VISUALIZATION =================
    elif option == "Visualization":
        st.subheader('Visualization')

        # Heatmap
        if st.checkbox('Show Heatmap'):
            corr = data.corr(numeric_only=True)
            fig = px.imshow(corr, text_auto=True)
            st.plotly_chart(fig)

        # Filter
        st.subheader('Filter Data')
        col = st.selectbox('Column', data.columns, key='filter_col')
        val = st.text_input('Value')

        if val:
            filtered = data[data[col].astype(str).str.contains(val)]
            st.dataframe(filtered)

        # Groupby
        st.subheader('Groupby')
        gcols = st.multiselect('Group columns', data.columns)
        op_col = st.selectbox('Operation column', data.columns, key='op_col')
        op = st.selectbox('Operation', ['sum', 'max', 'min', 'count'])

        if gcols:
            try:
                result = data.groupby(gcols).agg({op_col: op}).reset_index()
                st.dataframe(result)
            except Exception as e:
             st.error("❌ Invalid operation for selected column")

        # ✅ Charts (FIXED)
        st.subheader('Charts')

        chart_type = st.selectbox('Chart Type', ['Scatter', 'Bar', 'Line', 'Histogram'])
        x = st.selectbox('X-axis', data.columns)

        numeric_cols = data.select_dtypes(include='number').columns

        fig = None  # ✅ prevent undefined error

        if chart_type != 'Histogram':
            y = st.selectbox('Y-axis', data.columns)

            if y not in numeric_cols:
              st.error("❌ Y-axis must be numeric for this chart")
            else:
               if chart_type == 'Scatter':
                   fig = px.scatter(data, x=x, y=y)
               elif chart_type == 'Bar':
                   fig = px.bar(data, x=x, y=y)
               elif chart_type == 'Line':
                   fig = px.line(data, x=x, y=y)

        else:
            fig = px.histogram(data, x=x)

# Only plot if figure exists
        if fig is not None:
           st.plotly_chart(fig)

    # ================= INSIGHTS =================
    elif option == "Insights":
        st.subheader('Insights')

        if st.button('Generate Insights'):
            st.write("Rows:", data.shape[0])
            st.write("Columns:", data.shape[1])

            st.write("### Missing Values")
            st.write(data.isnull().sum())

            st.write("### Correlation")
            corr = data.corr(numeric_only=True)
            st.dataframe(corr)

        # ✅ Smart Insights
        if st.button('Smart Insights'):
            numeric_cols = data.select_dtypes(include='number').columns

            for col in numeric_cols:
                st.write(f"📊 {col}")
                st.write(f"Mean: {data[col].mean():.2f}")
                st.write(f"Max: {data[col].max()}")
                st.write(f"Min: {data[col].min()}")
                st.write("---")

    # ================= DOWNLOAD =================
    st.subheader('Download')
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "data.csv", "text/csv")

else:
    st.info("Please upload a file to get started.")

st.caption("Built by Shruti 🚀")