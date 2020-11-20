const express = require('express')
var mysql = require('mysql');
var fs = require('fs');
const {URLSearchParams} = require('url')

const app = express()
const port = 80

const parent_stem = '/mnt/datay-netStorage-40G/'
const parent_obs_dir = '/mnt/datay-netStorage-40G/new_obs/'
const parent_database_dir = '/home/gurmehar/obs_database/'
//app.use(express.static('static'))
app.use(express.static('public'));

const user = process.argv[2];
const password = process.argv[3];
const host = "127.0.0.1"

console.log(user, password)

app.get('/obslist', (req, res) => {
	var files = fs.readdirSync(parent_database_dir);

        var url = req.url.split("?")[1];
        var urlParams = new URLSearchParams(url);
	var query_table = urlParams.get("table")

	var connection = mysql.createConnection({
		host     : host,
		user     : user,
		password : password,
		database : 'obs_info'
	});

	var results_return = ''

	connection.connect()

	connection.query("select obs_name, source from " + query_table, function (error, results, fields) {
  		//if (error) throw error;
		if (results == undefined){
			res.send('')
		}
		else{
			for (var i = 0; i < results.length; i++){
  				results_return += results[i].obs_name + "|" + results[i].source + ","
			}
			res.send(results_return)
		}
  	});

	//files = files.filter(file => !file.startsWith("."))
	//res.send(files.join(","));
})

app.get('/pulsarobslist', (req, res) => {
	var results_return = ''

	var connection = mysql.createConnection({
                host     : host,
                user     : user,
                password : password,
                database : 'obs_info'
        });

	connection.connect()

	connection.query("select obs_name, source from pulsar_obs_details", function(error, results, fields){
		for (var i = 0; i < results.length; i++){
			results_return += results[i].obs_name + "|" + results[i].source + ","
		}
		res.send(results_return)
	})
})

app.get('/obsspec', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var obs = urlParams.get("obs");
	var files = fs.readdirSync(parent_database_dir + obs)
	files = files.filter(file => !file.includes("."))
	res.send(files.join(","));
})

app.get('/getdirlisting', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var obs = urlParams.get("obs")
	var folder = urlParams.get("folder")	
	var files = fs.readdirSync(parent_database_dir + obs + "/" + folder)
	files = files.filter(file => !file.startsWith("."))
	files = files.filter(file => file != "data.written")
	res.send(files.join(","))
})

app.get('/fetchimage', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var path = urlParams.get("path");
	res.sendFile(parent_database_dir + path)	
})

app.get('/getcandlist', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var obs = urlParams.get("obs");
	var files = fs.readdirSync(parent_database_dir + obs + "/ics/candidates")
	files = files.filter(file => file.includes(".png"));
	res.send(files.join(","))
})

app.get('/fetchcand', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var obs = urlParams.get("obs");
	var file = urlParams.get("file")
	//res.sendFile(parent_obs_dir + obs + "/ics/candidates/" + file)
	//sharp(parent_obs_dir + obs + "/ics/candidates/" + file).resize({fit:sharp.fit.contain, width:350}).toFile('public/cache/' + file)
	res.sendFile(parent_database_dir + obs + "/ics/candidates/" + file)
})

app.get('/querybysource', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var source = urlParams.get("source")

	var connection = mysql.createConnection({
		host     : host,
		user     : user,
		password : password,
		database : 'obs_info'
	});

	var results_return = '';

	connection.connect();

	connection.query("select obs_name, source from obs_details where source like '%" + source + "%'", function (error, results, fields) {
  		//if (error) throw error;
  		for (var i = 0; i < results.length; i++){
  			results_return += results[i].obs_name + "|" + results[i].source + ","
  		}
		res.send(results_return)
  	});

	connection.end()
})

