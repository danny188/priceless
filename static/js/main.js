function getCookie(c_name) {
    if (document.cookie.length > 0)
    {
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

    // display spinner when update-url-button is pressed
    document.querySelector('.section.products').addEventListener('click', (e) => {
        if (e.target.classList.contains("update-url-button")) {
            e.target.classList.add("is-loading");
        }
    });



  });