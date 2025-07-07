// building the weather widget for the homepage 
// declaring all the variables required for this weather widget
var apiKey = "ff45dafffc2a5732af33da0615015d77";
let city = "sakaka";
var url =`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;

// main function to handle everything
async function execution() {
    try {
        var data = await getResponse();
    } catch(error) {
        console.log(error)
    }

    console.log(data);
}

// function to get the api responce and send the JS object back to the main function
async function getResponse() {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error("could not fetch data");
    }

    return response.json();
}
// end of weather widget for home 



