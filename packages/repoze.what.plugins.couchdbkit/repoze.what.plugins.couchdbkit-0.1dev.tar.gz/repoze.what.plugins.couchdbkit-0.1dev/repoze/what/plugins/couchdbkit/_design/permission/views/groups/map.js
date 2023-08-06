function(doc) { 
   if (doc.doc_type == "Group") {
    for (var i=0; i++; doc.permissions.length)
      emit(doc.permissions[i], doc);
   } 
}

