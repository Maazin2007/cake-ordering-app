// creating functions to help with the css of the page

// Get all elements with the class "status-buttons"
const status__Buttons = document.querySelectorAll(".status-button");

// Loop through each button and apply styling based on status
status__Buttons.forEach(button => {
    const status = button.textContent.trim().toLowerCase();

    switch (status) {
        case "baking":
            button.style.backgroundColor = "#FFE58A";  // light yellow
            button.style.color = "#7A5901";            // dark yellow text
            break;
        case "Ready":
            button.style.backgroundColor = "#A0E7E5";  // light blue
            button.style.color = "#055E57";            // dark teal
            break;
        case "Collected":
            button.style.backgroundColor = "#C3FBD8";  // light green
            button.style.color = "#1E5631";            // dark green
            break;
        default:
            button.style.backgroundColor = "#e0e0e0";  // neutral fallback
            button.style.color = "#333";
            break;
    }
});

// makign variables for both the eigthy variables
var currentOrders = document.getElementById("currentOrders");
var finance = document.getElementById("finance");
var oldOrders = document.getElementById("oldOrders");
var addItem = document.getElementById("addItem");

// set finance and rest of the pages to none 
finance.style.display = "none";
addItem.style.display = "none";
oldOrders.style.display = 'none';

// creating a function to make the current orders div go and the finance to come 
function changeDisplayOrders() {
    if (currentOrders.style.display == "none") {
        currentOrders.style.display = "flex";
        finance.style.display = "none";
        oldOrders.style.display = "none";
        addItem.style.display = "none";
    }
}

// creating function to change the display of the finance div
function changeDisplayFinance() {
    if (finance.style.display == "none") {
        finance.style.display = "flex";
        currentOrders.style.display = "none";
        oldOrders.style.display = "none";
        addItem.style.display = "none";
    }
}

function changeDisplayOldOrders() {
    if (oldOrders.style.display == "none") {
        oldOrders.style.display = "flex";
        finance.style.display = "none";
        currentOrders.style.display = "none";
        addItem.style.display = "none";
    }
}

function changeDisplaySearchItem() {
    if (addItem.style.display == "none") {
        addItem.style.display = "flex";
        finance.style.display = "none";
        currentOrders.style.display = "none";
        oldOrders.style.display = "none";
    }
}


// handling the API things and all the buttons

// getting node list of all the buttons in the page
const buttons = document.querySelectorAll(".maazin-button");
const status_selectors = document.getElementsByClassName("status-buttons");

// looping over each button
buttons.forEach(button => {
    // adding event listener to the buttons
    button.addEventListener('click', () => {
        // gettign user id and order id assocaited with the button
        const order_id = button.dataset.orderId;
        const user_id = button.dataset.userId;

        // changing status according to the class of the button
        if(button.classList.contains("button-ready")) {
            change_status("ready", user_id, order_id, button);
        } else if(button.classList.contains("button-collected")) {
            change_status("collected", user_id, order_id, button);
        }

    });
});


// function to send update request to server
async function change_status(status, user_id, order_id, button) {
    // trying async code
    try {
        // getting the response object from the function
        const data = await send_server_request(status, user_id, order_id);

        // displaying success message
        console.log(`Success - ${data.success}`);
        alert("successfully updated the cart");

        // chaning the text inside the button and the class of the button
        if (button.classList.contains("button-ready")) {

            button.textContent = "collected";
            button.classList.remove("button-ready");
            button.classList.add("button-collected");

        } else {

            button.textContent = "ready";
            button.classList.remove("button-collected");
            button.classList.add("button-ready");
        }

        // if the changed status is collected delete the element
        if (status == "collected") {
            // delete the entire order box
            let temp = `box-${order_id}`;
            box = document.getElementById(temp);
            box.remove()
        }

        // updating each status thing also client side
        for (let i = 0; i < status_selectors.length; i++) {
            if (status_selectors[i].dataset.orderId == order_id) {
                status_selectors[i].textContent = status;
            }
        }

    }
    catch(error){
        // displaying custom error message 
        console.error("error message: ", error.message);
        alert("error in updating the cart");
    } 
}

