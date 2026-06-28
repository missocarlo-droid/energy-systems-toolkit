import os
from docx import Document
from docxcompose.composer import Composer
from docx2pdf import convert


# Cartella con i file Word generati
input_folder = "Word_filled_contracts"
output_file = "ALL_CONTRACTS_MERGED.docx"

# Elenco dei file .docx (ordinati)
files = sorted([f for f in os.listdir(input_folder) if f.endswith(".docx")], key=str.casefold)

if not files:
    print("❌ Nessun file .docx trovato nella cartella.")
else:
    # Usa il primo file come base
    first_doc = Document(os.path.join(input_folder, files[0]))
    composer = Composer(first_doc)

    # Aggiungi gli altri documenti
    for filename in files[1:]:
        doc_path = os.path.join(input_folder, filename)
        print(f"Unisco: {filename}")
        doc = Document(doc_path)
        #doc.add_page_break()
        composer.append(doc)
    # Salva il documento unificato
    composer.save(output_file)
    print(f"\n✅ File unificato creato correttamente: {output_file}")

    # Convert in PDF
    try:
        pdf_output_file = output_file.replace(".docx", ".pdf")
        convert(output_file, pdf_output_file)
        print(f"✅ File PDF creato correttamente: {pdf_output_file}")
    except ImportError:
        print("⚠️ La conversione in PDF richiede il pacchetto 'docx2pdf'. Installalo per abilitare questa funzionalità.")
    
    # delete the merged docx file to keep only the pdf
    os.remove(output_file)
    print(f"✅ File temporaneo .docx eliminato: {output_file}")
    # deletae the input filled word files to keep only the pdf
    for filename in files:
        doc_path = os.path.join(input_folder, filename)
        os.remove(doc_path)
    print(f"✅ File temporanei nella cartella '{input_folder}' eliminati.")
        
