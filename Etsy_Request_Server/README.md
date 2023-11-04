# Request Server

This is a simple server that can be used to make requests to Etsy's API. It is intended to be used in conjunction with the [Etsy API](https://www.etsy.com/developers/documentation/getting_started/api_basics) and the [Etsy API OAuth](https://www.etsy.com/developers/documentation/getting_started/oauth) documentation.

## Usage

Laser OMS works in conjunction with a Request Server running at leboeuflasing.ddns.net. That host handles the actual communication with Etsy, and returns a safe response of data to the Laser OMS. Data is handled by this exact server, and passed onto clients via a websocket connection. Nothing is stored on the server. In the interest of being forward, the server code is available here. You may setup your own server with your own API access if you do not want to use the one provided.

Laser OMS requires the Asymmetric Encryption file. Do not delete this.

## Setup

The server will create a Server.json file in the parent of the parent directory. This will be the same location as the Laser-OMS_Data.json file. On the first run, all tables are created, and some settings need to be filled out. The biggest setting is the API Keystring which gives the server access to the Etsy API.

## Security

The server stores oauth tokens for all shops locally. However outside users cannot utilize the tokens without the shop ID and a randomly generated token. The hash of the Shop ID and token plus the Shop ID are stored. The token is not stored anywhere, and is only given to the client that makes the oauth token to keep.

The server and client talk only though an RSA public key encrypted tunnel. This may not prevent a man in the middle attack, but will stop any outside listening of the data transmitted.

## Additional Information

The request server has IP and shop ID logging. Both are keep to ensure the server is not being abused. The server also has a rate limit of 10 connections per IP per day. If you need more, consider setting up your own server.