async function send_server_request(status, user_id, order_id) {

    // sending POST request to the server
    const response = await fetch('/update-order', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    'status': status,
                                    'user_id': user_id,
                                    'order_id': order_id
                                })
                            });

    // checking if the error values is not between 200 - 299
    if (!response.ok) {
        // getting the response object
        const errorObj = await response.json();
        // throwing custom error 
        throw new Error(`HTTP ERROR ${response.status}: ${errorObj.error} - ${errorObj.details}`);
    }

    // if error code is 200 return successfully object
    return await response.json();
}

// adding code for expense table




// selelcting all the remove expense buttons
remove_buttons = document.querySelectorAll(".remove-expense-button");

// iterating over each button 
remove_buttons.forEach(button => {
    // adding event listener to each button
    add_expense_event_listener(button);
});

// async function to execute the whole even listener code
function add_expense_event_listener(button) {
    
    // adding event listener to the button
    button.addEventListener('click', async (event) => {

        // extracting the data for the name of the expense
        const expense_name = button.dataset.expenseName;

        // trying some async code to update the expense in the backend
        try{
            // sending request to the server to update the expense in the backend
            const expense_response = await update_expense_backend(expense_name);

            // print the success message
            console.log(`SUCCESS: ${expense_response.success}, details: ${expense_response.details}`);

            // now we update the tab by deleting the div
            const cleanKey = expense_name.trim().replace(/\s+/g, '_').replace(/[^\w\-]/g, '');
            let element_id = `expense-div-${cleanKey}`;
            let remove_div = document.getElementById(element_id);
            
            if (remove_div) {
                remove_div.remove();
            } else {
                console.error(`Element with ID "${element_id}" not found`);
            }


            // handle the case were there are no more expenses left
            // check if no more expenses left
            if (expense_response.expense_status === 'false') {
                // creating a new div element 
                const newDiv = document.createElement("div");
                // add the css properties so that it looks nice
                newDiv.classList.add("error-div-class");
                // now we have to set its ID so we can access it latet
                newDiv.id = "empty-expense-div";
                // we also have to create child div to store the text
                const newDivText = document.createElement('div');
                newDivText.classList.add('data-holder-text');
                newDivText.innerHTML = "THERE ARE NO MORE EXPENSES LEFT";
                // now we have to append both the divs
                newDiv.append(newDivText);
                document.getElementById("expense-body").prepend(newDiv);  
            }

            // now we get a finance object from the backend to update the whole finance div
            const finance_response = await get_finance_object();

            // displaying the finance object for debugging
            console.log(finance_response);
            
            // now we update the finance div
            update_finance_div(finance_response);

            // end of try block 
            
         }
        catch(error){
            // printing the error message
            error_message = `ERROR: ${error.message}`;
            console.error(error_message);
        }
    });
}

// function to update backend 
async function update_expense_backend(name) {
    // function send POST request to the server and await response
    let response = await fetch('/api/update-expense', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "expense_name": name,
                "expense_amount": "none",
                "action": "delete",
            })
        });
    
    // check if the status is not in 200 - 299 range
    if (!response.ok) {
        const errorObj = await response.json();
        console.error(`ERROR: ${response.status}, ${errorObj.error}, ${errorObj.details}`);
        throw new Error("there was an issue while communicating with the backend");
    }

    // if status code is correct return the response object
    return await response.json()    
}

async function get_finance_object() {
    // send GET request to the backend and retrieve the code 
    const response = await fetch('/api/get-finance-object');

    // check if the status_code is between 200 and 299
    if (!response.ok) {
        errorObj = await response.json()
        console.error(`ERROR: ${response.status}, ${errorObj.error}, ${errorObj.details}`);
        throw new Error("there was an issue while communicating with the backend for the finance object");
    }

    // send object back the main function
    return await response.json()
}

