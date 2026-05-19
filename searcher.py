# Κάνουμε import την κλάση Elasticsearch από τη βιβλιοθήκη elasticsearch
# Η κλάση αυτή μας επιτρέπει να στέλνουμε queries στον Elasticsearch server
from elasticsearch import Elasticsearch


# -------------------------------------------------------
# Ορισμός της κλάσης Searcher
# -------------------------------------------------------
# Η κλάση Searcher συγκεντρώνει όλες τις λειτουργίες αναζήτησης
# ώστε να υπάρχει διαχωρισμός μεταξύ:
# - GUI (διεπαφή χρήστη)
# - Indexer (εισαγωγή δεδομένων)
# - Searcher (αναζητήσεις)
class Searcher:


    # ---------------------------------------------------
    # Constructor (μέθοδος αρχικοποίησης)
    # ---------------------------------------------------
    def __init__(self, index_name="trash"):

        # Δημιουργούμε σύνδεση με τον Elasticsearch server
        # Ο server τρέχει τοπικά στη διεύθυνση http://localhost:9200
        self.es = Elasticsearch("http://localhost:9200")

        # Αποθηκεύουμε το όνομα του index που θα χρησιμοποιούμε
        # Από προεπιλογή είναι το "trash"
        self.index_name = index_name

        # Εκτυπώνουμε ενημερωτικό μήνυμα για debugging
        print("[INFO] Searcher: Συνδεθήκαμε στο Elasticsearch.")


    # ---------------------------------------------------
    # 1. BOOLEAN QUERY
    # ---------------------------------------------------
    # Η μέθοδος αυτή υλοποιεί Boolean αναζήτηση
    # Δηλαδή αναζήτηση με AND, OR, NOT
    def boolean_query(self, query_string):

        # Δημιουργούμε το query σε μορφή dictionary (JSON)
        # Χρησιμοποιούμε query_string query του Elasticsearch
        query = {

            # Το βασικό μέρος του query
            "query": {

                # query_string επιτρέπει λογικούς τελεστές
                "query_string": {

                    # Το query που έδωσε ο χρήστης (π.χ. "hillary AND email")
                    "query": query_string,

                    # Ορίζουμε ότι η αναζήτηση γίνεται στο πεδίο text_clean
                    "default_field": "text_clean"
                }
            }
        }

        # Στέλνουμε το query στον Elasticsearch
        # index: το index στο οποίο ψάχνουμε
        # body: το query που ορίσαμε παραπάνω
        res = self.es.search(index=self.index_name, body=query)

        # Από το αποτέλεσμα επιστρέφουμε μόνο τα hits
        # Τα hits είναι η λίστα με τα έγγραφα που βρέθηκαν
        return res["hits"]["hits"]


    # ---------------------------------------------------
    # 2. PHRASE QUERY
    # ---------------------------------------------------
    # Η μέθοδος αυτή αναζητά ακριβή φράση μέσα στο κείμενο
    def phrase_query(self, phrase, slop=0):

        # Δημιουργούμε match_phrase query
        # Το match_phrase ψάχνει ακριβή σειρά λέξεων
        query = {

            "query": {

                "match_phrase": {

                    # Το πεδίο στο οποίο γίνεται η αναζήτηση
                    "text_clean": {

                        # Η φράση που ψάχνουμε
                        "query": phrase,

                        # Το slop ορίζει πόσες λέξεις μπορούν να παρεμβληθούν
                        # slop=0 σημαίνει ακριβής φράση
                        "slop": slop
                    }
                }
            }
        }

        # Εκτελούμε το query στον Elasticsearch
        res = self.es.search(index=self.index_name, body=query)

        # Επιστρέφουμε τα αποτελέσματα της αναζήτησης
        return res["hits"]["hits"]


    # ---------------------------------------------------
    # 3. NUMERIC QUERY
    # ---------------------------------------------------
    # Η μέθοδος αυτή υλοποιεί αριθμητικό φίλτρο
    # π.χ. likes_num >= 500000
    def numeric_query(self, field_name, minimum_value=0):

        # Δημιουργούμε range query
        # Χρησιμοποιείται για αριθμητικά πεδία
        query = {

            "query": {

                "range": {

                    # Το όνομα του αριθμητικού πεδίου
                    field_name: {

                        # gte = greater than or equal (>=)
                        "gte": minimum_value
                    }
                }
            }
        }

        # Εκτελούμε το query
        res = self.es.search(index=self.index_name, body=query)

        # Επιστρέφουμε τα αποτελέσματα
        return res["hits"]["hits"]


    # ---------------------------------------------------
    # 4. DATE RANGE QUERY
    # ---------------------------------------------------
    # Η μέθοδος αυτή αναζητά posts μετά από συγκεκριμένη ημερομηνία
    def date_query_after(self, iso_date):

        # Δημιουργούμε range query για πεδίο ημερομηνίας
        query = {

            "query": {

                "range": {

                    # Το πεδίο ημερομηνίας στο index
                    "date_clean": {

                        # gte = μεγαλύτερο ή ίσο από την ημερομηνία
                        "gte": iso_date
                    }
                }
            }
        }

        # Εκτελούμε το query
        res = self.es.search(index=self.index_name, body=query)

        # Επιστρέφουμε τα αποτελέσματα
        return res["hits"]["hits"]


    # ---------------------------------------------------
    # 5. SIMILARITY SEARCH (TOP-K)
    # ---------------------------------------------------
    # Η μέθοδος αυτή βρίσκει posts παρόμοια με ένα συγκεκριμένο post
    def similarity_search(self, post_id, top_k=10):

        # Δημιουργούμε query τύπου more_like_this
        # Ο Elasticsearch συγκρίνει το περιεχόμενο των κειμένων
        query = {

            "query": {

                "more_like_this": {

                    # Το πεδίο που χρησιμοποιείται για σύγκριση
                    "fields": ["text_clean"],

                    # Το post με το οποίο θα συγκριθούν τα υπόλοιπα
                    "like": [

                        {
                            # Το index στο οποίο βρίσκεται το post
                            "_index": self.index_name,

                            # Το id του post αναφοράς
                            "_id": post_id
                        }
                    ],

                    # Ελάχιστη συχνότητα όρου στο έγγραφο
                    "min_term_freq": 1,

                    # Ελάχιστη συχνότητα όρου στο σύνολο των εγγράφων
                    "min_doc_freq": 1
                }
            },

            # Ορίζουμε πόσα αποτελέσματα θέλουμε να επιστραφούν
            "size": top_k
        }

        # Εκτελούμε το query
        res = self.es.search(index=self.index_name, body=query)

        # Επιστρέφουμε τα αποτελέσματα
        return res["hits"]["hits"]