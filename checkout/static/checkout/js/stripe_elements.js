
// Get the inserted template variables using jquery and id
// We're also slicing off the first and last character on each
// Since they have quotation marks we don't want
var stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
var client_secret = $('#id_client_secret').text().slice(1, -1);

// Made possible by the stripe script in base.html
// All we need to set up stripe is to create a variable
// Of it using our public key
var stripe = Stripe(stripe_public_key)

// We can now use the stripe instance to create
// An instance of stripe elements
var elements = stripe.elements();

// Create a new style
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

// Create a card using the elements instance, with the following styling
var card = elements.create('card', {style, style});

// Mount/insert the card into the div with the following id
// styled with the style above
card.mount("#card-element");