app.get('/querybydate', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var date = urlParams.get("date")
	var table = urlParams.get("table")
	if (table != "obs_details" && table != "pulsar_obs_details"){
		res.send('')
		return ;
	}
	if (date == ''){
		res.send("")
		return ''
	}
	var comparison = urlParams.get("comp")
	var connection = mysql.createConnection({host: host, user: user, password: password, database: 'obs_info'});
	var results_return = ''

	connection.connect()

	var query = 'select obs_name, source from ' + table + " where date "

	if (comparison == "on"){ query += "LIKE '%" + date + "%' "}
	else if (comparison == "after"){ query += "< '" + date + "' "}
	else if (comparison == "before"){ query += "> '" + date + "' "}
	else{ res.send(""); return ;}

	connection.query(query, function(error, results, fields){
		if (results == undefined){
			res.send('')
			return ;
		}
		for (var i = 0; i < results.length; i++){
			results_return += results[i].obs_name + "|" + results[i].source + ","
		}
		res.send(results_return)
	})
})


app.get('/fullinpquery', (req, res) => {
        var url = req.url.split("?")[1];
        var urlParams = new URLSearchParams(url);
        var date_inp = urlParams.get("date")
	var source = urlParams.get("source").replace("_", "+")
        var table = urlParams.get("table")
	var comparison = urlParams.get("comp")
	if (table != "obs_details" && table != "pulsar_obs_details"){
                res.send('')
                return ;
        }
        if (date_inp == ''){
                comparison = "on"
        }
        var connection = mysql.createConnection({host: host, user: user, password: password, database: 'obs_info'});
        var results_return = ''

        connection.connect()

        var query = 'select obs_name, source from ' + table + " where date "

        if (comparison == "on"){ query += "LIKE '%" + date_inp + "%' "}
        else if (comparison == "after"){ query += "> '" + date_inp + "' "}
        else if (comparison == "before"){ query += "< '" + date_inp + "' "}
        else{ res.send(""); return ;}

	query += "and source LIKE '%" + source + "%'"

        connection.query(query, function(error, results, fields){
                if (results == undefined){
                        res.send('')
                        return ;
                }
                for (var i = 0; i < results.length; i++){
                        results_return += results[i].obs_name + "|" + results[i].source + ","
                }
                res.send(results_return)
        })
})


app.get('/getsourcename', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var obs = urlParams.get("obs")
	var table = urlParams.get("table")
	if (obs == ''){
		res.send("")
		return ''
	}

	var connection = mysql.createConnection({
		host     : host,
		user     : user,
		password : password,
		database : 'obs_info'
	});	

	var results_return = ''

	connection.query("select source from " + table + " where obs_name = '" + obs + "'", function(error, results, fields){
		if (results == undefined){
			res.send("")
		}		
		else{
			for (var i = 0; i < results.length; i++){
				results_return += results[i].source + ","
			}
			res.send(results_return)
		}
	})
})

app.get('/arfiles', (req, res) => {
	var url = req.url.split("?")[1];
        var urlParams = new URLSearchParams(url);
        var obs = urlParams.get("obs")
	var files = fs.readdirSync(parent_database_dir + obs + "/ar_images")
	res.send(files.join(","))
})

app.get('/', (req, res) => {
	res.sendFile('public/templates/main.html', {root: __dirname})
})

app.get('/obssearch', (req, res) => {
	res.sendFile('public/templates/obssearch.html', {root: __dirname})
})

app.get('/obs', (req, res) => {
	res.sendFile('/public/templates/obs_landing.html', {root: __dirname})
})

app.get('/pulsarobs', (req, res) => {
	res.sendFile('public/templates/pulsarobs.html', {root: __dirname})
})

app.get('/viewdata', (req, res) => {
	res.sendFile('public/templates/obs_data.html', {root: __dirname})
})

app.get('/cands', (req, res) => {
	res.sendFile('public/templates/cands.html', {root: __dirname})
})

app.get('/*', (req, res) => {
	const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
	console.log(new Date(new Date().toUTCString()), ip)
        res.send('')
})

app.listen(port, '0.0.0.0')
