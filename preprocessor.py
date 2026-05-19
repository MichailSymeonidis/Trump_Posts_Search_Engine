# ============================================================
# ΕΙΣΑΓΩΓΗ ΒΙΒΛΙΟΘΗΚΩΝ
# ============================================================

# Κάνουμε import τη βιβλιοθήκη pandas
# Η pandas χρησιμοποιείται για να διαβάζουμε CSV αρχεία
# και να δουλεύουμε με πίνακες δεδομένων (DataFrames)
import pandas as pd

# Κάνουμε import τη βιβλιοθήκη numpy
# Η numpy χρησιμοποιείται για αριθμητικές πράξεις
# (σε αυτό το αρχείο δεν χρησιμοποιείται έντονα,
# αλλά συχνά συνδυάζεται με την pandas)
import numpy as np

# Κάνουμε import τη βιβλιοθήκη re
# Η re μας επιτρέπει να χρησιμοποιούμε κανονικές εκφράσεις (regex)
# Θα τη χρησιμοποιήσουμε για καθαρισμό κειμένου
import re

# Κάνουμε import τη datetime
# Χρησιμοποιείται για τη διαχείριση ημερομηνιών
from datetime import datetime


# ============================================================
# ΟΡΙΣΜΟΣ ΚΛΑΣΗΣ PREPROCESSOR
# ============================================================

# Η κλάση Preprocessor είναι υπεύθυνη για όλο το preprocessing
# Δηλαδή:
# - καθαρισμό κειμένου
# - καθαρισμό ημερομηνιών
# - μετατροπή αρχικών δεδομένων σε μορφή κατάλληλη για Elasticsearch
class Preprocessor:


    # --------------------------------------------------------
    # ΜΕΘΟΔΟΣ ΚΑΘΑΡΙΣΜΟΥ ΚΕΙΜΕΝΟΥ
    # --------------------------------------------------------
    def clean_text(self, text):

        # Ελέγχουμε αν το text είναι NaN (δηλαδή κενή τιμή στο CSV)
        # Αν είναι NaN, επιστρέφουμε κενό string
        if pd.isna(text):
            return ""

        # Μετατρέπουμε το text σε string
        # και όλα τα γράμματα σε πεζά
        # Αυτό βοηθά ώστε η αναζήτηση να μην επηρεάζεται
        # από κεφαλαία / πεζά γράμματα
        text = str(text).lower()

        # Αφαιρούμε σημεία στίξης και ειδικούς χαρακτήρες
        # [^\w\s] σημαίνει: οτιδήποτε ΔΕΝ είναι γράμμα, αριθμός ή κενό
        # Τα αντικαθιστούμε με κενό
        text = re.sub(r"[^\w\s]", " ", text)

        # Αν υπάρχουν πολλά συνεχόμενα κενά,
        # τα αντικαθιστούμε με ένα μόνο κενό
        text = re.sub(r"\s+", " ", text)

        # Αφαιρούμε κενά από την αρχή και το τέλος του κειμένου
        return text.strip()


    # --------------------------------------------------------
    # ΜΕΘΟΔΟΣ ΚΑΘΑΡΙΣΜΟΥ ΗΜΕΡΟΜΗΝΙΑΣ
    # --------------------------------------------------------
    def clean_date(self, date_val):

        # Αν η ημερομηνία είναι NaN ή κενή
        # τότε επιστρέφουμε None
        if pd.isna(date_val) or date_val == "":
            return None

        try:
            # Προσπαθούμε να μετατρέψουμε την ημερομηνία
            # από ISO μορφή (string) σε datetime αντικείμενο
            return datetime.fromisoformat(date_val)

        except:
            # Αν αποτύχει η μετατροπή (λάθος format),
            # επιστρέφουμε None για να μη σπάσει το πρόγραμμα
            return None


    # --------------------------------------------------------
    # ΠΡΟΕΠΕΞΕΡΓΑΣΙΑ ΟΛΟΚΛΗΡΟΥ DATAFRAME
    # --------------------------------------------------------
    def preprocess_dataframe(self, df):

        # Δημιουργούμε αντίγραφο του DataFrame
        # ώστε να μην αλλοιώσουμε το αρχικό
        df = df.copy()

        # ----------------------------------------------------
        # ΚΑΘΑΡΙΣΜΟΣ ΚΕΙΜΕΝΙΚΩΝ ΠΕΔΙΩΝ
        # ----------------------------------------------------

        # Παίρνουμε το status_message από το αρχικό CSV
        # και δημιουργούμε το text_clean
        df["text_clean"] = df["status_message"].apply(self.clean_text)

        # Καθαρίζουμε το πεδίο link_name
        # Αν έχει NaN, το αντικαθιστούμε με κενό string
        df["location_clean"] = df["link_name"].fillna("").astype(str)

        # Καθαρίζουμε τον τύπο του post
        df["type_clean"] = df["status_type"].fillna("").astype(str)

        # Καθαρίζουμε το link του post
        df["link_clean"] = df["status_link"].fillna("").astype(str)

        # Καθαρίζουμε την ημερομηνία δημοσίευσης
        df["date_clean"] = df["status_published"].apply(self.clean_date)

        # ----------------------------------------------------
        # ΚΑΘΑΡΙΣΜΟΣ ΑΡΙΘΜΗΤΙΚΩΝ ΠΕΔΙΩΝ
        # ----------------------------------------------------

        # Συνολικός αριθμός reactions
        # Αν είναι NaN, γίνεται 0 και μετατρέπεται σε int
        df["reactions_num"] = df["num_reactions"].fillna(0).astype(int)

        # Αριθμός σχολίων
        df["comments_num"] = df["num_comments"].fillna(0).astype(int)

        # Αριθμός κοινοποιήσεων
        df["shares_num"] = df["num_shares"].fillna(0).astype(int)

        # Αναλυτικά reactions (likes, loves, κ.λπ.)
        df["likes_num"] = df["num_likes"].fillna(0).astype(int)
        df["loves_num"] = df["num_loves"].fillna(0).astype(int)
        df["wows_num"] = df["num_wows"].fillna(0).astype(int)
        df["hahas_num"] = df["num_hahas"].fillna(0).astype(int)
        df["sads_num"] = df["num_sads"].fillna(0).astype(int)
        df["angrys_num"] = df["num_angrys"].fillna(0).astype(int)

        # Επιστρέφουμε το πλήρως καθαρισμένο DataFrame
        return df


    # --------------------------------------------------------
    # ΠΡΟΕΠΕΞΕΡΓΑΣΙΑ CSV ΑΡΧΕΙΟΥ
    # --------------------------------------------------------
    def process_csv(self, csv_path):

        # Διαβάζουμε το αρχικό CSV αρχείο
        df = pd.read_csv(csv_path)

        # Καλούμε τη preprocess_dataframe
        # για να καθαρίσουμε όλα τα δεδομένα
        df_clean = self.preprocess_dataframe(df)

        # Αποθηκεύουμε το καθαρό DataFrame σε νέο CSV αρχείο
        # index=False σημαίνει ότι δεν αποθηκεύεται το index της pandas
        df_clean.to_csv("clean_posts.csv", index=False)

        # Επιστρέφουμε το όνομα του νέου CSV αρχείου
        return "clean_posts.csv"