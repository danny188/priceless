"use strict";

let productsTable;

document.addEventListener('DOMContentLoaded', () => {
    // display loading bar when refresh all products button clicked
    if (document.querySelector('#refresh-all-products')) {
        document.querySelector('#refresh-all-products').addEventListener('click', (event) => {
            event.preventDefault();
            let total;
            let completed_count = 0;
            let progressBar = document.querySelector('#updating-products-progress-bar');
            const startTime = Date.now();

            document.querySelector('#updating-products-label').classList.remove('is-hidden');
            if (document.querySelector('#update-time-taken')) {
                document.querySelector('#update-time-taken').classList.add('is-hidden');
            }



            progressBar.classList.remove('is-hidden');

            function updateProgress(progressUrl) {
                fetch(progressUrl)
                    .then((response) => response.json())
                    .then((data) => {
                        completed_count = parseInt(data['completed_count'], 10);
                        total = parseInt(data['total'], 10);

                        document.querySelector('#num-of-products').textContent = total;
                        document.querySelector('#completed_count').textContent = completed_count;
                        progressBar.setAttribute("value", completed_count / total * 100);

                        console.log(completed_count + '/' + total + ' completed');
                    });

                if (total === completed_count) {
                    const durationMilliseconds = Date.now() - startTime;
                    const durationSeconds = (durationMilliseconds / 1000).toFixed(2);

                    window.location.href = '/products?refreshtime=' + durationSeconds;
                }
                setTimeout(updateProgress, 500, progressUrl);
            }


            // request to start background tasks to update user's products, and get the async group result id
            fetch('/products/refreshallforuser', {method: "POST", headers: {"X-CSRFToken": getCookie("csrftoken")}})
                .then((response) => response.json())
                .then((data) => data['group_result_id'])
                .then((groupResultId) => {
                    let progressUrl = '/products/refreshallforuser/get_progress?' + new URLSearchParams({'group_result_id': groupResultId});

                    updateProgress(progressUrl)
                });

        });


        // filter form reset
        document.querySelector('#filter-reset-btn').addEventListener('click', (event) => {
            const elements = document.querySelectorAll('#product-filter-form input:not(.button), #product-filter-form select');

            elements.forEach(element => {
                console.log(element.tagName);
                if (element.tagName === 'SELECT') {
                    element.querySelectorAll('option')[0].selected = 'selected';
                } else if (element.getAttribute('type') === 'checkbox') {
                    element.checked = false;
                } else {
                    element.value = "";
                }
            });
        });

        // toggle product filter form
        let productFilterToggleBtn = document.querySelector('#product-filter-toggle');
        productFilterToggleBtn.addEventListener('click', (event) => {
            document.querySelector('#product-filter-form').classList.toggle('is-hidden');

            // change arrow icon
            if (productFilterToggleBtn.querySelector('i').classList.contains('fa-angle-down')) {
                productFilterToggleBtn.querySelector('i').classList.remove('fa-angle-down');
                productFilterToggleBtn.querySelector('i').classList.add('fa-angle-up');
            } else {
                productFilterToggleBtn.querySelector('i').classList.add('fa-angle-down');
                productFilterToggleBtn.querySelector('i').classList.remove('fa-angle-up');
            }
        });

    }

    // Add a click event handlers on action buttons
    document.querySelector('.section.products-table').addEventListener('click', (e) => {
        let $trigger = e.target;

        // refreshing a single product
        if ($trigger.classList.contains('refresh-product')) {
            $trigger.classList.add("is-loading");
             // ajax request to get new row data
            let productId = e.target.dataset.productId;
            fetch(`/product/${productId}/refresh`, {
                method: 'post',
                headers: {"X-CSRFToken": getCookie("csrftoken")},
            })
            .then((response) => response.json())
            .then((data) => {
                if (data['result'] === 'success') {
                    let rowData = data['row_data'];
                    productsTable.row('#row-for-product-' + productId).data(rowData);

                    // update number of products on sale
                    document.querySelector('#num-products-on-sale').textContent = data['num_products_on_sale'];
                    showTimedNotification("Product updated", 5000, ['is-success']);
                } else {
                    // show error
                    showTimedNotification(data['error_msg'], 8000, ['is-danger']);
                    $trigger.classList.remove("is-loading");
                }
            });

        } else if ($trigger.classList.contains('show-update-url-modal')) {
            const modal = $trigger.dataset.target;
            const $target = document.getElementById(modal);
            let productId = $trigger.dataset.productId;

            openModal($target);

            // for product-url-update modal, fill modal form with data from trigger button
            $target.querySelector('#updated_url').value = $trigger.dataset.productUrl;
            $target.querySelector('#updated_url').select();
            $target.querySelector('#product_id').value = $trigger.dataset.productId;

            document.querySelector('#modal-js-update-product-url #update-url-button').dataset.productId = productId;
        } else if ($trigger.classList.contains('remove-product-button')) {
            if (confirm("Are you sure you want to remove this product?")) {
                let productId = $trigger.dataset.productId;

                let deleteProductForm = document.querySelector('#form-delete-product-' + productId);
                // send ajax request
                fetch('/product/delete', {
                    method: 'post',
                    body: new FormData(deleteProductForm),
                    headers: {"X-CSRFToken": getCookie("csrftoken")},
                })
                .then((response) => response.json())
                .then((data) => {
                    if (data['result'] === 'success') {
                        // remove product row
                        productsTable.row('#row-for-product-' + productId).remove();
                        productsTable.draw();

                        // update num of products, num of products on sale
                        document.querySelectorAll('.num-products').forEach((element) => {
                            element.textContent = data['num_products'];
                        });

                        document.querySelector('#num-products-on-sale').textContent = data['num_products_on_sale'];

                        // display feedback
                        showTimedNotification("Product successfully deleted", 5000, ['is-success']);
                    } else if (data['result'] === 'error') {
                        // display error
                        showTimedNotification("Error: " + data['error_msg'], 5000, ['is-danger']);
                    }
                });
            }
        }
    });


    // event handler for updating product url
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


    // todo: display spinner when update-url-button is pressed
    // document.querySelector('.section.products').addEventListener('click', (e) => {
    //     if (e.target.classList.contains("update-url-button")) {
    //         e.target.classList.add("is-loading");
    //     }
    // });

    productsTable = $('#products-table').DataTable({
        scrollX: false,
        responsive: true,
        autoWidth: false,
    });

});
