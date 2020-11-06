const express = require('express')
const sharp = require('sharp')
var fs = require('fs');

const app = express()
const port = 80

const parent_stem = '/Volumes/SETI_DATA/'
const parent_obs_dir = '/Volumes/SETI_DATA/new_obs/'

//app.use(express.static('static'))
app.use(express.static('public'));

app.get('/obslist', (req, res) => {
	var files = fs.readdirSync(parent_obs_dir);
	files = files.filter(file => !file.startsWith("."))
	res.send(files.join(","));
})

app.get('/obsspec', (req, res) => {
	var url = req.url.split("?")[1];
	var urlParams = new URLSearchParams(url);
	var obs = urlParams.get("obs");
	var files = fs.readdirSync(parent_stem + "obs_database/" + obs)
	files = files.filter(file => !file.startsWith("."))
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
	var files = fs.readdirSync(parent_obs_dir + obs + "/ics/candidates")
	files = files.filter(file => !file.startsWith("."));
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

app.get('/', (req, res) => {
	res.sendFile('public/templates/main.html', {root: __dirname})
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