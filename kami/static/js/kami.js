'use strict';

new List('table', {
    valueNames: ['title'],
    pagination: true,
    page: 15
});

[
    '#select-add',
    '#select-remove',
    '#select-edit'
].forEach(function (e) {
    var element = document.querySelector(e);

    if (element) {
        new TomSelect(e, {
            create: false,
            allowEmptyOption: true,
            sortField: {
                field: 'text',
                direction: 'asc'
            }
        });
    }
});

[
    '#anime-add',
    '#anime-edit'
].forEach(function (selector) {
    var element = document.querySelector(selector)

    if (element) {
        element.addEventListener('submit', function () {
            var url = document.querySelector('[name=url]');
            url.value = url.value.split('\n').join(',');
        }, false);
    }
});

var pageFrontend = document.querySelector('#page-frontend');

if (pageFrontend) {
    var md = window.markdownit({
        html: true,
        typographer: true
    });

    var text = pageFrontend.textContent;
    pageFrontend.innerHTML = md.render(text);
}
