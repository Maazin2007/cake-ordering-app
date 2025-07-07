// declaring variables 
var cart = null;

// creating a GET request to the server to get the intial cart
async function getCart() {
    try {
        const response = await fetch("/get-cart");

        if(!response.ok) {
            console.error("there was a server side error")

            const errorData = await response.json();
            console.log(errorData.error);

            return {};
        }
        
        const data = await response.json();
        return data;
    }
    catch(error){
        console.error("there is a error parsing the JSON or recieving it");
        return {};
    }

}

// declaring all the variables
// selection all the buttons in the class quantity holder and the total div
const buttons = document.querySelectorAll(".quantity-holder button");
var subtotal = document.getElementById("subtotal");
var tax = document.getElementById("tax");
var total = document.getElementById("total");
const removeButtons = document.querySelectorAll(".remove-holder button")

// calling the GET request function and assigning the return value to cart
getCart()
        .then(data => {
                cart = data;
                // looping over the node list of buttons
                buttons.forEach(button => {
                    // adding event listener to the buttons
                    button.addEventListener('click', () => {
                        // extracting the id of the item using string slicing
                        let id = button.id;
                        let product_id = id.slice(4);

                        // checking if it is a add or subtract button
                        if(button.classList.contains("add-button")) {
                            // increasing amount in the cart by 1
                            cart[product_id].amount += 1;
                        } else if(button.classList.contains("subtract-button")) {
                            // decreasing amount in the cart by 1
                            cart[product_id].amount -= 1;
                        }

                        // checking if the amount decreases to 0 
                        if(cart[product_id].amount == 0){
                            // deleting the row from the cart HTML
                            deleteItem(product_id);
                            // deleting the id key from the cart object
                            delete cart[product_id];
                            // updating the cart in the backend
                            updateCart(cart);
                        } else {
                            // update quantity
                            updateQuantity(cart[product_id].amount, product_id);
                            // update the backend
                            updateCart(cart); 
                        }

                        updateTotal(cart);

                        if(Object.keys(cart).length == 0) {
                            document.querySelector(".item-container").style.display = "none";
                            document.querySelector(".total-container").style.display = "none";
                            document.getElementById("empty-heading").style.display = "flex";
                            document.getElementById("empty-heading").style.fontSize = "3rem";
                        }
                    });
                });

                // node list of remove buttons
                removeButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        let id = button.id;
                        let product_id = id.slice(7);

                        deleteItem(product_id);
                        delete cart[product_id];
                        updateCart(cart);
                        updateTotal(cart);

                        if(Object.keys(cart).length == 0) {
                            document.querySelector(".item-container").style.display = "none";
                            document.querySelector(".total-container").style.display = "none";
                            document.getElementById("empty-heading").style.display = "flex";
                            document.getElementById("empty-heading").style.fontSize = "3rem";
                        }
                    });
                });
        });


// helper functions 
function updateQuantity(amount, id) {
    document.getElementById("quantity-value-" + id).innerHTML = `${amount}`;
}

// function to delete item row
function deleteItem(item_id) {
    document.getElementById("row-"+item_id).remove();
}

// function to send POST request to the server to update the cart in the backend
function updateCart(cart_copy) {
    fetch("/update-cart", {
        method: 'POST',
        headers: {
            'Content-Type':'application/json'
        },
        body: JSON.stringify(cart_copy)
    });
}

// function to change the total division
function updateTotal(cart_copy) {
    // pointing cart variable to the original cart
    let cart = cart_copy;
    let sum_array = [];
    let subtotal_value = 0;
    let tax_value = 0;
    let total_value = 0;
    // dictionary deconstruction
    for(let key in cart) {
        let {amount:amount_f, price:price_f} = cart[key];
        sum_array.push(amount_f * price_f);
    }

    // looping over array and storing the sum of all the values
    sum_array.forEach(value => {
        subtotal_value += value;
    });

    // getting the tax and the rest of the varibles
    tax_value = 0.15 * subtotal_value;
    total_value = subtotal_value + tax_value;

    // now changing the HTML code
    subtotal.innerHTML = `${subtotal_value.toFixed(1)}`;
    tax.innerHTML = `${tax_value.toFixed(1)}`;
    total.innerHTML = `${total_value.toFixed(1)}`;
}
// end of helper functions 