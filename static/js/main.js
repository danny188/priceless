document.addEventListener('DOMContentLoaded', () => {
    // add listener to delete notifications
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
      const $notification = $delete.parentNode;

      $delete.addEventListener('click', () => {
        $notification.parentNode.removeChild($notification);
      });
    });

    // display loading bar when refresh all products button clicked
    if (document.querySelector('#refresh-all-products')) {
        document.querySelector('#refresh-all-products').addEventListener('click', (event) => {
            let numProducts = parseInt(document.querySelector('#num-of-products').textContent, 10);
            let AVERAGE_API_RESPONSE_TIME_PER_PRODUCT = 1; // measured in seconds

            document.querySelector('#updating-products-label').classList.remove('is-hidden');
            document.querySelector('#updating-products-progress-bar').classList.remove('is-hidden');

            document.querySelector('#update-all-products-approx-time').innerHTML = Math.round(numProducts * AVERAGE_API_RESPONSE_TIME_PER_PRODUCT);
        });
    }

    // display spinner when update-url-button is pressed
    document.querySelector('.section.products').addEventListener('click', (e) => {
        if (e.target.classList.contains("update-url-button")) {
            e.target.classList.add("is-loading");
        }
    });
  });