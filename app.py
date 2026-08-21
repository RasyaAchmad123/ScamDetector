import streamlit as st
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
from dataset import dataset

# =========================
# CONFIGURATION
# =========================

st.set_page_config(
    page_title="Scam Detector",
    page_icon="🛡️"
)

# =========================
# SCAM RULES
# =========================

rules = {
    "🔐 Meminta OTP / password / PIN": {"keywords": ["otp", "password", "pin", "kode verifikasi"], "score": 3},
    "🎁 Menawarkan hadiah / uang": {"keywords": ["hadiah", "menang", "gratis", "bonus", "jutaan", "juta"], "score": 2},
    "🔗 Mengandung link": {"keywords": ["http://", "https://", "bit.ly", "tinyurl", "link"], "score": 2},
    "⏰ Memberikan tekanan waktu": {"keywords": ["sekarang", "segera", "hari ini", "10 menit", "cepat"], "score": 1},
    "💳 Meminta pembayaran / transfer": {"keywords": ["transfer", "bayar", "deposit", "kirim uang"], "score": 2},
}

def predict(text):
    text = text.lower()
    total_score = 0
    detected = []
    for rule_name, rule_data in rules.items():
        for kw in rule_data["keywords"]:
            if kw in text:
                total_score += rule_data["score"]
                detected.append((rule_name, rule_data["score"]))
                break
    return total_score, detected

def label_from_score(score):
    return "Scam" if score >= 3 else "Legit"

# =========================
# TABS
# =========================

tab1, tab2 = st.tabs(["🔍 Cek Pesan", "📊 Metodologi & Evaluasi"])

# =========================
# TAB 1 - SCAM CHECKER
# =========================

with tab1:
    st.title("🛡️ Scam Detector")
    st.write("Cek pesan mencurigakan sebelum kamu klik atau memberikan informasi pribadi.")

    message = st.text_area(
        "📩 Masukkan pesan yang ingin diperiksa:",
        height=200,
        placeholder="Contoh: Selamat! Anda mendapatkan hadiah..."
    )

    if st.button("🔍 CHECK MESSAGE"):
        if not message.strip():
            st.warning("⚠️ Silakan masukkan pesan terlebih dahulu.")
        else:
            total_score, detected_rules = predict(message)

            if total_score >= 6:
                risk_level = "🔴 HIGH RISK"
                risk_message = "Pesan memiliki beberapa ciri yang perlu diwaspadai."
            elif total_score >= 3:
                risk_level = "🟡 MEDIUM RISK"
                risk_message = "Pesan memiliki beberapa ciri mencurigakan."
            else:
                risk_level = "🟢 LOW RISK"
                risk_message = "Tidak banyak indikator scam yang terdeteksi."

            st.divider()
            st.subheader("Hasil Pemeriksaan")
            st.markdown(f"# {risk_level}")
            st.write(f"**Risk Score: {total_score}**")
            st.write(risk_message)

            if detected_rules:
                st.subheader("🚨 Indikator yang Terdeteksi")
                for rule_name, score in detected_rules:
                    st.write(f"⚠️ {rule_name} **(+{score})**")
            else:
                st.success("Tidak ada indikator scam yang terdeteksi.")

            st.subheader("💡 Rekomendasi")
            if total_score >= 6:
                st.error("Jangan klik link, jangan transfer uang, dan jangan berikan OTP/password. Verifikasi melalui sumber resmi.")
            elif total_score >= 3:
                st.warning("Jangan langsung percaya. Periksa identitas pengirim dan verifikasi informasi.")
            else:
                st.info("Tetap berhati-hati dan pastikan informasi berasal dari sumber resmi.")

# =========================
# TAB 2 - METODOLOGI & EVALUASI
# =========================

with tab2:
    st.title("📊 Metodologi & Evaluasi")
    st.write("Halaman ini menunjukkan bagaimana Scam Detector diuji terhadap dataset contoh pesan.")

    y_true = []
    y_pred = []
    rows = []

    for row in dataset:
        score, _ = predict(row["pesan"])
        pred_label = label_from_score(score)
        y_true.append(row["label"])
        y_pred.append(pred_label)
        rows.append({
            "Pesan": row["pesan"][:60] + "...",
            "Label Asli": row["label"],
            "Prediksi": pred_label,
            "Benar": row["label"] == pred_label
        })

    df_result = pd.DataFrame(rows)
    accuracy = (df_result["Benar"].sum() / len(df_result)) * 100

    st.metric("Akurasi pada Dataset Uji", f"{accuracy:.1f}%")

    st.subheader("Confusion Matrix")
    cm = confusion_matrix(y_true, y_pred, labels=["Scam", "Legit"])
    cm_df = pd.DataFrame(cm, index=["Actual Scam", "Actual Legit"], columns=["Pred Scam", "Pred Legit"])
    st.dataframe(cm_df)

    st.subheader("Classification Report")
    report = classification_report(y_true, y_pred, labels=["Scam", "Legit"], output_dict=True)
    st.dataframe(pd.DataFrame(report).transpose())

    st.subheader("Detail Hasil Prediksi")
    st.dataframe(df_result)

    st.caption(f"Dataset uji saat ini berisi {len(dataset)} pesan. Semakin banyak dan variatif datanya, semakin valid hasil evaluasinya.")