function update_finance_div(data) {
    // select all the text divs we have to change
    const revenue_holder = document.getElementById("revenue-holder");
    const cost_holder = document.getElementById("cost-holder");
    const expense_holder = document.getElementById("expense-holder");
    const profit_holder = document.getElementById("profit-holder");
    const loss_holder = document.getElementById("loss-holder");
    const profit_div = document.getElementById("profit-div");
    const loss_div = document.getElementById("loss-div");
    const full_bar = document.getElementById("full-bar");
    const bars = document.querySelectorAll(".bar-item");
    const error_display = document.getElementById("error_display");
    const percentageProfit = document.getElementById("percentageProfit");
    const percentageLoss = document.getElementById("percentageLoss");
    const percentageProfitDiv = document.getElementById("percentageProfitDiv");
    const percentageLossDiv = document.getElementById("percentageLossDiv");

    // change the inner HTML of each span element
    revenue_holder.textContent = `${data.revenue}`;
    cost_holder.textContent = `${data.cost}`;
    expense_holder.textContent = `${data.expenses}`;

    // handle the case were the profit decreases below zero
    if ( data.profit_status === 'true') {
        // change the percentage profit
        percentageProfitDiv.style.display = 'flex';
        percentageLossDiv.style.display = 'none';
        percentageProfit.textContent = `${data.percentageProfit}`;

        // show the profit div and hide the loss div
        profit_div.style.display = 'flex';
        loss_div.style.display = 'none';

        // change the inner HTML
        profit_holder.textContent = `${data.profit}`;
        full_bar.style.display = 'flex';
        error_display.style.display = 'none';

        // change the bar
        bars.forEach(bar => {

            if (bar.style.backgroundColor == 'green') {
                bar.style.width = `${data.percentageProfit}%`;
            } else if (bar.style.backgroundColor == 'blue') {
                bar.style.width = `${data.costPercentage}%`;
            } else if (bar.style.backgroundColor == 'orange') {
                bar.style.width = `${data.expensesPercentage}%`;
            }

        });


    } else {
        // show the loss div and hide the profit div
        profit_div.style.display = 'none';
        loss_div.style.display = 'flex';
        full_bar.style.display = 'none';

        // change the inner HTML
        loss_holder.textContent = `${data.profit}`;
        error_display.style.display = 'flex';

        //change the percentage loss
        percentageLossDiv.style.display = 'flex';
        percentageProfitDiv.style.display = 'none';
        percentageLoss.textContent = `${data.percentageLoss}`;
    }
}

// handeling the adding of new expense

// now we need to handle the button to add new expenses
var expense_name = document.getElementById("expense_name");
var expense_amount = document.getElementById("expense_amount");

// select the error message display
const expenseErrorDisplay = document.getElementById("expense-error-holder");
const expenseErrorContent = document.getElementById("expense-holder-text");

// now select the the submit button and add event lsitener
const add_expense_button = document.getElementById("add-expense-button");

add_expense_button.addEventListener('click', async (event) => {

    if (!expenseErrorDisplay || !expenseErrorContent) {
        console.error("Missing #expense-error-holder or #expense-holder-text in the DOM.");
        return;
    }

    // check if the expense name is empty
    if (expense_name.value === "") {
        expenseErrorDisplay.style.display = "block";
        expenseErrorContent.textContent = "Please enter an expense name";
        return;
    }

    // check if the expense amount is empty
    if (expense_amount.value === "") {
        expenseErrorDisplay.style.display = "block";
        expenseErrorContent.textContent = "Please enter an expense amount";
        return;
    }

    // check if the expense amount is not a number
    if (isNaN(expense_amount.value)) {
        expenseErrorDisplay.style.display = "block";
        expenseErrorContent.textContent = "Please enter a valid expense amount";
        return;
    }

    // call the add_expense function in a safe try block 
    try {
        // getting data from the fetch
        response_data = await add_expense(expense_name.value, expense_amount.value);

        // print success image
        console.log(`success: ${response_data.success}, details: ${response_data.details}.`);

        // checking if the expense is empty or not 
        const emptyDiv = document.getElementById("empty-expense-div");
        if (emptyDiv && getComputedStyle(emptyDiv).display === 'flex') {
            emptyDiv.style.display = 'none';
        }

        // adding expense to the expense div ---------------------------------------------------
        // still working on this part of the frontend

        // adding the expense to the DOM
        addExpenseToDOM(expense_name.value, expense_amount.value);

        // reset the expense form
        expense_name.value = '';
        expense_amount.value = '';

        // hide the error display
        expenseErrorDisplay.style.display = "none";
        // ----------------------------------------------------------------------------------------

        // get finance object fresh from the backend 
        const finance_object = await get_finance_object();

        // change the finance div
        update_finance_div(finance_object);

    }
    catch(error) {
        // displaying the success message 
        console.log('There has been and error adding the expense');
        console.log(error);
    }
});

