"use strict";

/**
* Displays a short-lived notification on screen
* @param  {String} text notification message
* @param  {Number} duration number of milliseconds to show notification for
* @param  {Array} modifierClasses array of classes to add to the notification div
*/
function showTimedNotification(text, duration, modifierClasses) {
    let shortLivedNotification = document.querySelector('.short-lived-notification');

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
            // remove modifier classes
            modifierClasses.forEach((modifierClass) => shortLivedNotification.classList.remove(modifierClass));

            // to reset css animation, it is needed to remove and re-insert the notification div element
            const copyShortLivedNotification = shortLivedNotification.cloneNode(true);
            shortLivedNotification.parentNode.replaceChild(copyShortLivedNotification, shortLivedNotification);
            shortLivedNotification.remove();
        }, 3000);
    }, duration);
}

/**
 * Retrives a cookie by name
 * @param  {String} c_name key of cookie
 * @return {String}        value of cookie
 */
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

});