```html

<script>
    let form;
    let submitButton;
    let validator;

    form = document.querySelector('#kt_sign_in_form');
    submitButton = document.querySelector('#kt_sign_in_submit');

    // In Progress
    submitButton.setAttribute('data-kt-indicator', 'on');
    submitButton.disabled = true;

    // Success
    submitButton.removeAttribute('data-kt-indicator');
    submitButton.disabled = false;
</script>

```