// fucntion to add and expense to the expnese div
function addExpenseToDOM(expenseKey, expenseAmount) {
    // Get the template div
    const template = document.getElementById("try-piece-expense");

    // Clone the template deeply (includes children)
    const clone = template.cloneNode(true);

    const cleanKey = expenseKey.trim().replace(/\s+/g, '_').replace(/[^\w\-]/g, '');

    // Update the ID (must be unique in the DOM)
    clone.id = `expense-div-${cleanKey}`;
    clone.style.display = "flex";  // make it visible

    // Update the inner text and button data
    const textDiv = clone.querySelector(".data-holder-text");
    if (textDiv) {
        textDiv.innerHTML = `
            <div id="expense-div-{{ key|replace(' ', '-')|lower }}" class="data-holder" style="padding: 5px; display: flex; flex-direction: column; border-bottom: none;">
                <div class="data-holder-text" style="margin-botton: 20px; text-align: left;">${expenseKey}: ${expenseAmount} SAR</div>
                <div class="data-holder-text"><button data-expense-name="${expenseKey}" class="maazin-button remove-expense-button">REMOVE</button></div>
            </div>
        `;
    }
    // remove justify content left
    clone.style.justifyContent = "center"
    // add event listener to the button
    add_expense_event_listener(clone.querySelector(".remove-expense-button"));

    // Append to wherever the expenses are listed
    const container = document.getElementById("expense-body"); // Make sure you have this
    container.prepend(clone);
}


// function to send expense to the backend
async function add_expense(name, amount) {
    // send POST request to the backend
    const response = await fetch('/api/update-expense', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'expense_name': name,
            'expense_amount': amount,
            'action': 'add'
        })
    });

    // checking if the error is in 200 - 299 range
    if (!response.ok) {
        // get the error object
        const errorObj = await response.json();
        // print error statement
        console.error(`ERROR: ${response.status}, ${errorObj.error}, details: ${errorObj.details}.`);
        // throw new error
        throw new Error("there was any error will adding the expense");
    }

    // sending the response object
    return await response.json();    
}

//------------------------------- Order History JS code ----------------------------------------------------------------

// get all the div elements needed 
// const error_message_div_order_history = document.getElementById("error_div_order_history");
const order_history_button = document.getElementById("search_button");
const order_history_input = document.getElementById("name_input");
const order_holder = document.getElementById("order_holder");
const order_holder_error = document.getElementById("order_holder_error");
const error_text = document.getElementById("error_text");

// adding an event listener to the button and is the main function for the async code 
order_history_button.addEventListener('click', async (event) => {
    
    // extract name from the input box
    let name = order_history_input.value;

    try {
        // check input name
        await check_name_response(name);

        // send API request to the backend and await result
        const response = await send_order_history_request(name);

        // turn off error
        order_holder.style.display = "flex";
        // sending the data to function to display the orders
        change_order_history_display(response.orders, name);
    }
    catch(error){
        // displaying the error message
        console.error(error.message)

        // clear the order holder div
        const all_orders = order_holder.querySelectorAll("#order_holder .admin-order-box");
        all_orders.forEach(order => {
            order.remove();
        });

        // turn on error
        activateErrorDisplay(order_holder_error, order_holder, error_text, error.message);
    }

    // putting the input box to empty after 
    order_history_input.value = '';

});

// function to send the API request
async function send_order_history_request(name) {
    // sending request
    const response = await fetch('/api/get-order-by-name', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'name': name
        })
    });

    // check if error code is not in 200 - 299 range
    if (!response.ok) {
        errorObj = await response.json()
        throw new Error(`${errorObj.details}`);
    }

    // send back json of the respnse
    return await response.json()
}

