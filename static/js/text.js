sc.text = {
    
}

if (document.getElementById('text')) {
    sc.text.uid = window.location.pathname.split('/').slice(-1)[0];
    sc.text.acro = sc.util.uidToAcro(sc.text.uid);
}
