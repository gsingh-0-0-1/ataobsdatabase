const express = require('express')
var mysql = require('mysql');
var fs = require('fs');

const app = express()
const port = 80

const parent_stem = ''
const parent_obs_dir = ''
const parent_database_dir = ''

const db_file = 'header_info.db'

//app.use(express.static('static'))
app.use(express.static('public'));

const user = "";
const password = "";
const host = "127.0.0.1"

app.get('/obslist', (req, res) => {
	var files = fs.readdirSync(parent_database_dir);

	var connection = mysql.createConnection({
		host     : host,
		user     : user,
		password : password,
		database : 'obs_info'
	});

	var results_return = ''

	connection.connect()

	connection.query("select obs_name from obs_details", function (error, results, fields) {
  		//if (error) throw error;
  		for (var i = 0; i < results.length; i++){
  			results_return += results[i].obs_name + ","
  		}
		res.send(results_return)
  	});

	//files = files.filter(file => !file.startsWith("."))
	//res.send(files.join(","));
})

app.get('/obsspec', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var obs = urlParams.get("obs");
	var files = fs.readdirSync(parent_stem + "obs_database/" + obs)
	files = files.filter(file => !file.includes("."))
	res.send(files.join(","));
})

app.get('/getdirlisting', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var obs = urlParams.get("obs")
	var folder = urlParams.get("folder")	
	var files = fs.readdirSync(parent_stem + "obs_database/" + obs + "/" + folder)
	files = files.filter(file => !file.startsWith("."))
	files = files.filter(file => file != "data.written")
	res.send(files.join(","))
})

app.get('/fetchimage', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var path = urlParams.get("path");
	res.sendFile(parent_stem + "obs_database/" + path)	
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
	res.sendFile(parent_stem + "obs_database/" + obs + "/ics/candidates/" + file)
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

	connection.query("select obs_name from obs_details where source like '%" + source + "%'", function (error, results, fields) {
  		//if (error) throw error;
  		for (var i = 0; i < results.length; i++){
  			results_return += results[i].obs_name + ","
  		}
		res.send(results_return)
  	});

	connection.end()
})

app.get('/querybydate', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var date = urlParams.get("date")
	if (date == ''){
		res.send("")
		return ''
	}

	//verify date format


	var comparison = urlParams.get("comp")

	var connection = mysql.createConnection({
		host     : host,
		user     : user,
		password : password,
		database : 'obs_info'
	});

	var results_return = ''

	connection.connect()

	if (comparison == "on"){
		connection.query("select obs_name from obs_details where date LIKE '%" + date + "%'", function(error, results, fields){
			//if (error) throw error;
			for (var i = 0; i < results.length; i++){
				results_return += results[i].obs_name + ","
			}
			res.send(results_return)
		})
	}
	else{
		if (comparison == "after"){
			comp_op = ">"
		}
		if (comparison == "before"){
			comp_op = "<"
		}
		connection.query("select obs_name from obs_details where date " + comp_op + " '" + date + "'", function(error, results, fields){
			//if (error) throw error;
			if (results == undefined){
				res.send("")
			}
			else{
				for (var i = 0; i < results.length; i++){
					results_return += results[i].obs_name + ","
				}
				res.send(results_return)
			}
		})
	}

	connection.end()
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

app.get('/viewdata', (req, res) => {
	res.sendFile('public/templates/obs_data.html', {root: __dirname})
})

app.get('/cands', (req, res) => {
	res.sendFile('public/templates/cands.html', {root: __dirname})
})

app.listen(port, () => {
	console.log(`Example app listening at http://localhost:${port}`);
})