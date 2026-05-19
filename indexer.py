# ============================================================
# ΕΙΣΑΓΩΓΗ ΒΙΒΛΙΟΘΗΚΩΝ
# ============================================================

# Κάνουμε import την κλάση Elasticsearch
# Η κλάση αυτή μας επιτρέπει να συνδεθούμε με τον Elasticsearch server
# και να εκτελούμε εντολές (create index, insert, delete κ.λπ.)
from elasticsearch import Elasticsearch, helpers

# Κάνουμε import τη βιβλιοθήκη pandas
# Θα τη χρησιμοποιήσουμε για να διαβάσουμε το CSV αρχείο
# και να επεξεργαστούμε τα δεδομένα γραμμή-γραμμή
import pandas as pd


# ============================================================
# ΟΡΙΣΜΟΣ ΚΛΑΣΗΣ INDEXER
# ============================================================

# Η κλάση Indexer είναι υπεύθυνη για:
# - δημιουργία index στον Elasticsearch
# - εισαγωγή δεδομένων από CSV αρχείο
# - διαγραφή ενός ή πολλών posts
class Indexer:


    # --------------------------------------------------------
    # CONSTRUCTOR (ΑΡΧΙΚΟΠΟΙΗΣΗ ΚΛΑΣΗΣ)
    # --------------------------------------------------------
    def __init__(self, index_name="trash"):

        # Αποθηκεύουμε το όνομα του index
        # Αυτό το όνομα θα χρησιμοποιείται σε όλες τις αναζητήσεις
        self.index_name = index_name

        # Δημιουργούμε σύνδεση με τον Elasticsearch server
        # Ο server υποθέτουμε ότι τρέχει τοπικά στη θύρα 9200
        self.es = Elasticsearch("http://localhost:9200")


    # --------------------------------------------------------
    # ΔΗΜΙΟΥΡΓΙΑ INDEX
    # --------------------------------------------------------
    def create_index(self):

        # Πρώτα ελέγχουμε αν το index υπάρχει ήδη
        # Αυτό αποτρέπει σφάλμα αν προσπαθήσουμε να το ξαναδημιουργήσουμε
        if self.es.indices.exists(index=self.index_name):
            print(f"[INFO] Index '{self.index_name}' υπάρχει ήδη.")
            return

        # ----------------------------------------------------
        # ΟΡΙΣΜΟΣ MAPPING
        # ----------------------------------------------------
        # Το mapping καθορίζει:
        # - ποια πεδία θα έχει το index
        # - τι τύπο δεδομένων έχει κάθε πεδίο
        mapping = {
            "mappings": {
                "properties": {

                    # ------------------------------------------------
                    # ΚΕΙΜΕΝΙΚΑ ΠΕΔΙΑ
                    # ------------------------------------------------

                    # Το καθαρισμένο κείμενο του post
                    # Τύπος text → κατάλληλο για full-text search
                    "text_clean": {"type": "text"},

                    # Καθαρισμένο πεδίο τοποθεσίας / link name
                    "location_clean": {"type": "text"},

                    # Τύπος post (status, link κ.λπ.)
                    "type_clean": {"type": "text"},

                    # Καθαρισμένο link
                    "link_clean": {"type": "text"},

                    # ------------------------------------------------
                    # ΠΕΔΙΟ ΗΜΕΡΟΜΗΝΙΑΣ
                    # ------------------------------------------------
                    "date_clean": {
                        # Τύπος date για χρονικές αναζητήσεις
                        "type": "date",

                        # Αν η ημερομηνία είναι λάθος, δεν απορρίπτεται
                        "ignore_malformed": True,

                        # Αν είναι null, αποθηκεύεται ως None
                        "null_value": None
                    },

                    # ------------------------------------------------
                    # ΑΡΙΘΜΗΤΙΚΑ ΠΕΔΙΑ (METRICS)
                    # ------------------------------------------------

                    # Συνολικές αντιδράσεις
                    "reactions_num": {"type": "integer"},

                    # Αριθμός σχολίων
                    "comments_num": {"type": "integer"},

                    # Αριθμός κοινοποιήσεων
                    "shares_num": {"type": "integer"},

                    # Αναλυτικά reactions
                    "likes_num": {"type": "integer"},
                    "loves_num": {"type": "integer"},
                    "wows_num": {"type": "integer"},
                    "hahas_num": {"type": "integer"},
                    "sads_num": {"type": "integer"},
                    "angrys_num": {"type": "integer"}
                }
            }
        }

        # ----------------------------------------------------
        # ΔΗΜΙΟΥΡΓΙΑ INDEX ΣΤΟΝ ELASTICSEARCH
        # ----------------------------------------------------

        # Δημιουργούμε το index χρησιμοποιώντας το mapping
        self.es.indices.create(index=self.index_name, body=mapping)

        # Εμφανίζουμε μήνυμα επιτυχίας
        print("[OK] Δημιουργήθηκε το index.")


    # --------------------------------------------------------
    # ΕΙΣΑΓΩΓΗ ΔΕΔΟΜΕΝΩΝ ΑΠΟ CSV
    # --------------------------------------------------------
    def insert_csv(self, csv_path):

        # Διαβάζουμε το CSV αρχείο και το φορτώνουμε σε DataFrame
        df = pd.read_csv(csv_path)

        # Αντικαθιστούμε όλες τις NaN τιμές με κενό string
        # Αυτό είναι σημαντικό για να μην υπάρξουν σφάλματα
        # κατά τη μετατροπή και εισαγωγή στον Elasticsearch
        df = df.fillna("")

        # Δημιουργούμε μία λίστα ενεργειών (actions)
        # Θα χρησιμοποιηθεί για bulk εισαγωγή
        actions = []

        # Διατρέχουμε κάθε γραμμή του DataFrame
        for _, row in df.iterrows():

            # Παίρνουμε την τιμή της ημερομηνίας
            date_val = row["date_clean"]

            # Αν η ημερομηνία είναι κενό string
            # τη μετατρέπουμε σε None
            if isinstance(date_val, str) and date_val.strip() == "":
                date_val = None

            # ------------------------------------------------
            # ΔΗΜΙΟΥΡΓΙΑ DOCUMENT
            # ------------------------------------------------
            # Κάθε document αντιστοιχεί σε ένα post
            actions.append({

                # Ορίζουμε σε ποιο index θα μπει
                "_index": self.index_name,

                # Το περιεχόμενο του document
                "_source": {

                    # Κείμενο post
                    "text_clean": row["text_clean"],

                    # Κειμενικά metadata
                    "location_clean": row["location_clean"],
                    "type_clean": row["type_clean"],
                    "link_clean": row["link_clean"],

                    # Ημερομηνία δημοσίευσης
                    "date_clean": date_val,

                    # Αριθμητικά πεδία
                    "reactions_num": int(row["reactions_num"]),
                    "comments_num": int(row["comments_num"]),
                    "shares_num": int(row["shares_num"]),
                    "likes_num": int(row["likes_num"]),
                    "loves_num": int(row["loves_num"]),
                    "wows_num": int(row["wows_num"]),
                    "hahas_num": int(row["hahas_num"]),
                    "sads_num": int(row["sads_num"]),
                    "angrys_num": int(row["angrys_num"])
                }
            })

        # ----------------------------------------------------
        # BULK ΕΙΣΑΓΩΓΗ
        # ----------------------------------------------------

        # Εκτελούμε bulk εισαγωγή στον Elasticsearch
        # Είναι πολύ πιο αποδοτική από εισαγωγή ένα-ένα
        helpers.bulk(self.es, actions)

        # Εμφανίζουμε πόσα posts εισήχθησαν
        print(f"[OK] Εισήχθησαν {len(actions)} posts.")

        # Επιστρέφουμε τον αριθμό των εισαγόμενων posts
        return len(actions)


    # --------------------------------------------------------
    # ΔΙΑΓΡΑΦΗ ΕΝΟΣ POST
    # --------------------------------------------------------
    def delete_post(self, post_id):

        try:
            # Διαγράφουμε το post με βάση το μοναδικό id του
            self.es.delete(index=self.index_name, id=post_id)

            # Μήνυμα επιτυχίας
            print(f"[OK] Διαγράφηκε post {post_id}")

        except:
            # Αν το post δεν βρεθεί ή υπάρξει σφάλμα
            print("[WARN] Δεν βρέθηκε post.")


    # --------------------------------------------------------
    # ΔΙΑΓΡΑΦΗ ΠΟΛΛΩΝ POSTS
    # --------------------------------------------------------
    def delete_posts_bulk(self, ids):

        # Δημιουργούμε λίστα ενεργειών διαγραφής
        # Κάθε στοιχείο της λίστας είναι μία delete εντολή
        actions = [
            {
                "_op_type": "delete",     # Τύπος ενέργειας: delete
                "_index": self.index_name,
                "_id": _id                # id του post προς διαγραφή
            }
            for _id in ids
        ]

        # Εκτελούμε bulk διαγραφή
        helpers.bulk(self.es, actions)

        # Εμφανίζουμε μήνυμα επιτυχίας
        print(f"[OK] Διαγράφηκαν {len(ids)} posts.")