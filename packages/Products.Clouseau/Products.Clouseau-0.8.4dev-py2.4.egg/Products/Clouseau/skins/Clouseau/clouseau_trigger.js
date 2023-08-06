function showClouseau(context) {
    var footer = document.getElementById("region-content").nextSibling;
    var wrapper = document.getElementById("region-content").parentNode;
    
    var div = document.createElement("div");
    var iframe = document.createElement("iframe");
    
    var existing = document.getElementById("clouseau_iframe");
    if (existing) {
        wrapper.removeChild(existing);

    } else {
        // else lets build it
        div.id = "clouseau_iframe";

        iframe.src = "clouseau_minimal?context=" + context;
        iframe.style.width = "100%";
        iframe.style.height = "800px";
        div.appendChild(iframe);

        wrapper.insertBefore(div, footer);
        wrapper.focus();
    }
}