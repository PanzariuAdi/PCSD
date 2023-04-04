const express = require('express');
const AWS = require('aws-sdk');
const { Pool } = require('pg');
var router = express.Router();

const ACCESS_KEY_ID = "AKIAUTWQYMQQ6XQHG7XK";
const SECRET_ACCESS_KEY = "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";
const HOST = 'homework2-database.cvstx0tpswao.eu-central-1.rds.amazonaws.com';
const USER = 'postgres';
const PASSWORD = 'postgres';
const PORT = '5432'
const BUCKET = "homework2-images-bucket";
const REGION = 'eu-central-1';

const SUCCESS_MESSAGE = "THANKS FOR BUYING OUR PRODUCT !";
var chartProducts = [];

const SQS = new AWS.SQS({ 
    accessKeyId: ACCESS_KEY_ID,
    secretAccessKey: SECRET_ACCESS_KEY,
    region: REGION
});

const S3 = new AWS.S3({
    accessKeyId: ACCESS_KEY_ID,
    secretAccessKey: SECRET_ACCESS_KEY,
});

const pool = new Pool({
    host: HOST,
    user: USER,
    password: PASSWORD,
    port: PORT 
});

router.get('/', async(req, res) => {
    try {
        const productsQuery = await pool.query('SELECT * FROM products ORDER BY name');
        const products = productsQuery.rows;

        var imagePromises = products.map(product => {
            const fileName = product.name.concat(".jpg").replace(/\s+/g, '').toLowerCase();

            return S3.getObject({Bucket: BUCKET, Key: fileName}).promise()
                .then(data => {
                    if (!data.Body || data.Body.length === 0) {
                        throw new Error(`Object "${fileName}" in bucket "${BUCKET}" has no data.`);
                    }

                    const image = Buffer.from(data.Body).toString('base64');
                    return [product.name, image];
                })
                .catch(err => {
                    console.log(`Error fetching object "${fileName}" from S3: ${err.message}`);
                    return [product.name, null];
                });
        });

        const images = new Map(await Promise.all(imagePromises));

        return res.render('index', { products, images });
    } catch (err) {
        console.log(err);
        return res.sendStatus(500);
    }
});

router.post('/add', function(req, res) {
    const product = {
        id: req.body.productId,
        name: req.body.productName,
        price: req.body.productPrice,
    };
    chartProducts.push(product);
    res.redirect('/');
});

router.get('/chart', function(req, res) {
    var totalPrice = 0;
    chartProducts.forEach(element => { totalPrice += parseInt(element.price); });
    res.render('chart', { chartProducts: chartProducts, totalPrice: totalPrice});
});

router.post('/buy', function(req, res) {
    chartProducts.forEach(product => {
        updateStocks(product.id);
    })
    chartProducts = [];
    sendSQSMessage(SUCCESS_MESSAGE);
    res.redirect('/');
});

function updateStocks(productId) {
    pool.query('UPDATE products SET stocks = stocks - 1 WHERE id = $1', [productId], (err, result) => {
        if (err) {
            console.error(err);
            return false;
        }
        return true;
    });
}

function sendSQSMessage(message) {
    const params = {
        QueueUrl: "https://sqs.eu-central-1.amazonaws.com/317191644193/homework2-queue", 
        MessageBody: JSON.stringify(message),
    }

    SQS.sendMessage(params, (err, data) => {
        if (err) {
            console.log(err);
        } else {
            console.log('Message sent !')
            console.log('Message id: ', data.MessageId);
            console.log('Message : ', message)
        }
    })
}

module.exports = router;
