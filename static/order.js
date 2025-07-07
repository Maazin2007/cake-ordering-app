// getting the list of the buttons to adjust the color based on the status
var buttons = document.querySelectorAll(".status-buttons")

// looping over the node list 
buttons.forEach(button => {

    const status = button.textContent.trim().toLowerCase();
    
    if (status === "baking") {
        button.style.backgroundColor = "#FFE58A";
        button.style.color = "#7A5901";
    } else if (status === "ready for pickup") {
        button.style.backgroundColor = "#A0E7E5";
        button.style.color = "#055E57";
    } else if (status === "collected") {
        button.style.backgroundColor = "#C3FBD8";
        button.style.color = "#1E5631";
    }
});


