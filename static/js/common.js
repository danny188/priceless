"use strict";

/**
* Displays a short-lived notification on screen
* @param  {String} text notification message
* @param  {Number} duration number of milliseconds to show notification for
* @param  {Array} modifierClasses array of classes to add to the notification div
*/
function showTimedNotification(text, duration, modifierClasses) {
    let shortLivedNotification = document.querySelector('.short-lived-notification');

    // remove all classes except those in essentialClasses
    let essentialClasses = ['notification', 'short-lived-notification', 'is-hidden'];
    shortLivedNotification.classList.forEach(cssClass => {
        if (!essentialClasses.some(c => c === cssClass)) {
            shortLivedNotification.classList.remove(cssClass);
        }
    });

    // add modifier classes
    modifierClasses.forEach((modifierClass) => shortLivedNotification.classList.add(modifierClass));

    shortLivedNotification.classList.remove('is-hidden');
    shortLivedNotification.classList.add('fade-in-notification');
    shortLivedNotification.querySelector('#notification-text').textContent = text;

    setTimeout(() => {
        shortLivedNotification.classList.add('fade-out-notification');

        // cleanup
        setTimeout(() => {
            shortLivedNotification.classList.add('is-hidden');
            shortLivedNotification.classList.remove('fade-in-notification');
            shortLivedNotification.classList.remove('fade-out-notification');

            // to reset css animation, it is needed to remove and re-insert the notification div element
            const copyShortLivedNotification = shortLivedNotification.cloneNode(true);
            if (shortLivedNotification.parentNode) {
                shortLivedNotification.parentNode.replaceChild(copyShortLivedNotification, shortLivedNotification);
            }
            shortLivedNotification.remove();
        }, 3000);
    }, duration);
}

/**
 * Retrives a cookie by name
 * @param  {String} name key of cookie
 * @return {String}      value of cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Scroll view back to top
 */
const goToTop = () => {
    document.body.scrollIntoView({behavior: "smooth",});
};

// Functions to open and close a modal
function openModal($el) {
    $el.classList.add('is-active');
}

function closeModal($el) {
    $el.classList.remove('is-active');

    // stop embedded video if this modal contains video
    let iframe = $el.querySelector('iframe');
    if (iframe) {
        iframe.setAttribute('src', iframe.getAttribute('src'));
    }
}

function closeAllModals() {
    (document.querySelectorAll('.modal') || []).forEach(($modal) => {
        closeModal($modal);
    });
}

document.addEventListener('DOMContentLoaded', () => {
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


    // (document.querySelectorAll('.js-modal-trigger') || []).forEach(($trigger) => {

    // });

    if (document.querySelector('#form-add-product #input-new-url')) {
        document.querySelector('#form-add-product #input-new-url').focus();
    }

    // Get all "navbar-burger" elements
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

    // Add a click event on each of them
    $navbarBurgers.forEach( el => {
        el.addEventListener('click', () => {

        // Get the target from the "data-target" attribute
        const target = el.dataset.target;
        const $target = document.getElementById(target);

        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        el.classList.toggle('is-active');
        $target.classList.toggle('is-active');

        });
    });

    // update copyright year to current year
    let copyrightYear = document.querySelector('#copyright-year');
    if (copyrightYear) {
        copyrightYear.innerHTML = new Date().getFullYear();
    }

    // back to top button
    let backToTopButton = document.querySelector('#back-to-top');
    if (backToTopButton) {
        backToTopButton.addEventListener('click', (event) => {
            goToTop();
        });
    }

    // demo video play button
    let demoVideoPlayButton = document.querySelector('#demo-video-play-button');
    if (demoVideoPlayButton) {
        demoVideoPlayButton.addEventListener('click', (event) => {
            document.querySelector('#demo-video-modal').classList.add('is-active');
        })
    }
});