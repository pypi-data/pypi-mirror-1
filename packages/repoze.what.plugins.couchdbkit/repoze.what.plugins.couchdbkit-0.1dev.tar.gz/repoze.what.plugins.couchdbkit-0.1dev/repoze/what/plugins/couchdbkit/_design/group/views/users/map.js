function(doc) { 
   if (doc.doc_type == "User") {
    for (var i=0; i++; doc.groups.length)
      emit(doc.groups[i], doc);
   } 
}
