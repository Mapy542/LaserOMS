# Request Server

This is a simple server that can be used to make requests to Etsy's API. It is intended to be used in conjunction with the [Etsy API](https://www.etsy.com/developers/documentation/getting_started/api_basics) and the [Etsy API OAuth](https://www.etsy.com/developers/documentation/getting_started/oauth) documentation.

## Usage

Laser OMS works in conjunction with a Request Server running at leboeuflasing.ddns.net. That host handles the actual communication with Etsy, and returns a safe response of data to the Laser OMS. Data is handled by this exact server, and passed onto clients via a websocket connection. Nothing is stored on the server. In the interest of being forward, the server code is available here. You may setup your own server with your own API access if you do not want to use the one provided.

Laser OMS requires the Asymmetric Encryption file. Do not delete this.