function change_order_history_display(data, name) {
    // clear the order holder div
    order_holder.innerHTML = '';
    // clear the error message div
    order_holder_error.style.display = "none";

    // we have to iterate over the object
    Object.entries(data).forEach(([orderId, order]) => {
        // create new div and add class
        const newElement = document.createElement('div')
        newElement.classList.add('admin-order-box')

        // getting the item quantities inner HTML and storing in a variable
        let itemQuantities = '';
        // looping over the items dicntionary and append to the string
        Object.entries(order.items).forEach(([itemId, itemDetails]) => {
            itemQuantities += `
                <li>
                    <div class="admin-order-box-content-text">
                        <span style="font-weight: bold; font-size: 1.5rem;">${itemDetails.quantity} x ${itemDetails.name}</span>
                    </div>
                </li>`;
        });        

        // add the inner HTML to the div
        newElement.innerHTML = `
            <div class="admin-order-box-heading">
                    <div class="admin-order-box-heading-text" style="margin-right: 200px">ORDER# ${orderId}</div>
                    <div class="admin-order-box-heading-text">${name}</div>
                </div>
        
                <div class="admin-order-box-content">
                    <div class="admin-order-box-content-body" style="border-right: 1px solid black;">
                        <div class="admin-order-box-content-text" style="width: 100%; text-align: center; border-bottom: 1px solid black;"><span style="font-weight: bold; font-size: 1.5rem;">Order Items:<span></div>
                            <ul>
                                ${itemQuantities}
                            </ul>
                            <div class="admin-order-box-content-text"><span style="font-weight: bold; font-size: 1.5rem;">Time: ${order.time}</span></div>
        
                            <div class="total-div">Total : ${order.value} SAR</div>
                    </div>
                    <div class="admin-order-box-content-status">
                            <div class="admin-order-box-content-body"><span style="font-weight: bold; font-size: 2.0rem; border-bottom: 2px solid black;">CURRENT STATUS:</span></div>
                            <div class="admin-order-box-content-body"><button class="maazin-button" style="width: fit-content;"><span class="status-buttons" style="font-weight: bold; font-size: 2.0rem;">${order.status}</span></button></div>
                    </div>
                </div>
            </div>
        `;

        // append the new div to the order holder
        order_holder.prepend(newElement);
    });
}

async function check_name_response(name) {
    // checking if the name block is empty
    if (name == '') {
        throw new Error("Please enter a name");
    }

    // checking if the name is not a string
    if (typeof name !== 'string') {
        throw new Error("Please enter a valid name");
    }

    // checking if the name is too long
    if (name.length > 50) {
        throw new Error("Please enter a name that is less than 50 characters");
    }

    // checking if the name is too short
    if (name.length < 2) {
        throw new Error("Please enter a name that is more than 2 characters");
    }

    // checking if the name contains special characters
    if (!/^[a-zA-Z\s]+$/.test(name)) {
        throw new Error("Please enter a name that does not contain special characters");
    }
}

function activateErrorDisplay(order_holder_error, order_holder, error_text, errorMessage) {
    order_holder_error.style.display = "flex";
    order_holder.style.display = "none";
    error_text.textContent = errorMessage;
}

// ------------------------------------------- end of JS section ------------------------------------------------




//------------------------------- Adding Item  JS code ----------------------------------------------------------------

// selecting all the HTML elements from the add item form 
const product_name_add = document.getElementById("product_name_add"); // select the name 
const product_price_add = document.getElementById("product_price_add"); // select the price
const product_description_add = document.getElementById('description'); // select the description
const product_category_add = document.getElementById('category'); // select the category
const product_image_add = document.getElementById('imageUpload'); // select the image
const add_item_button = document.getElementById('addItemButton'); // select the add item button
const production_cost_add = document.getElementById('production_cost_add'); // gettign the product cost
const product_quantity_add = document.getElementById('product_quantity_add');
const imageUploadLabel = document.getElementById('imageUploadLabel');
const display_message = document.getElementById('display_message_screen');

// selecting all the error messages
const product_name_error = document.getElementById('product_name_error');
const product_price_error = document.getElementById('product_price_error');
const product_description_error = document.getElementById('description_error');
const product_cost_error = document.getElementById('production_cost_error');
const product_quantity_error = document.getElementById('product_quantity_error');

