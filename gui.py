# ============================================================
# ΕΙΣΑΓΩΓΗ ΒΙΒΛΙΟΘΗΚΩΝ
# ============================================================

# Εισάγουμε τη βασική βιβλιοθήκη tkinter
# Χρησιμοποιείται για τη δημιουργία παραθύρων, κουμπιών, labels κ.λπ.
import tkinter as tk

# Εισάγουμε επιπλέον εργαλεία από το tkinter:
# ttk → πιο σύγχρονα widgets (tabs)
# filedialog → παράθυρο επιλογής αρχείων
# messagebox → αναδυόμενα μηνύματα (error, warning κ.λπ.)
from tkinter import ttk, filedialog, messagebox

# Εισάγουμε τη βιβλιοθήκη csv
# Χρησιμοποιείται για αποθήκευση αποτελεσμάτων σε CSV αρχείο
import csv

# Εισάγουμε τη βιβλιοθήκη re (regular expressions)
# Θα τη χρησιμοποιήσουμε για highlighting λέξεων στο snippet
import re

# Εισάγουμε τις κλάσεις του συστήματος
# Preprocessor → καθαρισμός CSV
# Indexer → δημιουργία index & εισαγωγή δεδομένων
# Searcher → αναζητήσεις
from preprocessor import Preprocessor
from indexer import Indexer
from searcher import Searcher


# ============================================================
# ΒΟΗΘΗΤΙΚΗ ΣΥΝΑΡΤΗΣΗ – SNIPPET
# ============================================================

