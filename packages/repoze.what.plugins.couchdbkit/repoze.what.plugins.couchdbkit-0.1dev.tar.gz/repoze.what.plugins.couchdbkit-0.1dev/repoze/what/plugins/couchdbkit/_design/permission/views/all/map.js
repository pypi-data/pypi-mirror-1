function(doc) { 
   if (doc.doc_type == "Permission") 
    emit(doc._id, doc); 
}

