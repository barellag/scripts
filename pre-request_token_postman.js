//Setting creds
var url_appliance = 'https://44.219.132.69:11020/api/v1/token';
var username = pm.globals.get("appliance_user");
var password = pm.globals.get("appliances_pwd");


pm.sendRequest({
    url: url_appliance,
    method: 'POST',
    header: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-api-version': '1.6-rev0'
    },
    body: 'grant_type=password&username=' + username + '&password=' + password
},
function (error, response) {
    if (error) {
        console.log(error);
    } else {
        var jsonData = response.json();
        if(jsonData.access_token)
        pm.collectionVariables.set("accessToken", jsonData.access_token);
        else
        console.log("Error in getting access token");
    }
});