// when the addItemButton is clicked
add_item_button.addEventListener('click', async (event) => {
    // check if the the values of the name and description is correct
    // checking the name of the product
    try{
        await check_text(product_name_add.value);
        // remove the error input style from the input
        if (product_name_add.classList.contains('input-error')) {
            product_name_add.classList.remove('input-error');
        }
        // change the inner HTML of the error text to a black space &40;
        product_name_error.innerHTML = "&nbsp;";


    } catch (error) {
        console.error(error.messsage)
        // activate the error display
        if (product_name_error.style.visibility == 'hidden') {
            // make the display visible and show the error message
            product_name_error.style.visibility = 'visible';
            // make the eror putline for the input
            product_name_add.classList.add('input-error');
        }

        // ensure the class on input error exists
        if (!product_name_add.classList.contains('input-error')) {
            product_name_add.classList.add('input-error');
        }
        product_name_error.innerHTML = error.message;
    }
    
    // checking the description of the product
    try{
        await check_text(product_description_add.value);
        // remove the error input style from the input
        if (product_description_add.classList.contains('description-error')) {
            product_description_add.classList.remove('description-error');
        }
        // change the inner HTML of the error text to a black space &40;
        product_description_error.innerHTML = "&nbsp;";

    } catch (error) {
        console.error(error.messsage)
        // activate the error display
        if (product_description_error.style.visibility == 'hidden') {
            // make the display visible and show the error message
            product_description_error.style.visibility = 'visible';
            // add error class
            product_description_add.classList.add('description-error');
        }

        // ensure the class on input error exists
        if (!product_description_add.classList.contains('description-error')) {
            product_description_add.classList.add('description-error');
        }

        product_description_error.innerHTML = error.message;
    }

    // now to check for the product price
    try {
        await check_number(product_price_add.value);
        // remove the error input style from the input
        if (product_price_add.classList.contains('input-error')) {
            product_price_add.classList.remove('input-error');
        }
        // change the inner HTML of the error text to a black space &40;
        product_price_error.innerHTML = "&nbsp;";

    } catch(error) {
        console.error(error.message);
        // activate the error display
        if (product_price_error.style.visibility == 'hidden') {
            // make the display visible and show the error message
            product_price_error.style.visibility = 'visible';
            // add error class
            product_price_add.classList.add('input-error');
        }

        // ensure the class on input error exists
        if (!product_price_add.classList.contains('input-error')) {
            product_price_add.classList.add('input-error');
        }
        product_price_error.innerHTML = error.message;
    }

    // now checking for the production cost
    try {
        await check_number(production_cost_add.value);
        // remove the error input style from the input
        if (production_cost_add.classList.contains('input-error')) {
            production_cost_add.classList.remove('input-error');
        }
        // change the inner HTML of the error text to a black space &40;
        product_cost_error.innerHTML = "&nbsp;";

    } catch(error) {
        console.error(error.message);
        // activate the error display
        if (product_cost_error.style.visibility == 'hidden') {
            // make the display visible and show the error message
            product_cost_error.style.visibility = 'visible';
            // add error class
            production_cost_add.classList.add('input-error');
        }

        // ensure the class on input error exists
        if (!production_cost_add.classList.contains('input-error')) {
            production_cost_add.classList.add('input-error');
        }
        product_cost_error.innerHTML = error.message;
    }

    // now checking for the quantity
    try {
        await check_number(product_quantity_add.value);
        if (product_quantity_add.classList.contains('input-error')) {
            product_quantity_add.classList.remove('input-error');
        }
        // change the inner HTML of the error text to a black space &40;
        product_quantity_error.innerHTML = "&nbsp;";

    } catch(error) {
        console.error(error.message);
        // activate the error display
        if (product_quantity_error.style.visibility == 'hidden') {
            // make the display visible and show the error message
            product_quantity_error.style.visibility = 'visible';
            // add error class
            product_quantity_add.classList.add('input-error');
        }
        // ensure the class on input error exists
        if (!product_quantity_add.classList.contains('input-error')) {
            product_quantity_add.classList.add('input-error');
        }
        product_quantity_error.innerHTML = error.message;
    }

    // checking the category
    try {
        // Step 1: Try validating the category (async)
        await check_category(product_category_add.value);
    
        // Step 2: If valid, hide error and remove red border
        product_category_add.classList.remove('input-error');
    
    } catch (error) {
        // Step 3: If error, show error message and highlight input
        product_category_add.classList.add('input-error');
    }

    // checking if an image is selected
    try {
        // Step 1: Try validating the category (async)
        await check_image(product_image_add.value);
    
        // Step 2: If valid, hide error and remove red border
        imageUploadLabel.classList.remove('input-error');
    
    } catch (error) {
        // Step 3: If error, show error message and highlight input
        imageUploadLabel.classList.add('input-error');
    }

    // extracting the data from the image selector
    const imageFile = product_image_add.files[0];

    // now checking if the image has a correct extension
    try {
        if (imageFile) {
            const allowedExtensions = ['jpg', 'jpeg'];
            const extension = imageFile.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(extension)) {
                throw new Error('Please select an image file.');
            }
        }
    } catch (error) {
        // Step 3: If error, show error message and highlight input
        imageUploadLabel.classList.add('input-error');
    }

    // end of validation
    // making a list of all the elements which contain the data
    const all_elements = [product_name_add, product_price_add, product_description_add, production_cost_add, product_quantity_add, product_category_add, imageUploadLabel];

    let formIsValid = true;
    for (const element of all_elements) {
        if (element.classList.contains('input-error')) {
            formIsValid = false;
            break;
        }
    }

    if (!formIsValid) {
        console.error('Form is not valid. Aborting submission.');
        display_message.style.visibility = 'visible';
        display_message.style.color = 'red';
        display_message.innerHTML = 'Form is not valid';
        return; // 🛑 STOP here if validation fails
    }

    // ✅ No errors, proceed with preparing the FormData
    const dataForm = new FormData();
    dataForm.append('name', product_name_add.value);
    dataForm.append('price', product_price_add.value);
    dataForm.append('description', product_description_add.value);
    dataForm.append('production_cost', production_cost_add.value);
    dataForm.append('quantity', product_quantity_add.value);
    dataForm.append('category', product_category_add.value);
    dataForm.append('image', imageFile);

    // now sending the data to the backend
    try {
        // send backend request
        const data = await adding_item_backend(dataForm);

        // displaying success message
        console.log(`Successful API request, details: ${data.details}`);

        // sending success message on the top screen
        // change the visibility of the message
        display_message.style.visibility = 'visible';
        display_message.style.color = 'green';
        display_message.innerHTML = 'Successfully Added';

        // resetting the form
        product_name_add.value = '';
        product_price_add.value = '';
        product_description_add.value = '';
        production_cost_add.value = '';
        product_quantity_add.value = '';
        product_category_add.value = '';
        imageUploadLabel.innerHTML = 'Select Image';

    } catch (error) {
        // displaying error message
        console.error(error.message);

        // sending error message on the top screen
        // change the visibility of the message
        display_message.style.visibility = 'visible';
        display_message.style.color = 'red';
        display_message.innerHTML = error.message;
    }

});

