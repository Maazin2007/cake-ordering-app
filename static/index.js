// coding the JS for the Home Page

// We now have to get the weather data from openweather API

// declaring all the variables required for this weather widget
var apiKey = "ff45dafffc2a5732af33da0615015d77";
let city = "sakaka";
var url =`https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`;

// selection all the elements in the weather icon
const actual_temp_display = document.getElementById("actual_temp");
const feels_like_display = document.getElementById("feels_like");
const humidity_display = document.getElementById("humidity");
const max_temp_display = document.getElementById("max_temp");
const error_message = document.getElementById("error-message");
const weather_box = document.getElementById("weather-box");

// calling the execution function
execution();

// main function to handle eveything 
async function execution() {
    // try block to ensure that we can catch any error
    try {
        // fetching data from the API
        const data = await getWeatherData();

        // displaying the data for debugging purposes
        console.log(data);

        // now we have to change the data on the weather icon
        changeData(data);

    }
    catch(error) {
        // displaying error message
        console.error(error.message);

        // displaying error message
        weather_box.style.display = "none";
        error_message.style.display = "block";
    }
}

// function to fetch data from the API
async function getWeatherData() {
    // fetching data 
    const response = await fetch(url);

    // check if response is outside 200 - 299
    if (!response.ok) {
        // displaying error
        throw new Error('could not fetch data from the API'); 
    }

    // returing the JSON object
    return await response.json();
}

// function to change data on the weather icon
function changeData(data){
    // object destructuring to extract data from the 
    const {main: {temp: actual_temp, humidity: humidity, temp_max: max_temp, feels_like: feels_like_temp}, weather: [{description: weather_description, icon: weather_icon}]} = data;

    // changing data on the weather icon
    actual_temp_display.textContent = actual_temp.toFixed(1);
    feels_like_display.textContent = feels_like_temp.toFixed(1);
    humidity_display.textContent = humidity;
    max_temp_display.textContent = max_temp.toFixed(1);

    // getting icon url
    const icon_url = `https://openweathermap.org/img/wn/${weather_icon}@4x.png`;

    // putting error message to none
    error_message.style.display = "none";

    // showing the weather icon
    weather_box.style.display = "flex";

    // changing the icon
    document.getElementById("weather-icon").src = icon_url;
    document.getElementById("weather-icon").alt = weather_description;
    document.getElementById("weather-icon").style.height = "150px";
    document.getElementById("weather-icon").style.width = "150px";
}

