function(doc) { 
   if (doc.doc_type == "Permission") 
    emit(doc.name, doc); 
}