// function to check the image
async function check_image(value) {
    if (value === '') {
        throw new Error('Please select an image.');
    }
}
// function to check the category sectiobn
async function check_category(value) {
    if (value === '') {
        throw new Error('Please select a category.');
    }

    if (value !== 'cake' && value !== 'food') {
        throw new Error('Invalid category selected. Please choose Cake or Food.');
    }
}
// function to check all the text boxes in the form
async function check_text(value) {
    // first check if it is empty or not
    if (!value) {
        throw new Error('Enter an input'); 
    }
    // check if the input does not contain any number
    else if (!isNaN(value)) {
        throw new Error('Input should be text');
    }
    // check if contains a special characters
    else if (containsSpecialChars(value)) {
        throw new Error('input should not contain special characters');
    }
}

// function to check special characters
function containsSpecialChars(str) {
    // This regex blocks any special character except dash, comma, and period
    const specialChars = /[!@#$%^&*()?"{}|<>\\[\]=/`~';:]/;
    return specialChars.test(str);
}
// function to check if the number is a number
async function check_number(value) {
    if (!value) {
        throw new Error('Please enter a number');
    }
    else if (isNaN(value)) {
        throw new Error('Please enter a valid number');
    }
}

// function to send the data back
async function adding_item_backend(data) {
    // sending data the the backend
    const response = await fetch('/api/adding-item', {
        method: 'POST',
        body: data
    });

    // checking the error HTTP code is betwene 200 and 299
    if (!response.ok) {
        const errorObj = await response.json();
        // displaying an error mesage
        console.error(`ERROR: ${response.status}, details: ${errorObj.details}`);
        // throwing error to display on the form 
        throw new Error('Please Try Again');
    }

    // sending back successfull object
    return await response.json();
}



//------------------------------- end of JS section ----------------------------------------------------------------
