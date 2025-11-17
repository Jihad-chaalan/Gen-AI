import streamlit as st
from pages.step_1_loading import load_documents_from_streamlit_files
from pages.rag_step_2_chunking import chunk_documents
from pages.rag_step_3_embeddings import embed_texts
from pages.rag_step_4_vector_db import get_db_collection

uploaded_files = st.file_uploader(
    "Choose documents",
    type=['txt', 'pdf', 'docx', 'csv', 'xlsx', 'json'],
    accept_multiple_files=True,
    help="You can upload multiple files at once"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")

    #step 1: load existing files
    source_list = load_documents_from_streamlit_files(uploaded_files)


    #step2: chunk the contents
    my_chunks_with_metadata = chunk_documents(source_list)
    st.success(f"✂️ Step 2: Created {len(my_chunks_with_metadata)} chunks from documents")


    #prepare data for storage

    ids_list = [f"chunk_{i}" for i in range(len(my_chunks_with_metadata))]
    text_list = []
    metadata_list = []

    for chunk in my_chunks_with_metadata:
        text_list.append(chunk["text"])
        metadata_list.append({
            'source': chunk['source'],
            'doc_id': chunk['doc_id'],
            'chunk_id': chunk['chunk_id']
        })

    #step 3: generate embeddings
    vectors_list = embed_texts(text_list)
    st.success(f"🧮 Step 3: Generated embeddings for {len(vectors_list)} chunks")

    #step 4: store into vector_db
    my_rag_collection = get_db_collection()
    my_rag_collection.upsert(
            ids = ids_list,
            embeddings = vectors_list,
            documents = text_list,
            metadatas = metadata_list
        )
    
    st.session_state.rag_collection = my_rag_collection
    st.success(f"🗄️ Step 4: Successfully added {my_rag_collection.count()} chunks into vector database")

    st.subheader("📊 Processing Summary")
    col1, col2, col3, col4 = st.columns(4)
        
    with col1:
        st.metric("Original Files", len(uploaded_files))
    with col2:
        st.metric("Loaded Documents", len(source_list))
    with col3:
        st.metric("Text Chunks", len(my_chunks_with_metadata))
    with col4:
        st.metric("Vector DB Entries", my_rag_collection.count())