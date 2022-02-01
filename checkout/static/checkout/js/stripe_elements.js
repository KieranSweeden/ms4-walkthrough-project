
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

    // Trigger overlay and fade out fom when user clicks submit
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    // Get boolean value from check box
    var saveInfo = Boolean($("#id-save-info").attr("checked"));

    // Get csrf token from the hidden input that django generates for out form
    var csrfToken = $("input[name='csrfmiddlewaretoken']").val();

    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };

    console.log(postData)

    // Create variable to store new url
    var url = '/checkout/cache_checkout_data/';

    // Using the post function within jQuery, post to the given url with the postData above
    // We'll want to wait for a response that the payment intent was updated before calling 
    // the payment confirmed method, this is easily done by adding the .done() function which
    // will execute the callback function if our view returns a status code of 200
    $.post(url, postData).done(function(){
        console.log("posting done")
        // ConfirmCardPayment sends card information
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                // Get value's from form inputs and trim to remove any white space
                card: card,
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address: {
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value)
                        // Postal code auto inputted via stripe
                    }
                }
            },
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    // Postal code needed here
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value)
                }
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
    
                // Display payment form and remove loading screen
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
    
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
    }).fail(function () {
        // just reload the page, the error will be in django messages
        location.reload();
    });
});



