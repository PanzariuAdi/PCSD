const express = require('express');
const AWS = require('aws-sdk');
const { Pool } = require('pg');
var router = express.Router();

import {ACCESS_KEY_ID, SECRET_ACCESS_KEY, HOST, USER, PASSWORD, PORT, REGION, BUCKET } from './keys.js';

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

const SQS = new AWS.SQS({ 
    accessKeyId: ACCESS_KEY_ID,
    secretAccessKey: SECRET_ACCESS_KEY,
    region: REGION
});

const SUCCESS_MESSAGE = "THANKS FOR BUYING OUR PRODUCT !";

router.get('/', function(req, res, next) {
    res.render('index', { title: 'Express' });
});


router.get('/products', async(req, res) => {
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
})


router.post('/buy', function(req, res) {
    updateStocks(req.body.productId);
    sendSQSMessage(SUCCESS_MESSAGE);
    res.redirect('/products');
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
