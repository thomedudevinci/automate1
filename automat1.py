import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "Rapport Business Insights Automator+", ln=True, align="C")  # ✅ emoji supprimé
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def section_body(self, body):
        self.set_font("Arial", "", 11)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 8, body)
        self.ln(3)

    def add_section(self, title, body):
        self.section_title(title)
        self.section_body(body)



# Configuration
st.set_page_config(page_title="📊 Business Insights Automator+", layout="wide")
st.title("📊 Business Insights Automator+")
st.markdown("""
Optimise ton activité en quelques secondes grâce à notre assistant intelligent 👇

- Analyse automatique de tes ventes
- Diagnostic clair et recommandations
- Export PDF du rapport
""")

# Upload du fichier CSV
uploaded_file = st.file_uploader("📤 Téléverse ton fichier CSV (Stripe, Shopify, etc.)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("🗂️ Aperçu des données")
    st.dataframe(df[["Date","Product","Amount"]].head())

    # Détection des colonnes
    date_col = next((col for col in df.columns if "date" in col.lower()), None)
    amount_col = next((col for col in df.columns if "amount" in col.lower() or "total" in col.lower()), None)
    product_col = next((col for col in df.columns if "product" in col.lower() or "item" in col.lower() or "description" in col.lower()), None)

    if date_col and amount_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col, amount_col])
        df["Month"] = df[date_col].dt.to_period("M").astype(str)

        total_revenue = df[amount_col].sum()
        st.metric("💰 Chiffre d'affaires total", f"{total_revenue:,.2f} €")

        monthly = df.groupby("Month")[amount_col].sum().reset_index()
        st.subheader("📅 Revenus mensuels")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(monthly["Month"], monthly[amount_col], marker="o")
        ax.set_title("Revenus par mois")
        ax.set_xlabel("Mois")
        ax.set_ylabel("Chiffre d'affaires (€)")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Top produits
        if product_col:
            top_products = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False).head(5)
            st.subheader("🏆 Top produits")
            st.bar_chart(top_products)

        # Diagnostic intelligent (manuel)
        st.subheader("🧠 Diagnostic automatique")
        last_month_value = monthly[amount_col].iloc[-1]
        avg_revenue = monthly[amount_col].mean()
        if last_month_value < avg_revenue:
            st.warning("📉 Tes ventes du dernier mois sont en baisse par rapport à ta moyenne.")
        else:
            st.success("📈 Tes ventes sont supérieures à la moyenne !")

        st.markdown("""**📌 Recommandation :** \n Pour booster ton chiffre d'affaires, relance ton produit phare en proposant une offre spéciale ou un pack promotionnel.\n
Pense aussi à diversifier ton catalogue avec des services complémentaires qui répondent aux besoins de tes clients actuels.\n
Enfin, automatise le suivi de tes clients pour augmenter leur fidélité et leur panier moyen.

""")
        

        # Génération du rapport PDF
        # Génération du PDF
        pdf = PDF()
        pdf.add_page()

        # Section : Résumé
        pdf.add_section("Résumé général", f"""
        Chiffre d'affaires total : {total_revenue:,.2f} EUR
        Nombre de ventes : {len(df)}
        Période couverte : {df[date_col].min().date()} à {df[date_col].max().date()}

        """)

        # Section : Top produits
        if product_col:
            top_str = "\n".join(
                [f"- {prod}: {val:,.2f} EUR" for prod, val in top_products.items()]
            )
            pdf.add_section("Produits les plus rentables", top_str)
        else:
            pdf.add_section("Produits", "Aucune colonne produit détectée.")

        # Section : Revenus mensuels
        monthly_lines = "\n".join([
            f"- {row['Month']}: {row[amount_col]:,.2f} EUR"
            for _, row in monthly.iterrows()
        ])
        pdf.add_section("Revenus mensuels", monthly_lines)

        # Section : Recommandation
        recommendation = """
        Nous te recommandons de relancer tes meilleures offres avec un message fort ou un pack combiné.
        Pense également à identifier les mois les plus faibles pour tester des campagnes ciblées.
        Enfin, mets en avant ton produit phare ou crée une offre complémentaire.
        """
        pdf.add_section("Diagnostic & Recommandations", recommendation)

        # Export en mémoire
        buffer = BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin1')  # Convertit le contenu PDF en bytes
        buffer.write(pdf_output)
        buffer.seek(0)

        st.download_button("📥 Télécharger le rapport PDF", buffer.getvalue(), file_name="rapport_automator.pdf", mime="application/pdf")
    else:
        st.error("Impossible de détecter les colonnes 'date' et 'montant'. Vérifie ton fichier.")
