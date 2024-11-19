import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from streamlit_elements import elements, mui, html, sync

def app():
    st.set_page_config(layout="wide")
    st.title("Insights")

    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Overview", "Insights", "Actions"],
            icons=["house", "graph-up-arrow", "gear"],
            menu_icon="cast",
            default_index=1,
        )

    if selected == "Overview":
        st.header("Overview")
        st.write("Welcome to the Overview page.")
    elif selected == "Insights":
        # Top bar
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.selectbox("Insight Type", ["Payment term recommendation"], key="insight_type")
        with col2:
            st.selectbox("Show all", ["Show all"], key="show_all_1")
        with col3:
            st.selectbox("Status", ["Status"], key="show_all_2")

        # Main content
        col_left, col_middle, col_right = st.columns([1, 2, 1])

        with col_left:
            st.subheader("99 insights")
            suppliers = [
                {"Supplier": "Frode Laursen", "PTR": "PTR-63", "Value (M)": 1.5},
                {"Supplier": "Baldwin Richardson Foods", "PTR": "PTR-471", "Value (M)": 1.4},
                {"Supplier": "Infusetter Dairy", "PTR": "PTR-457", "Value (M)": 1.4},
                {"Supplier": "Moeller Trucking", "PTR": "PTR-664", "Value (M)": 1.4},
                {"Supplier": "HSBC", "PTR": "PTR-625", "Value (M)": 1.3},
                {"Supplier": "Newbury Investments", "PTR": "PTR-237", "Value (M)": 1.3},
                {"Supplier": "Proagro", "PTR": "PTR-10", "Value (M)": 1.2},
                {"Supplier": "Segata", "PTR": "PTR-17", "Value (M)": 1.2},
                {"Supplier": "Bigas Energie", "PTR": "PTR-41", "Value (M)": 1.1},
                {"Supplier": "United Natural Foods", "PTR": "PTR-351", "Value (M)": 1.1},
                {"Supplier": "Provinord", "PTR": "PTR-45", "Value (M)": 1.0},
                {"Supplier": "OMD Worldwide", "PTR": "PTR-342", "Value (M)": 1.0},
                {"Supplier": "CH Robinson", "PTR": "PTR-392", "Value (M)": 1.0}
            ]
            df_suppliers = pd.DataFrame(suppliers)
            df_suppliers.reset_index(drop=True, inplace=True)
            st.dataframe(df_suppliers)

        with col_middle:
            st.subheader("Provinord")
            st.write("Payment term recommendation (EUR)")
            st.write("1.0M")
            st.write("AI-recommended payment terms for Provinord is Net 45 days based on Sievo community data.")
            st.write(
                "This is 14 days better than the current, spend-weighted average payment term of 31 days for Provinord.")
            st.write("Negotiate payment terms to 45 days for all spend to secure 1.0M EUR working capital savings.")
            # st.title("Provinord Insights")
            # Details table
            st.subheader("Details")
            details = {
                "Total insight value": "1.0M",
                "Spend (EUR)": "25.2M",
                "Supplier": "Provinord",
                "Recommended payment term": "Net 45 days",
                "Time range": "07/2023 - 06/2024",
                "Country analysis": "Supplier 360 >"
            }

            with st.container():
                for key, value in details.items():
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.write(f"<div style='border:1px solid #ddd; padding: 10px;'>{key}</div>",
                                 unsafe_allow_html=True)
                    with col2:
                        st.write(f"<div style='border:1px solid #ddd; padding: 10px;'>{value}</div>",
                                 unsafe_allow_html=True)
            st.write("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

            # Maintain the state of the analytics section visibility
            if not hasattr(st.session_state, 'show_analytics'):
                st.session_state.show_analytics = False

            if st.button("Show analytics" if not st.session_state.show_analytics else "Hide analytics"):
                st.session_state.show_analytics = not st.session_state.show_analytics

            # Collapsible analytics section
            if st.session_state.show_analytics:
                with elements("analytics_section"):
                    with mui.Paper():
                        with mui.Grid({"container": True, "spacing": 3}):
                            # Charts
                            with mui.Grid({"item": True, "xs": 6}):
                                st.subheader("Spend by payment terms (EUR)")
                                fig1, ax1 = plt.subplots()
                                df_suppliers.plot(kind='bar', x='Supplier', y='Value (M)', ax=ax1, legend=False)
                                ax1.set_title("Spend by Payment Terms")
                                ax1.set_xlabel("Supplier")
                                ax1.set_ylabel("Value (M)")
                                st.pyplot(fig1)
                            with mui.Grid({"item": True, "xs": 6}):
                                st.subheader("Spend development by payment terms (EUR)")
                                fig2, ax2 = plt.subplots()
                                df_suppliers.plot(kind='pie', y='Value (M)', labels=df_suppliers['Supplier'].values, ax=ax2, legend=False)
                                ax2.set_title("Spend Development by Payment Terms")
                                ax2.set_ylabel("")
                                st.pyplot(fig2)

                            st.subheader("Working capital opportunity details")
                            # Add table here using streamlit's table feature
                            working_capital_data = pd.DataFrame({
                                "Category": ["Total insight value", "Spend (EUR)", "Supplier",
                                             "Recommended payment term", "Time range", "Country analysis"],
                                "Details": ["1.0M", "25.2M", "Provinord", "Net 45 days", "07/2023 - 06/2024",
                                            "Supplier 360 >"]
                            })
                            st.table(working_capital_data)

        with col_right:
            st.subheader("Assignee")
            st.selectbox("", ["Unassigned"], key="assignee")

            st.subheader("Status")
            st.selectbox("", ["Open"], key="status")

            st.subheader("Actions")
            st.button("Launch negobot")
            st.button("Create initiative")
            st.button("Contact supplier")

    elif selected == "Actions":
        st.header("Actions")
        st.write("Here you can manage actions related to the insights.")

if __name__ == "__main__":
    app()
