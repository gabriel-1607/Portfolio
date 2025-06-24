// Global variable 'myurls' is defined in index.html
let post_id;
let paginator = {
      current_page: 1,
      max_page: 1,
      url: ''
};

document.addEventListener('DOMContentLoaded', () => {
      document.querySelector('#all_posts_button').addEventListener('click', () => {load_posts(myurls.post)});
      document.querySelectorAll('#paginator_button').forEach(button => {
            button.addEventListener('click', () => {paginator_page(button.getAttribute('data-direction'));});
      });
      load_posts(myurls.post);
});



// Gets posts from the database via a get request
async function load_posts(url, paginating=false) {

      const response = await fetch(url);
      const json_response = await response.json();

      display_posts(json_response.posts);

      if (paginating) {
            reset_paginator(json_response.max_page);
      } else {
            reset_paginator(json_response.max_page, url);
      }
}


function paginator_page(direction) {
      if (direction == "previous" && paginator.current_page > 1) {
            paginator.current_page--;
      }
      else if (direction == "next" && paginator.current_page < paginator.max_page) {
            paginator.current_page++;
      }
      load_posts(paginator.url + '?p=' + paginator.current_page, true);
}


function display_posts(posts) {

      const all_posts_container = document.querySelector('#posts_container_id');
      all_posts_container.classList.add('d-none');
      all_posts_container.innerHTML = '';

      posts.forEach(post => {
            const post_container = my_create_element(
                  'div',
                  all_posts_container,
                  null,
                  ['border', 'border-3', 'mb-1', 'p-4', 'rounded-2']
            );
            my_create_element('h5', post_container, post.user);
            let post_content = post.content.replace(/^(.+)$/gm, '<p>$1</p>');
            post_content = post_content.replace(/^\n?$/gm, '<br>');
            my_create_element('div', post_container, post_content, ['mb-3']);
            my_create_element('p', post_container, post.likes + document.querySelector('#my_svg').innerHTML);
            my_create_element('p', post_container, post.timestamp, ['fw-light']);
      });

      all_posts_container.classList.remove('d-none');

      if (document.documentElement.scrollHeight > window.innerHeight) {
            document.querySelector('#lower-page-navigation').classList.remove('d-none')
      } else {
            document.querySelector('#lower-page-navigation').classList.add('d-none')
      }
}


// Handles the creation of html elements
function my_create_element(my_tag, append_origin, content, my_classes='', my_id='') {
      const element = document.createElement(`${my_tag}`);
      if (my_classes) {
            element.classList.add(...my_classes);
      }
      if (my_id) {
            element.id = my_id;
      }
      element.innerHTML = content;
      append_origin.append(element);
      return element;
}


function reset_paginator(max_page, url="") {
      paginator.max_page = max_page;
      paginator.current_page = 1;
      if (url) {
            paginator.url = url;
      }
}