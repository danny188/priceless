function getCookie(c_name) {
    if (document.cookie.length > 0) {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1)
        {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}

document.addEventListener('DOMContentLoaded', () => {
    // Functions to open and close a modal
    function openModal($el) {
      $el.classList.add('is-active');
    }

    function closeModal($el) {
      $el.classList.remove('is-active');
    }

    function closeAllModals() {
      (document.querySelectorAll('.modal') || []).forEach(($modal) => {
        closeModal($modal);
      });
    }

    // Add a click event on buttons for displaying modal to update product url
    document.querySelector('.section.products-table').addEventListener('click', (e) => {
        $trigger = e.target;

        if ($trigger.classList.contains('show-update-url-modal')) {
            const modal = $trigger.dataset.target;
            const $target = document.getElementById(modal);
            let productId = $trigger.dataset.productId;

            openModal($target);

            // for product-url-update modal, fill modal form with data from trigger button
            console.log($trigger);
            $target.querySelector('#updated_url').value = $trigger.dataset.productUrl;
            $target.querySelector('#updated_url').select();
            $target.querySelector('#product_id').value = $trigger.dataset.productId;

            document.querySelector('#modal-js-update-product-url #update-url-button').dataset.productId = productId;
        }
    });


    document.querySelector('#modal-js-update-product-url #update-url-button').addEventListener('click', (event) => {
        // ajax request to get new row data
        let productId = event.target.dataset.productId;
        fetch('/product/update-url', {
            method: 'post',
            body: new FormData(document.querySelector('#update-product-url')),
        })
        .then((response) => response.json())
        .then((data) => {
            let rowData = data['row_data'];
            productsTable.row('#row-for-product-' + productId).data(rowData);

            // update number of products on sale
            document.querySelector('#num-products-on-sale').textContent = data['num_products_on_sale'];
        });

        const modal = event.target.closest('.modal');
        closeModal(modal);
    });


    // (document.querySelectorAll('.js-modal-trigger') || []).forEach(($trigger) => {

    // });


    // Add a click event on various child elements to close the parent modal
    (document.querySelectorAll('.modal-background, .modal-close, .modal-close2, .modal-card-head .delete, .modal-card-foot .button') || []).forEach(($close) => {
      const $target = $close.closest('.modal');

      $close.addEventListener('click', () => {
        closeModal($target);
      });
    });

    // Add a keyboard event to close all modals
    document.addEventListener('keydown', (event) => {
      const e = event || window.event;

      if (e.keyCode === 27) { // Escape key
        closeAllModals();
      }
    });

    // add listener to delete notifications
    (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
        const $notification = $delete.parentNode;

        $delete.addEventListener('click', () => {
            $notification.parentNode.removeChild($notification);
        });
    });

});