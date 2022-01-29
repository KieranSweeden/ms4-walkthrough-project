
// Get the inserted template variables using jquery and id
// We're also slicing off the first and last character on each
// Since they have quotation marks we don't want
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);

// Made possible by the stripe script in base.html
// All we need to set up stripe is to create a variable
// Of it using our public key
var stripe = Stripe(stripePublicKey)

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

// Create a card input using the elements instance, with the following styling
var card = elements.create('card', {style, style});

// Mount/insert the card into the div with the following id
// styled with the style above
card.mount("#card-element");

// Handle realtime validation errors on the card element
card.addEventListener("change", function(event) {
    var errorDiv = document.getElementById("card-errors");
    if (event.error) {
        var html = `
        <span class="icon" role="alert">
            <i class="fas fa-times"></i>
        </span>
        <span>${event.error.message}</span>
        `;

        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment-form');

// When form is submitted
form.addEventListener('submit', function(ev) {
    // The forms default behaviour is to post
    // We're preventing the default behaviour
    // To insert our own functionality
    ev.preventDefault();

    // Disable card & submit button to prevent multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);

    // ConfirmCardPayment sends card information
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
        }
    }).then(function(result) {

        // Execute this code with the result
        // If error
        if (result.error) {
            // Get error div and populate with message
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);

            // Re-enable card and submit button to allow user to fix issue and re-submit
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false);
        } else {
            // If succeded, we'll submit the form via javascript(jquery)
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
});



