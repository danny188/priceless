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
                    const duration = Date.now() - startTime;
                    window.location.reload();
                    alert("took " + (duration / 1000).toFixed(2)  + " seconds");
                }
                setTimeout(updateProgress, 500, progressUrl);

            }


            // request to start background tasks to update user's products, and get the async group result id
            fetch('/products/refreshallforuser', {method: "POST"})
                .then((response) => response.json())
                .then((data) => data['group_result_id'])
                .then((groupResultId) => {
                    let progressUrl = '/products/refreshallforuser/get_progress?' + new URLSearchParams({'group_result_id': groupResultId});

                    updateProgress(progressUrl)
                });

        });
    }

    // display spinner when update-url-button is pressed
    document.querySelector('.section.products').addEventListener('click', (e) => {
        if (e.target.classList.contains("update-url-button")) {
            e.target.classList.add("is-loading");
        }
    });
  });