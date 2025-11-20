import streamlit as st
from pages.rag_step_4_vector_db import get_db_collection

st.title("🗃️ Vector Database Management")
    
with st.expander("📖 About this page"):
    st.write("""
        **View and manage your uploaded files in the vector database:**
        
        - **See all files** you've added and their chunks
        - **Delete entire files** - removes all chunks from that file
        - **See database statistics**
        
        *Files are automatically chunked and embedded when you upload them in the 'Add Documents' page.*
        """)
collection = get_db_collection()
total_count = collection.count()

if collection:

 if total_count == 0:
    st.info("📭 Database is empty. Please add documents first using the 'Add Documents' page.")
 else:
    st.success(f"✅ Database connected: {total_count} total chunks found")

    # Get all data from collection
    all_data = collection.get(
        include=["documents", "metadatas"],
        limit=total_count
    )

    if not all_data['documents']:
        st.info("📭 No documents found in the database.")

    files_chunks = {}
    for metadata, document in zip(all_data['metadatas'], all_data['documents']):
        source = metadata.get('source', 'Unknown')
        if source not in files_chunks:
            files_chunks[source] = []
        
        files_chunks[source].append({
            'content': document,
            'metadata': metadata,
            'doc_id': metadata.get('doc_id', 'N/A'),
            'chunk_id': metadata.get('chunk_id', 'N/A')
        })

    # Display files and their chunks
    st.header("📁 Files in Database")

    for file_name, chunks in files_chunks.items():
    # Sort chunks by chunk_id for better organization
        chunks.sort(key=lambda x: x['chunk_id'])
        
        with st.expander(f"📄 {file_name} - {len(chunks)} chunks", expanded=False):
            
            # File summary
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**Total chunks:** {len(chunks)}")
            with col2:
                # Calculate average chunk length
                avg_length = sum(len(chunk['content']) for chunk in chunks) / len(chunks)
                st.write(f"**Avg chunk size:** {avg_length:.0f} chars")
            with col3:
                # Delete button for this file
                if st.button("🗑️ Delete File", key=f"delete_{file_name}"):
                    # Delete all chunks from this file using where filter
                    collection.delete(where={"source": file_name})
                    st.success(f"✅ Deleted {len(chunks)} chunks from {file_name}")
                    st.rerun() #to rerun the page and the updated DB appear
            

    # File Details Table
    
    file_data = []
    for file_name, chunks in files_chunks.items():
        total_chars = sum(len(chunk['content']) for chunk in chunks)
        avg_length = total_chars / len(chunks)
        file_data.append({
            'File Name': file_name,
            'Chunks': len(chunks),
            'Total Characters': total_chars,
            'Avg Chunk Size': f"{avg_length:.0f} chars"
        })
    
    if file_data:
        st.subheader("📋 File Details")
        st.dataframe(file_data)


    # Database Statistics
    st.header("📊 Database Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", len(files_chunks))
    with col2:
        st.metric("Total Chunks", total_count)
    with col3:
        avg_chunks = total_count / len(files_chunks) if files_chunks else 0
        st.metric("Avg Chunks/File", f"{avg_chunks:.1f}")
    with col4:
        # Calculate total characters stored
        total_chars = sum(len(chunk['content']) for chunks in files_chunks.values() for chunk in chunks)
        st.metric("Total Characters", f"{total_chars:,}")
            