# Η συνάρτηση αυτή δημιουργεί ένα μικρό απόσπασμα (snippet)
# από το πλήρες κείμενο, γύρω από λέξεις-κλειδιά
def make_snippet(full_text, keywords, max_words=25):

    # Χωρίζουμε το πλήρες κείμενο σε λίστα λέξεων
    words = full_text.split()

    # Αν δεν υπάρχουν λέξεις (κενό κείμενο)
    # επιστρέφουμε κενό string
    if not words:
        return ""

    # Δημιουργούμε κενή λίστα για τις θέσεις των keywords
    positions = []

    # Για κάθε λέξη-κλειδί που ψάχνουμε
    for key in keywords:
        # Διατρέχουμε όλες τις λέξεις του κειμένου
        for i, w in enumerate(words):
            # Αν η λέξη-κλειδί υπάρχει μέσα στη λέξη (χωρίς διάκριση πεζών)
            if key.lower() in w.lower():
                # Αποθηκεύουμε τη θέση της
                positions.append(i)

    # Αν δεν βρέθηκε καμία λέξη-κλειδί
    # επιστρέφουμε τις πρώτες max_words λέξεις
    if not positions:
        return " ".join(words[:max_words])

    # Παίρνουμε τη θέση της πρώτης εμφάνισης keyword
    center = positions[0]

    # Υπολογίζουμε την αρχή του snippet
    start = max(0, center - max_words // 2)

    # Υπολογίζουμε το τέλος του snippet
    end = min(len(words), start + max_words)

    # Επιστρέφουμε το snippet ως string
    return " ".join(words[start:end])


# ============================================================
# ΚΥΡΙΑ ΚΛΑΣΗ GUI
# ============================================================

# Ορίζουμε την κλάση TrashGUI
# Είναι υπεύθυνη για ΟΛΟ το γραφικό περιβάλλον
class TrashGUI:

    # Constructor της κλάσης
    def __init__(self, root):

        # Αποθηκεύουμε το βασικό παράθυρο της εφαρμογής
        self.root = root

        # Ορίζουμε τον τίτλο του παραθύρου
        self.root.title("TrASH – Trump Automated Search Hub")

        # Ορίζουμε το αρχικό μέγεθος του παραθύρου
        self.root.geometry("1300x850")

        # ----------------------------------------------------
        # ΧΡΩΜΑΤΙΚΗ ΠΑΛΕΤΑ (DARK THEME)
        # ----------------------------------------------------

        # Χρώμα φόντου εφαρμογής
        self.bg_main = "#2e3440"

        # Εναλλακτικό χρώμα φόντου
        self.bg_alt = "#3b4252"

        # Χρώμα widgets (entry, text κ.λπ.)
        self.bg_widget = "#3b4252"

        # Χρώμα κειμένου
        self.fg_text = "#eceff4"

        # Χρώμα έμφασης
        self.accent = "#88c0d0"

        # Χρώμα highlighting
        self.highlight_color = "#ebcb8b"

        # ----------------------------------------------------
        # ΔΗΜΙΟΥΡΓΙΑ CORE ΑΝΤΙΚΕΙΜΕΝΩΝ
        # ----------------------------------------------------

        # Δημιουργούμε αντικείμενο Preprocessor
        self.prep = Preprocessor()

        # Δημιουργούμε αντικείμενο Indexer
        self.indexer = Indexer()

        # Δημιουργούμε αντικείμενο Searcher
        self.searcher = Searcher()

        # ----------------------------------------------------
        # ΜΕΤΑΒΛΗΤΕΣ ΚΑΤΑΣΤΑΣΗΣ
        # ----------------------------------------------------

        # Αποθηκεύει το όνομα του καθαρού CSV
        self.clean_csv = None

        # Αποθηκεύει τα τελευταία αποτελέσματα αναζήτησης
        self.last_results = []

        # Αποθηκεύει τις τελευταίες λέξεις-κλειδιά
        self.last_keywords = []

        # Αποθηκεύει τύπο τελευταίας αναζήτησης
        self.last_query_type = None

        # Αποθηκεύει την τιμή τελευταίας αναζήτησης
        self.last_query_value = None

        # ----------------------------------------------------
        # ΛΙΣΤΕΣ WIDGETS (για dark theme)
        # ----------------------------------------------------

        self.frames = []
        self.labels = []
        self.buttons = []
        self.entries = []
        self.texts = []
        self.listboxes = []

        # Δημιουργούμε το γραφικό περιβάλλον
        self.build_ui()

        # Εφαρμόζουμε το dark theme
        self.apply_dark_theme()

    # ========================================================
    # ΔΗΜΙΟΥΡΓΙΑ ΤΟΥ ΚΥΡΙΟΥ UI ΚΑΙ ΤΩΝ TABS
    # ========================================================
    def build_ui(self):

        # Δημιουργούμε αντικείμενο Style της ttk
        # Χρησιμοποιείται για εμφάνιση των tabs
        style = ttk.Style()

        # Επιλέγουμε το theme "clam"
        # Είναι πιο ουδέτερο και συνεργάζεται καλά με dark themes
        style.theme_use("clam")

        # Δημιουργούμε Notebook (tabs container)
        notebook = ttk.Notebook(self.root)

        # Τοποθετούμε το notebook στο παράθυρο
        # fill="both" → πιάνει όλο τον χώρο
        # expand=True → προσαρμόζεται όταν αλλάζει μέγεθος το παράθυρο
        notebook.pack(fill="both", expand=True)

        # ----------------------------------------------------
        # ΔΗΜΙΟΥΡΓΙΑ ΤΩΝ TABS
        # ----------------------------------------------------

        # Tab για preprocessing
        self.tab_pre = tk.Frame(notebook)

        # Tab για index
        self.tab_index = tk.Frame(notebook)

        # Tab για search
        self.tab_search = tk.Frame(notebook)

        # Tab για results
        self.tab_results = tk.Frame(notebook)

        # Προσθέτουμε τα tabs στο notebook
        notebook.add(self.tab_pre, text="1. Preprocess")
        notebook.add(self.tab_index, text="2. Index")
        notebook.add(self.tab_search, text="3. Search")
        notebook.add(self.tab_results, text="4. Results")

        # Αποθηκεύουμε τα tabs στη λίστα frames
        # για μελλοντική αλλαγή χρωμάτων (dark theme)
        self.frames.extend([
            self.tab_pre,
            self.tab_index,
            self.tab_search,
            self.tab_results
        ])

        # Χτίζουμε το περιεχόμενο κάθε tab
        self.build_tab_preprocess()
        self.build_tab_index()
        self.build_tab_search()
        self.build_tab_results()

    # ========================================================
    # TAB 1: PREPROCESS
    # ========================================================
    def build_tab_preprocess(self):

        # Δημιουργούμε label με οδηγία προς τον χρήστη
        lbl = tk.Label(self.tab_pre, text="Επιλέξτε το CSV:")

        # Τοποθετούμε το label με απόσταση από πάνω
        lbl.pack(pady=15)

        # Αποθηκεύουμε το label στη λίστα
        self.labels.append(lbl)

        # Δημιουργούμε κουμπί για φόρτωση CSV
        btn = tk.Button(
            self.tab_pre,
            text="Load CSV",
            command=self.load_csv  # callback συνάρτηση
        )

        # Τοποθετούμε το κουμπί
        btn.pack()

        # Αποθηκεύουμε το κουμπί
        self.buttons.append(btn)

        # Label για εμφάνιση μηνυμάτων (status)
        self.lbl_pre = tk.Label(self.tab_pre, text="")

        # Τοποθετούμε το label
        self.lbl_pre.pack(pady=20)

        # Το αποθηκεύουμε για theme
        self.labels.append(self.lbl_pre)

    def load_csv(self):

        # Ανοίγουμε παράθυρο επιλογής αρχείου
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )

        # Αν ο χρήστης δεν επέλεξε αρχείο
        if not path:
            return

        try:
            # Καλούμε τον Preprocessor για καθαρισμό CSV
            self.clean_csv = self.prep.process_csv(path)

            # Εμφανίζουμε μήνυμα επιτυχίας
            self.lbl_pre.config(
                text=f"Cleaned file saved as: {self.clean_csv}"
            )

        except Exception as e:
            # Αν συμβεί οποιοδήποτε σφάλμα
            messagebox.showerror("Error", str(e))

    # ========================================================
    # TAB 2: INDEX
    # ========================================================
    def build_tab_index(self):

        # Label τίτλου
        lbl = tk.Label(self.tab_index, text="Index Operations")
        lbl.pack(pady=10)
        self.labels.append(lbl)

        # Κουμπί δημιουργίας index
        btn1 = tk.Button(
            self.tab_index,
            text="Create Index",
            command=self.create_index
        )
        btn1.pack(pady=5)
        self.buttons.append(btn1)

        # Κουμπί εισαγωγής CSV
        btn2 = tk.Button(
            self.tab_index,
            text="Insert Clean CSV",
            command=self.insert_posts
        )
        btn2.pack(pady=5)
        self.buttons.append(btn2)

        # Label για μηνύματα
        self.lbl_index = tk.Label(self.tab_index, text="")
        self.lbl_index.pack(pady=20)
        self.labels.append(self.lbl_index)

    def create_index(self):

        # Δημιουργούμε index μέσω Indexer
        self.indexer.create_index()

        # Ενημερώνουμε το UI
        self.lbl_index.config(text="Index created")


    def insert_posts(self):

        # Αν δεν έχει γίνει preprocess
        if not self.clean_csv:
            messagebox.showwarning(
                "Warning",
                "Preprocess CSV first."
            )
            return

        # Εισάγουμε τα posts
        count = self.indexer.insert_csv(self.clean_csv)

        # Ενημερώνουμε το UI
        self.lbl_index.config(text=f"Inserted {count} posts")

    # ========================================================
    # TAB 3: SEARCH
    # ========================================================
    def build_tab_search(self):

        # Δημιουργούμε frame για ομαδοποίηση widgets
        frame = tk.Frame(self.tab_search)
        frame.pack(pady=20)
        self.frames.append(frame)

        # ---------------- TOP-K ----------------
        tk.Label(frame, text="Top-K:").grid(row=0, column=0)

        self.k_entry = tk.Entry(frame, width=8)
        self.k_entry.insert(0, "10")  # default τιμή
        self.k_entry.grid(row=0, column=1)
        self.entries.append(self.k_entry)

        # ---------------- BOOLEAN ----------------
        tk.Label(frame, text="Boolean Query:").grid(row=1, column=0)

        self.boolean_entry = tk.Entry(frame, width=50)
        self.boolean_entry.grid(row=1, column=1)
        self.entries.append(self.boolean_entry)

        tk.Button(
            frame,
            text="Search",
            command=self.run_boolean
        ).grid(row=1, column=2)

        # ---------------- PHRASE ----------------
        tk.Label(frame, text="Phrase Query:").grid(row=2, column=0)

        self.phrase_entry = tk.Entry(frame, width=50)
        self.phrase_entry.grid(row=2, column=1)
        self.entries.append(self.phrase_entry)

        tk.Button(
            frame,
            text="Search",
            command=self.run_phrase
        ).grid(row=2, column=2)

        # ---------------- NUMERIC SEARCH ----------------
        # Label για numeric φίλτρο (likes)
        tk.Label(frame, text="likes_num ≥").grid(row=3, column=0)

        # Entry για αριθμητική τιμή
        self.numeric_entry = tk.Entry(frame, width=20)
        self.numeric_entry.grid(row=3, column=1)

        # Αποθηκεύουμε το entry για αλλαγή theme
        self.entries.append(self.numeric_entry)

        # Κουμπί αναζήτησης numeric query
        tk.Button(
            frame,
            text="Search",
            command=self.run_numeric
        ).grid(row=3, column=2)

        # ---------------- SIMILARITY SEARCH ----------------
        # Label για similarity αναζήτηση
        tk.Label(frame, text="Similarity post_id:").grid(row=4, column=0)

        # Entry για id post
        self.sim_entry = tk.Entry(frame, width=20)
        self.sim_entry.grid(row=4, column=1)

        # Αποθηκεύουμε το entry
        self.entries.append(self.sim_entry)

        # Κουμπί αναζήτησης similarity
        tk.Button(
            frame,
            text="Search",
            command=self.run_similarity
        ).grid(row=4, column=2)

    # ========================================================
    # TAB 4: RESULTS
    # ========================================================
    def build_tab_results(self):

        # Δημιουργούμε βασικό container frame
        container = tk.Frame(self.tab_results)

        # Τοποθετούμε το frame σε όλο τον διαθέσιμο χώρο
        container.pack(fill="both", expand=True)

        # Το αποθηκεύουμε για theme
        self.frames.append(container)

        # ---------------- ΑΡΙΣΤΕΡΟ ΜΕΡΟΣ ----------------
        # Frame για τη λίστα αποτελεσμάτων
        left = tk.Frame(container)
        left.pack(side="left", fill="y")
        self.frames.append(left)

        # Listbox που εμφανίζει τα αποτελέσματα
        self.result_list = tk.Listbox(left, width=60, height=30)
        self.result_list.pack()

        # Το αποθηκεύουμε για αλλαγή theme
        self.listboxes.append(self.result_list)

        # Όταν ο χρήστης επιλέξει στοιχείο
        # καλείται η show_full_post
        self.result_list.bind(
            "<<ListboxSelect>>",
            self.show_full_post
        )

        # ---------------- ΔΕΞΙΟ ΜΕΡΟΣ ----------------
        # Frame για snippet & πλήρες post
        right = tk.Frame(container)
        right.pack(side="left", fill="both", expand=True)
        self.frames.append(right)

        # Text box για snippet
        self.snippet_box = tk.Text(right, height=8)
        self.snippet_box.pack(fill="x")

        # Αποθήκευση για theme
        self.texts.append(self.snippet_box)

        # Ορίζουμε tag για highlighting λέξεων
        self.snippet_box.tag_config(
            "highlight",
            background=self.highlight_color,
            foreground="black"
        )

        # Text box για πλήρη εμφάνιση post
        self.full_box = tk.Text(right, height=18)
        self.full_box.pack(fill="both", expand=True)

        # Αποθήκευση για theme
        self.texts.append(self.full_box)
    # ========================================================
    # DARK THEME
    # ========================================================
    def apply_dark_theme(self):

        # Ορίζουμε το φόντο του βασικού παραθύρου
        self.root.configure(bg=self.bg_main)

        # Εφαρμόζουμε background σε όλα τα frames
        for w in self.frames:
            w.configure(bg=self.bg_main)

        # Εφαρμόζουμε χρώματα στα labels
        for w in self.labels:
            w.configure(bg=self.bg_main, fg=self.fg_text)

        # Εφαρμόζουμε χρώματα στα κουμπιά
        for w in self.buttons:
            w.configure(bg=self.bg_alt, fg=self.fg_text)

        # Εφαρμόζουμε χρώματα στα entry
        for w in self.entries:
            w.configure(bg=self.bg_widget, fg=self.fg_text)

        # Εφαρμόζουμε χρώματα στα text boxes
        for w in self.texts:
            w.configure(bg=self.bg_widget, fg=self.fg_text)

        # Εφαρμόζουμε χρώματα στα listboxes
        for w in self.listboxes:
            w.configure(bg=self.bg_widget, fg=self.fg_text)

    # Παίρνουμε την τιμή Top-K από το entry
    def get_k(self):
        try:
            # Προσπαθούμε να μετατρέψουμε την τιμή σε int
            return int(self.k_entry.get())
        except:
            # Αν αποτύχει, επιστρέφουμε προεπιλογή
            return 10


    # Εξαγωγή λέξεων-κλειδιών από boolean query
    def extract_keywords(self, q):

        # Αφαιρούμε τους λογικούς τελεστές
        q = q.replace("AND", " ").replace("OR", " ").replace("NOT", " ")

        # Διαχωρίζουμε τις λέξεις και τις επιστρέφουμε σε πεζά
        return [w.lower() for w in q.split() if w.strip()]

    # Boolean αναζήτηση
    def run_boolean(self):

        # Παίρνουμε το query από το entry
        q = self.boolean_entry.get().strip()

        # Αν είναι κενό, σταματάμε
        if not q:
            return

        # Εξάγουμε λέξεις-κλειδιά
        keywords = self.extract_keywords(q)

        # Εκτελούμε την αναζήτηση
        hits = self.searcher.boolean_query(q)[:self.get_k()]

        # Εμφανίζουμε τα αποτελέσματα
        self.display_results(hits, keywords)


    # Phrase αναζήτηση
    def run_phrase(self):

        q = self.phrase_entry.get().strip()
        if not q:
            return

        hits = self.searcher.phrase_query(q)[:self.get_k()]
        self.display_results(hits, [q.lower()])


    # Numeric αναζήτηση
    def run_numeric(self):

        try:
            value = int(self.numeric_entry.get())
        except:
            return

        hits = self.searcher.numeric_query(
            "likes_num",
            value
        )[:self.get_k()]

        self.display_results(hits, [])


    # Similarity αναζήτηση
    def run_similarity(self):

        pid = self.sim_entry.get().strip()
        if not pid:
            return

        hits = self.searcher.similarity_search(
            pid,
            self.get_k()
        )

        self.display_results(hits, [])

    # Εμφάνιση αποτελεσμάτων στη λίστα
    def display_results(self, hits, keywords):

        # Αποθηκεύουμε τα αποτελέσματα
        self.last_results = hits

        # Αποθηκεύουμε τα keywords
        self.last_keywords = keywords

        # Καθαρίζουμε παλιά αποτελέσματα
        self.result_list.delete(0, tk.END)
        self.snippet_box.delete("1.0", tk.END)
        self.full_box.delete("1.0", tk.END)

        # Για κάθε αποτέλεσμα
        for h in hits:
            # Εμφανίζουμε score και αρχή κειμένου
            self.result_list.insert(
                tk.END,
                f"[{h['_score']:.2f}] {h['_source']['text_clean'][:80]}"
            )

    # Όταν επιλεγεί αποτέλεσμα από τη λίστα
    def show_full_post(self, event):

        # Παίρνουμε την επιλογή
        sel = self.result_list.curselection()

        # Αν δεν υπάρχει επιλογή
        if not sel:
            return

        # Παίρνουμε το αντίστοιχο αποτέλεσμα
        hit = self.last_results[sel[0]]

        # Παίρνουμε το περιεχόμενο
        src = hit["_source"]

        # Καθαρίζουμε το πλήρες text box
        self.full_box.delete("1.0", tk.END)

        # Εμφανίζουμε όλα τα πεδία του post
        for k, v in src.items():
            self.full_box.insert(tk.END, f"{k}: {v}\n")

        # Δημιουργούμε snippet
        snippet = make_snippet(
            src["text_clean"],
            self.last_keywords
        )

        # Καθαρίζουμε το snippet box
        self.snippet_box.delete("1.0", tk.END)

        # Εμφανίζουμε το snippet
        self.snippet_box.insert("1.0", snippet)

        # Highlight λέξεων-κλειδιών
        for key in self.last_keywords:
            for m in re.finditer(key, snippet, re.IGNORECASE):
                self.snippet_box.tag_add(
                    "highlight",
                    f"1.{m.start()}",
                    f"1.{m.end()}"
                )

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # Δημιουργούμε το βασικό παράθυρο
    root = tk.Tk()

    # Δημιουργούμε το GUI αντικείμενο
    app = TrashGUI(root)

    # Ξεκινάμε το event loop
    root.mainloop()